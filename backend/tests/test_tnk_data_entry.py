from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.audit.models import AuditEvent
from apps.documents.models import EvidenceDocument
from apps.locations.models import Province, Tikina, Village
from apps.population.models import AgeGroup, PopulationMovement, PopulationSnapshot
from apps.reporting.forms import SectionStatusForm
from apps.reporting.forms import build_entry_form
from apps.reporting.form_choices import controlled_choices
from apps.reporting.models import ReportSectionStatus, ReportingPeriod, TNKReport
from apps.reporting.section_entries import entry_queryset
from apps.reporting.section_registry import SECTION_ENTRIES, get_entry_config, section_data_types
from apps.reporting.services import create_report


class TNKDataEntryWorkflowTests(TestCase):
    def setUp(self):
        self.province = Province.objects.create(code="LAU", name_en="Lau")
        self.tikina = Tikina.objects.create(province=self.province, code="LAK", name_en="Lakeba")
        self.village = Village.objects.create(tikina=self.tikina, code="TUB", name_en="Tubou")
        self.other_village = Village.objects.create(tikina=self.tikina, code="OTH", name_en="Other")
        self.user = User.objects.create_user(username="tnk", password="safe-password")
        role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        UserRoleAssignment.objects.create(user=self.user, role=role)
        UserLocationAssignment.objects.create(user=self.user, village=self.village)
        self.period = ReportingPeriod.objects.create(year=2026, quarter=2, start_date=date(2026, 4, 1), end_date=date(2026, 6, 30), submission_due_date=date(2026, 7, 15), is_open=True)
        self.report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        self.age_group = AgeGroup.objects.create(code="25_34", name_en="25-34", minimum_age=25, maximum_age=34)
        self.client.force_login(self.user)

    def test_all_substantive_sections_have_entry_workflows(self):
        self.assertEqual(len(SECTION_ENTRIES), 15)
        self.assertGreaterEqual(sum(len(entries) for entries in SECTION_ENTRIES.values()), 40)
        for section_code in SECTION_ENTRIES:
            response = self.client.get(reverse("reporting:section_update", args=(self.report.uuid, section_code)))
            self.assertEqual(response.status_code, 200, section_code)
            self.assertContains(response, "Each record saves independently")

    def test_data_type_colours_and_mixed_section_labels_render(self):
        response = self.client.get(reverse("reporting:detail", args=(self.report.uuid,)))
        self.assertContains(response, "data-type-master")
        self.assertContains(response, "data-type-operational")
        self.assertContains(response, "data-type-snapshot")
        self.assertContains(response, "data-type-workflow")
        self.assertEqual(
            {item["key"] for item in section_data_types("population_households")},
            {"master", "operational", "snapshot"},
        )
        self.assertEqual(section_data_types("validation_submission")[0]["key"], "workflow")

        section_response = self.client.get(
            reverse("reporting:section_update", args=(self.report.uuid, "population_households"))
        )
        self.assertContains(section_response, "data-entry-master")
        self.assertContains(section_response, "data-entry-operational")
        self.assertContains(section_response, "data-entry-snapshot")

    def test_every_configured_create_form_renders(self):
        for section_code, configs in SECTION_ENTRIES.items():
            for config in configs:
                if not config.allow_create:
                    continue
                with self.subTest(section=section_code, entry=config.key):
                    response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, section_code, config.key)))
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "Save record")

    def test_analysable_plain_text_fields_use_controlled_dropdowns(self):
        controlled_count = 0
        for configs in SECTION_ENTRIES.values():
            for config in configs:
                form = build_entry_form(config, report=self.report)
                for field_name, field in form.fields.items():
                    if controlled_choices(config.model, field_name):
                        controlled_count += 1
                        self.assertEqual(field.widget.input_type, "select", f"{config.key}.{field_name}")
        self.assertGreaterEqual(controlled_count, 70)

    def test_controlled_dropdown_rejects_an_unlisted_analytical_value(self):
        config = get_entry_config("population_households", "population")
        form = build_entry_form(config, report=self.report, data={
            "age_group": self.age_group.pk,
            "gender": "user typed anything",
            "resident_status": "permanent_resident",
            "count": 1,
            "measurement_date": "2026-06-30",
            "measurement_unit": "people",
            "data_source": "physical_count",
            "collection_method": "household census",
            "source_reference": "Register",
            "verification_status": "unverified",
            "confidence_level": "high",
            "notes": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)

    def test_generic_forms_do_not_expose_legacy_direct_file_fields(self):
        unsafe_fields = {"supporting_document", "evidence_document", "verification_document", "plan_document"}
        for configs in SECTION_ENTRIES.values():
            for config in configs:
                self.assertFalse(unsafe_fields.intersection(config.fields), config.key)

    def test_author_cannot_mark_a_section_verified(self):
        form = SectionStatusForm(instance=self.report.section_statuses.first(), initial={"expected_version": 1})
        values = {value for value, _label in form.fields["status"].choices}
        self.assertNotIn(ReportSectionStatus.Status.VERIFIED, values)
        self.assertNotIn("completion_percentage", form.fields)

    def test_confirmed_unchanged_automatically_completes_section(self):
        from apps.reporting.services import update_section_status

        section = self.report.section_statuses.get(section_code=ReportSectionStatus.Section.WATER)
        update_section_status(
            report=self.report,
            section_code=section.section_code,
            status=ReportSectionStatus.Status.IN_PROGRESS,
            confirmed_unchanged=True,
            user=self.user,
            expected_version=1,
        )
        section.refresh_from_db()
        self.report.refresh_from_db()
        self.assertEqual(section.status, ReportSectionStatus.Status.COMPLETE)
        self.assertEqual(section.completion_percentage, 100)
        self.assertEqual(self.report.completeness_percentage, Decimal("5.88"))

    def test_period_scoped_entry_does_not_leak_from_other_quarter(self):
        other_period = ReportingPeriod.objects.create(year=2026, quarter=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31), submission_due_date=date(2026, 4, 15), is_open=False)
        current = PopulationMovement.objects.create(village=self.village, reporting_period=self.period, movement_type="birth", movement_date=date(2026, 5, 1), count=1, data_source="physical_count")
        PopulationMovement.objects.create(village=self.village, reporting_period=other_period, movement_type="birth", movement_date=date(2026, 2, 1), count=2, data_source="physical_count")
        queryset = entry_queryset(get_entry_config("population_households", "movement"), self.report)
        self.assertEqual(list(queryset), [current])

    def test_population_entry_binds_report_and_village_server_side(self):
        response = self.client.post(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")), {
            "age_group": self.age_group.pk, "gender": "female", "resident_status": "permanent_resident", "count": 15,
            "measurement_date": "2026-06-30", "measurement_unit": "people", "data_source": "physical_count",
            "collection_method": "household census", "source_reference": "Register 2026 Q2", "verification_status": "unverified",
            "confidence_level": "high", "notes": "",
        })
        self.assertRedirects(response, reverse("reporting:section_update", args=(self.report.uuid, "population_households")))
        snapshot = PopulationSnapshot.objects.get()
        self.assertEqual(snapshot.report, self.report)
        self.assertEqual(snapshot.village, self.village)
        section = self.report.section_statuses.get(section_code="population_households")
        self.assertEqual(section.status, ReportSectionStatus.Status.IN_PROGRESS)
        self.assertEqual(section.last_updated_by, self.user)
        self.assertTrue(AuditEvent.objects.filter(action="report.entry_saved", object_uuid=snapshot.uuid).exists())
        self.report.refresh_from_db()
        self.assertGreater(self.report.completeness_percentage, 0)

    def test_itaukei_language_translates_dynamic_data_entry_form(self):
        self.client.post(reverse("set_language"), {"language": "fj", "next": "/"})
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iwiliwili ni lewenivanua")
        self.assertContains(response, "Tagane se yalewa")
        self.assertContains(response, "Dau tiko tudei")
        self.assertContains(response, "Maroroya na itukutuku")

    def test_master_person_entry_is_bound_to_assigned_village(self):
        response = self.client.post(reverse("reporting:entry_create", args=(self.report.uuid, "leadership_governance", "person")), {
            "full_name": "Fictional Official", "gender": "male", "date_of_birth": "1980-01-01", "phone": "", "email": "",
            "confidentiality_level": "confidential", "is_active": "on",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.village.people.get().full_name, "Fictional Official")
        self.assertFalse(self.other_village.people.exists())

    def test_user_without_author_role_cannot_open_entry_form(self):
        reviewer = User.objects.create_user(username="reviewer")
        reviewer_role = Role.objects.create(code=Role.Codes.MATA_NI_TIKINA, name="Mata ni Tikina")
        UserRoleAssignment.objects.create(user=reviewer, role=reviewer_role)
        UserLocationAssignment.objects.create(user=reviewer, tikina=self.tikina)
        self.client.force_login(reviewer)
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_sign_the_village_final_declaration(self):
        reviewer = User.objects.create_user(username="declaration-reviewer")
        reviewer_role = Role.objects.create(code=Role.Codes.MATA_NI_TIKINA, name="Mata ni Tikina")
        UserRoleAssignment.objects.create(user=reviewer, role=reviewer_role)
        UserLocationAssignment.objects.create(user=reviewer, tikina=self.tikina)
        self.client.force_login(reviewer)
        response = self.client.post(reverse("reporting:declare", args=(self.report.uuid,)), {"acknowledged": "on"})
        self.assertEqual(response.status_code, 403)

    def test_submitted_report_rejects_entry_changes(self):
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self.report.refresh_from_db()
        response = self.client.get(reverse("reporting:entry_create", args=(self.report.uuid, "population_households", "population")))
        self.assertEqual(response.status_code, 403)

    @override_settings(MEDIA_ROOT=settings.BASE_DIR / "test_media")
    def test_evidence_upload_is_linked_to_report(self):
        response = self.client.post(reverse("reporting:evidence_upload", args=(self.report.uuid,)), {
            "title": "Population register", "document_type": "register", "description": "Fictional test evidence",
            "confidentiality_level": "restricted", "file": SimpleUploadedFile("register.pdf", b"%PDF-1.4 fictional", content_type="application/pdf"),
        })
        self.assertEqual(response.status_code, 302)
        document = EvidenceDocument.objects.get()
        self.assertEqual(document.links.get().content_object, self.report)
        self.assertEqual(len(document.checksum), 64)

    def _photo_target(self, village=None):
        from apps.infrastructure.models import VillageAsset
        return VillageAsset.objects.create(village=village or self.village, asset_code="PHOTO", asset_name="Village hall", quantity=1)

    def _photo_url(self, record, section="housing_assets", key="asset", report=None):
        return reverse("reporting:record_photos", args=((report or self.report).uuid, section, key, record.uuid))

    def _photo_data(self, count=1):
        from io import BytesIO
        from PIL import Image
        content = BytesIO()
        Image.new("RGB", (24, 18), "green").save(content, format="PNG")
        data = {"form-TOTAL_FORMS": str(count), "form-INITIAL_FORMS": "0"}
        for index in range(count):
            data.update({
                f"form-{index}-image": SimpleUploadedFile(f"garden-{index}.png", content.getvalue(), content_type="image/png"),
                f"form-{index}-caption": f"Garden photo {index}",
                f"form-{index}-captured_at": "2026-05-01T10:30",
                f"form-{index}-stage": "before" if index == 0 else "after",
                f"form-{index}-confidentiality_level": "restricted",
            })
        return data

    def _temporary_photo_storage(self):
        import tempfile
        directory = tempfile.TemporaryDirectory(dir=settings.BASE_DIR / "tmp")
        self.addCleanup(directory.cleanup)
        override = override_settings(MEDIA_ROOT=directory.name)
        override.enable()
        self.addCleanup(override.disable)
        return directory.name

    def test_record_photos_upload_multiple_metadata_and_protected_gallery(self):
        from apps.documents.models import RecordPhoto
        self._temporary_photo_storage()
        asset = self._photo_target()
        data = self._photo_data(2)
        data.update({"form-0-latitude": "-18.123456", "form-0-longitude": "178.123456", "form-0-location_accuracy_metres": "8.50"})
        section = self.report.section_statuses.get(section_code="housing_assets")
        old_status = section.status
        response = self.client.post(self._photo_url(asset), data)
        self.assertEqual(response.status_code, 302)
        photos = list(RecordPhoto.objects.order_by("pk"))
        self.assertEqual(len(photos), 2)
        self.assertEqual(photos[0].record_identifier, str(asset.uuid))
        self.assertEqual(photos[0].stage, "before")
        self.assertEqual(photos[1].stage, "after")
        self.assertEqual(photos[0].document.latitude, Decimal("-18.123456"))
        self.assertIsNone(photos[1].document.latitude)
        self.assertEqual(photos[0].document.captured_at.hour, 22)  # Fiji 10:30 is previous-day UTC 22:30.
        self.assertEqual(photos[0].document.links.get().content_object, self.report)
        section.refresh_from_db()
        self.assertEqual(section.status, old_status)
        gallery = self.client.get(self._photo_url(asset))
        self.assertIn("geolocation=(self)", gallery["Permissions-Policy"])
        self.assertContains(gallery, "Garden photo 0")
        self.assertContains(gallery, "Garden photo 1")
        preview = self.client.get(reverse("documents:photo_preview", args=(photos[0].document.uuid,)))
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview["Content-Type"], "image/jpeg")
        self.assertEqual(preview["Cache-Control"], "private, no-store")
        self.assertTrue(AuditEvent.objects.filter(action="document.uploaded", object_uuid=photos[0].document.uuid).exists())

    def test_all_five_priority_areas_expose_photos_and_accept_uploads(self):
        from apps.economy.models import CropProductionSnapshot, CropType
        from apps.infrastructure.models import VillageWaterSource
        from apps.projects.models import IVDPProject
        from apps.resilience.models import ClimateImpactObservation
        self._temporary_photo_storage()
        crop_type = CropType.objects.create(code="taro", name_en="Taro")
        targets = [
            ("housing_assets", "asset", self._photo_target()),
            ("agriculture_food", "crop", CropProductionSnapshot.objects.create(report=self.report, crop_type=crop_type, measurement_date=date(2026, 5, 1))),
            ("water", "source", VillageWaterSource.objects.create(village=self.village, source_name="Tank")),
            ("ivdp_projects", "project", IVDPProject.objects.create(village=self.village, project_code="P1", project_name="Hall")),
            ("climate_disaster", "climate", ClimateImpactObservation.objects.create(village=self.village, report=self.report, observation_date=date(2026, 5, 1))),
        ]
        for section, key, record in targets:
            with self.subTest(section=section):
                url = self._photo_url(record, section, key)
                self.assertContains(self.client.get(reverse("reporting:section_update", args=(self.report.uuid, section))), url)
                self.assertContains(self.client.get(url), "Add photo evidence")
                self.assertEqual(self.client.post(url, self._photo_data()).status_code, 302)
        self.assertEqual(self.report.record_photos.count(), 5)

    def test_photo_batch_validation_is_all_or_nothing(self):
        self._temporary_photo_storage()
        asset = self._photo_target()
        data = self._photo_data(2)
        data["form-1-image"] = SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")
        response = self.client.post(self._photo_url(asset), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(EvidenceDocument.objects.exists())
        for changes in ({"form-0-latitude": "-18"}, {"form-0-stage": "verified"}, {"form-0-captured_at": "2999-01-01T10:00"}, {"form-0-caption": ""}):
            data = self._photo_data()
            data.update(changes)
            self.assertEqual(self.client.post(self._photo_url(asset), data).status_code, 200)
            self.assertFalse(EvidenceDocument.objects.exists())
        self.assertEqual(self.client.post(self._photo_url(asset), self._photo_data(11)).status_code, 200)
        self.assertFalse(EvidenceDocument.objects.exists())
        with override_settings(TNK_MAX_UPLOAD_BYTES=10):
            self.assertEqual(self.client.post(self._photo_url(asset), self._photo_data()).status_code, 200)
            self.assertFalse(EvidenceDocument.objects.exists())

    def test_photo_targets_are_scoped_to_report_record_and_enabled_section(self):
        other = self._photo_target(self.other_village)
        self.assertEqual(self.client.get(self._photo_url(other)).status_code, 404)
        self.assertEqual(self.client.post(self._photo_url(other), self._photo_data()).status_code, 404)
        self.assertEqual(self.client.get(self._photo_url(other, "health", "condition")).status_code, 404)
        self.assertEqual(self.client.get(reverse("reporting:record_photos", args=(self.report.uuid, "water", "source", "bad-id"))).status_code, 404)

    def test_photo_readonly_and_cross_village_download_permissions(self):
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        document = EvidenceDocument.objects.get()
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        gallery = self.client.get(self._photo_url(asset))
        self.assertContains(gallery, "Garden photo 0")
        self.assertNotContains(gallery, "Save photos securely")
        self.assertEqual(self.client.post(self._photo_url(asset), self._photo_data()).status_code, 403)
        outsider = User.objects.create_user(username="photo-outsider")
        UserRoleAssignment.objects.create(user=outsider, role=Role.objects.get(code=Role.Codes.TURAGA_NI_KORO))
        UserLocationAssignment.objects.create(user=outsider, village=self.other_village)
        self.client.force_login(outsider)
        self.assertEqual(self.client.get(self._photo_url(asset)).status_code, 404)
        for route in ("documents:photo_preview", "documents:download"):
            self.assertEqual(self.client.get(reverse(route, args=(document.uuid,))).status_code, 403)

    def test_photo_gallery_does_not_include_another_record_or_quarter(self):
        from apps.infrastructure.models import VillageAsset
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        other = VillageAsset.objects.create(village=self.village, asset_code="OTHER", quantity=1)
        self.assertNotContains(self.client.get(self._photo_url(other)), "Garden photo 0")
        period = ReportingPeriod.objects.create(year=2026, quarter=3, start_date=date(2026, 7, 1), end_date=date(2026, 9, 30), submission_due_date=date(2026, 10, 15), is_open=True)
        report = create_report(village=self.village, reporting_period=period, prepared_by=self.user)
        self.assertNotContains(self.client.get(self._photo_url(asset, report=report)), "Garden photo 0")

    def test_failed_photo_transaction_cleans_up_new_files(self):
        from pathlib import Path
        from unittest.mock import patch
        directory = self._temporary_photo_storage()
        asset = self._photo_target()
        with patch("apps.documents.photos.record_event", side_effect=RuntimeError("audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post(self._photo_url(asset), self._photo_data())
        self.assertFalse(EvidenceDocument.objects.exists())
        self.assertEqual([path for path in Path(directory).rglob("*") if path.is_file()], [])

    def test_record_photo_permissions_do_not_bypass_draft_or_section_rules(self):
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        document = EvidenceDocument.objects.get()
        reviewer = User.objects.create_user(username="photo-reviewer")
        role = Role.objects.create(code=Role.Codes.MATA_NI_TIKINA, name="Reviewer")
        UserRoleAssignment.objects.create(user=reviewer, role=role)
        UserLocationAssignment.objects.create(user=reviewer, tikina=self.tikina)
        self.client.force_login(reviewer)
        self.assertNotContains(self.client.get(self._photo_url(asset)), "Garden photo 0")
        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(document.uuid,))).status_code, 403)
        self.assertEqual(self.client.post(self._photo_url(asset), self._photo_data()).status_code, 403)
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self.assertContains(self.client.get(self._photo_url(asset)), "Garden photo 0")

        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(document.uuid,))).status_code, 200)
        nurse = User.objects.create_user(username="photo-nurse")
        role = Role.objects.create(code=Role.Codes.VILLAGE_NURSE, name="Nurse")
        UserRoleAssignment.objects.create(user=nurse, role=role)
        UserLocationAssignment.objects.create(user=nurse, village=self.village)
        self.client.force_login(nurse)
        self.assertEqual(self.client.get(self._photo_url(asset)).status_code, 403)
        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(document.uuid,))).status_code, 403)

    def _photo_report_reviewer(self, role_code=Role.Codes.ROKO_VEIVUKE, village=None):
        user = User.objects.create_user(username=f"photos-{role_code}")
        role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": role_code})
        UserRoleAssignment.objects.create(user=user, role=role)
        UserLocationAssignment.objects.create(user=user, village=village or self.village)
        self.client.force_login(user)
        return user

    def test_photo_reports_menu_and_routes_are_senior_only(self):
        list_url = reverse("reporting:photo_report_list")
        detail_url = reverse("reporting:photo_report_detail", args=(self.report.uuid,))
        for role in (Role.Codes.ROKO_VEIVUKE, Role.Codes.ROKO_TUI, Role.Codes.PROVINCIAL_ADMIN, Role.Codes.SYSTEM_ADMIN):
            with self.subTest(role=role):
                self._photo_report_reviewer(role)
                self.assertContains(self.client.get(reverse("core:dashboard")), "Open Photo Reports")
                self.assertEqual(self.client.get(list_url).status_code, 200)
                self.assertEqual(self.client.get(detail_url).status_code, 200)
                self.assertEqual(self.client.post(detail_url, {}).status_code, 405)
        for role in (Role.Codes.TURAGA_NI_KORO, Role.Codes.MATA_NI_TIKINA, Role.Codes.VILLAGE_NURSE, Role.Codes.AUDITOR, Role.Codes.READ_ONLY_ANALYST):
            with self.subTest(role=role):
                self._photo_report_reviewer(role)
                self.assertNotContains(self.client.get(reverse("core:dashboard")), "Open Photo Reports")
                self.assertEqual(self.client.get(list_url).status_code, 403)
                self.assertEqual(self.client.get(detail_url).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(list_url).status_code, 302)

    def test_photo_report_filters_are_location_scoped_and_fail_closed(self):
        UserLocationAssignment.objects.create(user=self.user, village=self.other_village)
        other_report = create_report(village=self.other_village, reporting_period=self.period, prepared_by=self.user)
        reviewer = self._photo_report_reviewer()
        url = reverse("reporting:photo_report_list")
        response = self.client.get(url, {"province": self.province.pk, "tikina": self.tikina.pk, "village": self.village.pk, "year": 2026, "quarter": 2})
        self.assertEqual([item.pk for item in response.context["page_obj"]], [self.report.pk])
        self.assertNotContains(response, str(other_report.uuid))
        self.assertEqual(self.client.get(reverse("reporting:photo_report_detail", args=(other_report.uuid,))).status_code, 404)
        for parameters in ({"village": self.other_village.pk}, {"year": "invalid"}, {"quarter": "9"}, {"province": "bad"}):
            response = self.client.get(url, parameters)
            self.assertFalse(response.context["filters"].is_valid())
            self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.assertEqual(self.client.get(url, {"quarter": 1}).context["page_obj"].paginator.count, 0)
        reviewer.role_assignments.update(is_active=False)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_photo_report_gallery_includes_record_and_general_images_not_documents(self):
        from apps.documents.models import RecordPhoto
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data(2))
        # Existing report-level uploads have no record/stage/capture metadata.
        self.client.post(reverse("reporting:evidence_upload", args=(self.report.uuid,)), {
            "title": "General village photo", "document_type": "photograph", "confidentiality_level": "restricted", "file": self._photo_data()["form-0-image"],
        })
        self.client.post(reverse("reporting:evidence_upload", args=(self.report.uuid,)), {
            "title": "Private PDF register", "document_type": "register", "confidentiality_level": "restricted", "file": SimpleUploadedFile("register.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
        })
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self._photo_report_reviewer()
        url = reverse("reporting:photo_report_detail", args=(self.report.uuid,))
        response = self.client.get(url)
        self.assertEqual(response.context["total_photos"], 3)
        self.assertContains(response, "General village photo")
        self.assertNotContains(response, "Private PDF register")
        self.assertContains(response, f"#record-asset-{asset.uuid}")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertNotContains(response, "Save photos securely")
        rows = response.context["page_obj"].object_list
        self.assertEqual([row["stage"] for row in rows], ["before", "after", "unspecified"])
        general = EvidenceDocument.objects.get(title="General village photo")
        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(general.uuid,))).status_code, 200)
        pdf = EvidenceDocument.objects.get(title="Private PDF register")
        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(pdf.uuid,))).status_code, 404)
        filtered = self.client.get(url, {"area": "housing_assets", "stage": "after"})
        self.assertEqual(filtered.context["filtered_photos"], 1)
        self.assertContains(filtered, "Garden photo 1")
        self.assertNotContains(filtered, "Garden photo 0")
        self.assertEqual(self.client.get(url, {"area": "general"}).context["filtered_photos"], 1)
        self.assertEqual(self.client.get(url, {"stage": "invalid"}).context["filtered_photos"], 0)
        self.assertEqual(self.client.get(url, {"area": "water"}).context["filtered_photos"], 0)
        self.assertEqual(RecordPhoto.objects.count(), 2)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, TNKReport.Status.SUBMITTED)

    def test_photo_report_draft_counts_and_previews_do_not_leak(self):
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        document = EvidenceDocument.objects.get()
        self._photo_report_reviewer()
        url = reverse("reporting:photo_report_detail", args=(self.report.uuid,))
        response = self.client.get(url)
        self.assertEqual(response.context["total_photos"], 0)
        self.assertNotContains(response, "Garden photo 0")
        self.assertNotContains(response, str(document.uuid))
        self.assertContains(response, "No photos available")
        self.assertEqual(self.client.get(reverse("documents:photo_preview", args=(document.uuid,))).status_code, 403)
        self._photo_report_reviewer(Role.Codes.PROVINCIAL_ADMIN)
        self.assertEqual(self.client.get(url).context["total_photos"], 1)

    def test_photo_report_gallery_excludes_documents_without_clearance(self):
        from unittest.mock import patch
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        EvidenceDocument.objects.update(confidentiality_level="highly_restricted")
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self._photo_report_reviewer()
        with patch("apps.core.security.confidentiality._clearance", return_value=2):
            response = self.client.get(reverse("reporting:photo_report_detail", args=(self.report.uuid,)))
            self.assertEqual(response.context["total_photos"], 0)
            self.assertNotContains(response, "Garden photo 0")

    def test_photo_report_gallery_pagination_keeps_filters(self):
        from apps.documents.models import RecordPhoto, EvidenceLink
        from django.contrib.contenttypes.models import ContentType
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        first = EvidenceDocument.objects.get()
        for index in range(24):
            document = EvidenceDocument.objects.create(title=f"Extra photo {index}", document_type="photograph", file=first.file.name, uploaded_by=self.user, mime_type="image/png")
            document.file.close()
            EvidenceLink.objects.create(document=document, content_type=ContentType.objects.get_for_model(self.report), object_id=self.report.pk)
            RecordPhoto.objects.create(document=document, report=self.report, section_code="housing_assets", entry_key="asset", record_identifier=str(asset.uuid), stage="before")
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        self._photo_report_reviewer()
        response = self.client.get(reverse("reporting:photo_report_detail", args=(self.report.uuid,)), {"area": "housing_assets", "stage": "before", "page": 2})
        self.assertEqual(response.context["total_photos"], 25)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertContains(response, "area=housing_assets&amp;stage=before&amp;page=1")

    def test_record_photos_remain_accessible_from_frozen_master_snapshot(self):
        from apps.reporting.history import capture_master_snapshots
        from apps.infrastructure.models import VillageAsset
        self._temporary_photo_storage()
        asset = self._photo_target()
        self.client.post(self._photo_url(asset), self._photo_data())
        capture_master_snapshots(self.report)
        self.report.save(update_fields=("master_snapshot_captured_at",))
        TNKReport.objects.filter(pk=self.report.pk).update(status=TNKReport.Status.SUBMITTED)
        # A later master change must not hide the official report's photos.
        VillageAsset.objects.filter(pk=asset.pk).update(acquisition_date=date(2026, 8, 1))
        self.assertContains(self.client.get(self._photo_url(asset)), "Garden photo 0")
