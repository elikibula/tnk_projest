import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.generators import SchemaGenerator

from apps.accounts.models import Role, User, UserLocationAssignment, UserRoleAssignment
from apps.locations.models import Province, Tikina, Village
from apps.mobile_api.models import MobileDevice
from apps.documents.models import EvidenceDocument
from apps.analytics.models import IndicatorDefinition, IndicatorValue
from apps.population.models import AgeGroup, PopulationSnapshot
from apps.reporting.models import ReportingPeriod, ReportSectionStatus, TNKReport
from apps.reporting.services import create_report
from apps.workflow.models import ApprovalAction


class MobileApiTests(APITestCase):
    password = "Strong-test-password-938!"

    @classmethod
    def setUpTestData(cls):
        cls.province = Province.objects.create(code="TEST", name_en="Test Province")
        cls.tikina = Tikina.objects.create(province=cls.province, code="A", name_en="Tikina A")
        cls.village = Village.objects.create(tikina=cls.tikina, code="A1", name_en="Village A1")
        cls.other_village = Village.objects.create(tikina=cls.tikina, code="A2", name_en="Village A2")
        cls.role = Role.objects.create(code=Role.Codes.TURAGA_NI_KORO, name="Turaga ni Koro")
        cls.user = User.objects.create_user(username="tnk-a1", password=cls.password, first_name="TNK", last_name="A1")
        UserRoleAssignment.objects.create(user=cls.user, role=cls.role)
        UserLocationAssignment.objects.create(user=cls.user, village=cls.village)
        cls.period = ReportingPeriod.objects.create(
            year=2026,
            quarter=2,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 6, 30),
            submission_due_date=date(2026, 7, 15),
            is_open=True,
        )
        cls.other_user = User.objects.create_user(username="tnk-a2", password=cls.password)
        UserRoleAssignment.objects.create(user=cls.other_user, role=cls.role)
        UserLocationAssignment.objects.create(user=cls.other_user, village=cls.other_village)

    def setUp(self):
        cache.clear()

    def login(self, *, identifier=None):
        response = self.client.post(
            reverse("mobile_api:login"),
            {
                "username": self.user.username,
                "password": self.password,
                "device_identifier": identifier or uuid.uuid4(),
                "platform": "android",
                "app_version": "1.0.0",
                "device_name": "Test Phone",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response

    def test_inactive_location_choices_excluded_but_report_history_kept(self):
        self.login()
        Village.objects.filter(pk=self.village.pk).update(is_active=False)
        response = self.client.get(reverse("mobile_api:villages"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        bootstrap = self.client.get(reverse("mobile_api:bootstrap"))
        self.assertEqual(bootstrap.data["villages"], [])
        Village.objects.filter(pk=self.village.pk).update(is_active=True)
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        Tikina.objects.filter(pk=self.tikina.pk).update(is_active=False)
        self.assertEqual(len(self.client.get(reverse("mobile_api:villages")).data), 0)
        bootstrap = self.client.get(reverse("mobile_api:bootstrap"))
        self.assertEqual([item["name_en"] for item in bootstrap.data["villages"]], ["Village A1"])
        self.assertIn(str(report.uuid), [str(item["uuid"]) for item in bootstrap.data["reports"]])

    def test_login_registers_device_and_tokens_are_device_bound(self):
        identifier = uuid.uuid4()
        response = self.login(identifier=identifier)

        device = MobileDevice.objects.get(user=self.user, device_identifier=identifier)
        self.assertEqual(str(RefreshToken(response.data["refresh"])["device_uuid"]), str(device.uuid))
        me = self.client.get(reverse("mobile_api:me"))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["roles"], [Role.Codes.TURAGA_NI_KORO])
        self.assertEqual(me.data["location_assignments"][0]["name_en"], "Village A1")
        self.assertFalse(response.data["version_policy"]["force_upgrade"])
        self.assertEqual(
            set(response.data),
            {"access", "refresh", "device_uuid", "version_policy"},
        )

    def test_login_accepts_flutter_semantic_version_with_build_number(self):
        response = self.client.post(
            reverse("mobile_api:login"),
            {
                "username": self.user.username,
                "password": self.password,
                "device_identifier": uuid.uuid4(),
                "platform": "android",
                "app_version": "1.0.0+1",
                "device_name": "android",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)

    def test_login_requires_username_and_password(self):
        base = {
            "username": self.user.username,
            "password": self.password,
            "device_identifier": uuid.uuid4(),
            "platform": "android",
            "app_version": "1.0.0+1",
        }
        for field in ("username", "password"):
            with self.subTest(field=field):
                payload = {key: value for key, value in base.items() if key != field}
                response = self.client.post(reverse("mobile_api:login"), payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_login_rejects_invalid_credentials_and_inactive_user(self):
        payload = {
            "username": self.user.username,
            "password": "incorrect-password",
            "device_identifier": uuid.uuid4(),
            "platform": "android",
            "app_version": "1.0.0+1",
        }
        invalid = self.client.post(reverse("mobile_api:login"), payload, format="json")
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("credentials", invalid.data)

        self.user.is_active = False
        self.user.save(update_fields=("is_active",))
        payload["password"] = self.password
        inactive = self.client.post(reverse("mobile_api:login"), payload, format="json")
        self.assertEqual(inactive.status_code, 400)
        self.assertIn("credentials", inactive.data)

    def test_login_rejects_malformed_json(self):
        response = self.client.generic(
            "POST",
            reverse("mobile_api:login"),
            data=b"{",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "parse_error")

    def test_login_requires_valid_device_fields(self):
        base = {
            "username": self.user.username,
            "password": self.password,
            "device_identifier": str(uuid.uuid4()),
            "platform": "android",
            "app_version": "1.0.0+1",
        }
        for field in ("device_identifier", "platform", "app_version"):
            with self.subTest(field=field):
                payload = {key: value for key, value in base.items() if key != field}
                response = self.client.post(reverse("mobile_api:login"), payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

        payload = {**base, "device_identifier": "not-a-uuid"}
        response = self.client.post(reverse("mobile_api:login"), payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("device_identifier", response.data)

    def test_login_rejects_invalid_app_version(self):
        response = self.client.post(
            reverse("mobile_api:login"),
            {
                "username": self.user.username,
                "password": self.password,
                "device_identifier": uuid.uuid4(),
                "platform": "android",
                "app_version": "latest",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("app_version", response.data)

    @override_settings(DEBUG=True)
    def test_login_development_diagnostics_are_safe(self):
        secret = "must-never-appear-in-logs"
        with self.assertLogs("tnk.mobile_api", level="WARNING") as captured:
            response = self.client.post(
                reverse("mobile_api:login"),
                {
                    "username": self.user.username,
                    "password": secret,
                    "device_identifier": uuid.uuid4(),
                    "platform": "android",
                    "app_version": "1.0.0-development+1",
                },
                format="json",
            )

        output = "\n".join(captured.output)
        self.assertEqual(response.status_code, 400)
        self.assertIn("app_version", output)
        self.assertIn("validation_messages", output)
        self.assertNotIn(secret, output)

    def test_login_openapi_contract_matches_request_and_response(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)
        operation = schema["paths"]["/api/v1/auth/login/"]["post"]
        request_ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        response_ref = operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        request_schema = schema["components"]["schemas"][request_ref.rsplit("/", 1)[-1]]
        response_schema = schema["components"]["schemas"][response_ref.rsplit("/", 1)[-1]]

        self.assertEqual(
            set(request_schema["required"]),
            {"username", "password", "device_identifier", "platform", "app_version"},
        )
        self.assertEqual(
            set(response_schema["required"]),
            {"access", "refresh", "device_uuid", "version_policy"},
        )
        self.assertIn("400", operation["responses"])

    @override_settings(MOBILE_MINIMUM_SUPPORTED_VERSION="2.0.0", MOBILE_LATEST_VERSION="2.1.0")
    def test_bootstrap_returns_force_upgrade_policy(self):
        self.login()
        response = self.client.get(reverse("mobile_api:bootstrap"))
        self.assertTrue(response.data["device"]["version_policy"]["force_upgrade"])

    def test_authentication_updates_device_last_seen(self):
        login = self.login()
        before = timezone.now()
        self.client.get(reverse("mobile_api:me"))
        device = MobileDevice.objects.get(uuid=login.data["device_uuid"])
        self.assertGreaterEqual(device.last_seen_at, before)

    def test_login_is_throttled(self):
        payload = {
            "username": self.user.username,
            "password": "wrong-password",
            "device_identifier": uuid.uuid4(),
            "platform": "android",
            "app_version": "1.0.0",
        }
        responses = [self.client.post(reverse("mobile_api:login"), payload, format="json") for _ in range(6)]
        self.assertEqual(responses[-1].status_code, 429)

    def test_revoked_device_cannot_use_access_or_refresh_token(self):
        login = self.login()
        MobileDevice.objects.filter(uuid=login.data["device_uuid"]).update(is_active=False)

        self.assertEqual(self.client.get(reverse("mobile_api:me")).status_code, 401)
        self.client.credentials()
        refresh = self.client.post(reverse("mobile_api:refresh"), {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(refresh.status_code, 400)

    def test_logout_blacklists_refresh_token(self):
        login = self.login()
        response = self.client.post(reverse("mobile_api:logout"), {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(response.status_code, 204)
        self.client.credentials()
        self.assertEqual(self.client.post(reverse("mobile_api:refresh"), {"refresh": login.data["refresh"]}, format="json").status_code, 401)

    def test_bootstrap_is_location_and_section_scoped(self):
        self.login()
        response = self.client.get(reverse("mobile_api:bootstrap"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["name_en"] for item in response.data["villages"]], ["Village A1"])
        self.assertNotIn("Village A2", str(response.data))
        self.assertEqual(len(response.data["section_definitions"]), 17)
        self.assertEqual(response.data["schema_version"], 1)
        population = next(
            entry
            for section in response.data["section_definitions"]
            if section["code"] == "population_households"
            for entry in section["entry_types"]
            if entry["key"] == "population"
        )
        count = next(field for field in population["field_definitions"] if field["name"] == "count")
        self.assertEqual(count["type"], "integer")
        self.assertFalse(count["required"])
        resident_status = next(field for field in population["field_definitions"] if field["name"] == "resident_status")
        self.assertEqual(resident_status["type"], "choice")
        self.assertTrue(resident_status["required"])
        self.assertTrue(resident_status["choices"])
        self.assertIn("allow_create", population)

    def test_village_nurse_bootstrap_only_exposes_authorised_sections(self):
        nurse_role = Role.objects.create(code=Role.Codes.VILLAGE_NURSE, name="Village Nurse")
        nurse = User.objects.create_user(username="nurse-a1", password=self.password)
        UserRoleAssignment.objects.create(user=nurse, role=nurse_role)
        UserLocationAssignment.objects.create(user=nurse, village=self.village)
        self.user = nurse
        self.login()

        response = self.client.get(reverse("mobile_api:bootstrap"))
        codes = {section["code"] for section in response.data["section_definitions"]}
        self.assertEqual(codes, {"village_profile", "health", "disability"})

    def test_report_creation_reuses_service_and_rejects_cross_village(self):
        self.login()
        own = self.client.post(
            reverse("mobile_api:reports"),
            {"village_uuid": self.village.uuid, "reporting_period_uuid": self.period.uuid},
            format="json",
        )
        self.assertEqual(own.status_code, 201, own.data)
        self.assertEqual(TNKReport.objects.get(uuid=own.data["uuid"]).section_statuses.count(), 17)

        other = self.client.post(
            reverse("mobile_api:reports"),
            {"village_uuid": self.other_village.uuid, "reporting_period_uuid": self.period.uuid},
            format="json",
        )
        self.assertEqual(other.status_code, 403, other.data)
        self.assertFalse(TNKReport.objects.filter(village=self.other_village).exists())

    def test_cross_village_report_detail_is_not_exposed(self):
        report = TNKReport.objects.create(
            village=self.other_village,
            reporting_period=self.period,
            prepared_by=self.other_user,
            collection_started_at="2026-04-01T00:00:00Z",
        )
        self.login()

        response = self.client.get(reverse("mobile_api:report-detail", args=(report.uuid,)))
        self.assertEqual(response.status_code, 404)

    def test_plain_unbound_jwt_is_rejected(self):
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get(reverse("mobile_api:me")).status_code, 401)

    def test_anonymous_requests_are_rejected(self):
        self.assertEqual(self.client.get(reverse("mobile_api:bootstrap")).status_code, 401)

    def test_sync_batch_is_idempotent_and_changes_are_downloadable(self):
        self.login()
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        age_group = AgeGroup.objects.create(code="25_34", name_en="25-34", minimum_age=25, maximum_age=34)
        local_uuid = uuid.uuid4()
        item = {
            "idempotency_key": str(uuid.uuid4()),
            "operation": "create",
            "resource_type": "population",
            "section_code": "population_households",
            "report_uuid": str(report.uuid),
            "local_uuid": str(local_uuid),
            "values": {
                "age_group": str(age_group.pk),
                "gender": "male",
                "resident_status": "permanent_resident",
                "count": 10,
                "measurement_date": "2026-05-01",
                "measurement_unit": "people",
                "data_source": "estimate",
                "collection_method": "interview",
                "source_reference": "Village register",
                "verification_status": "unverified",
                "confidence_level": "medium",
                "notes": "",
            },
        }

        first = self.client.post(reverse("mobile_api:sync-batch"), {"changes": [item]}, format="json")
        replay = self.client.post(reverse("mobile_api:sync-batch"), {"changes": [item]}, format="json")

        self.assertEqual(first.status_code, 200, first.data)
        self.assertEqual(len(first.data["accepted"]), 1, first.data)
        self.assertEqual(replay.data["accepted"], first.data["accepted"])
        self.assertEqual(PopulationSnapshot.objects.filter(uuid=local_uuid).count(), 1)

        changes = self.client.get(reverse("mobile_api:sync-changes"))
        self.assertEqual(changes.status_code, 200)
        self.assertTrue(changes.data["next_cursor"])
        self.assertTrue(any(change["server_uuid"] == str(local_uuid) for change in changes.data["changes"]))

    def test_sync_batch_returns_record_version_conflict_without_overwrite(self):
        self.login()
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        age_group = AgeGroup.objects.create(code="35_44", name_en="35-44", minimum_age=35, maximum_age=44)
        snapshot = PopulationSnapshot.objects.create(
            report=report,
            village=self.village,
            age_group=age_group,
            gender="female",
            resident_status="permanent_resident",
            count=12,
            measurement_date=date(2026, 5, 1),
            data_source="estimate",
            collection_method="interview",
        )
        item = {
            "idempotency_key": str(uuid.uuid4()),
            "operation": "update",
            "resource_type": "population",
            "section_code": "population_households",
            "report_uuid": str(report.uuid),
            "local_uuid": str(uuid.uuid4()),
            "server_uuid": str(snapshot.uuid),
            "expected_record_version": 0,
            "values": {"count": 99},
        }

        response = self.client.post(reverse("mobile_api:sync-batch"), {"changes": [item]}, format="json")

        self.assertEqual(len(response.data["conflicts"]), 1, response.data)
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.count, 12)

    def test_mobile_evidence_upload_is_scoped_validated_and_idempotent(self):
        self.login()
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        key = str(uuid.uuid4())

        def payload(content=b"\xff\xd8\xff valid image"):
            return {
                "title": "Water source photo",
                "document_type": "photo",
                "confidentiality_level": "restricted",
                "captured_at": "2026-05-02T10:00:00Z",
                "latitude": "-18.141600",
                "longitude": "178.441900",
                "location_accuracy_metres": "8.50",
                "file": SimpleUploadedFile("water.jpg", content, content_type="image/jpeg"),
            }

        url = reverse("mobile_api:report-evidence", args=(report.uuid,))
        first = self.client.post(url, payload(), format="multipart", HTTP_IDEMPOTENCY_KEY=key)
        replay = self.client.post(url, payload(), format="multipart", HTTP_IDEMPOTENCY_KEY=key)

        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(replay.status_code, 201, replay.data)
        self.assertEqual(first.data["uuid"], key)
        self.assertEqual(EvidenceDocument.objects.filter(uuid=key).count(), 1)
        self.assertEqual(self.client.get(url).data[0]["latitude"], "-18.141600")

        changed = payload()
        changed["title"] = "Different metadata"
        mismatch = self.client.post(url, changed, format="multipart", HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(mismatch.status_code, 409)

        invalid = self.client.post(
            url,
            payload(b"not an image"),
            format="multipart",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )
        self.assertEqual(invalid.status_code, 400)

    def test_mobile_evidence_rejects_cross_village_and_locked_report(self):
        other = create_report(village=self.other_village, reporting_period=self.period, prepared_by=self.other_user)
        self.login()
        response = self.client.post(
            reverse("mobile_api:report-evidence", args=(other.uuid,)),
            {"title": "No", "document_type": "photo", "file": SimpleUploadedFile("x.jpg", b"\xff\xd8\xff x", content_type="image/jpeg")},
            format="multipart",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )
        self.assertEqual(response.status_code, 404)

        own = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        TNKReport.objects.filter(pk=own.pk).update(status=TNKReport.Status.LOCKED)
        locked = self.client.post(
            reverse("mobile_api:report-evidence", args=(own.uuid,)),
            {"title": "No", "document_type": "photo", "file": SimpleUploadedFile("x.jpg", b"\xff\xd8\xff x", content_type="image/jpeg")},
            format="multipart",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )
        self.assertEqual(locked.status_code, 403)

    def test_sync_change_cursor_pages_without_skipping_records(self):
        self.login()
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        age_group = AgeGroup.objects.create(code="45_54", name_en="45-54", minimum_age=45, maximum_age=54)
        for gender in ("male", "female"):
            PopulationSnapshot.objects.create(
                report=report, village=self.village, age_group=age_group, gender=gender,
                resident_status="permanent_resident", count=1,
                measurement_date=date(2026, 5, 1), data_source="estimate", collection_method="interview",
            )

        with patch("apps.mobile_api.sync.MAX_CHANGES", 1):
            pages = []
            cursor = None
            while True:
                response = self.client.get(reverse("mobile_api:sync-changes"), {"cursor": cursor} if cursor else {})
                pages.append(response.data)
                cursor = response.data["next_cursor"]
                if not response.data["has_more"]:
                    break

        self.assertGreater(len(pages), 1)
        downloaded = [change["server_uuid"] for page in pages for change in page["changes"]]
        expected = {str(value) for value in PopulationSnapshot.objects.filter(report=report).values_list("uuid", flat=True)}
        self.assertTrue(expected.issubset(set(downloaded)))
        self.assertEqual(len(downloaded), len(set(downloaded)))

    def test_mobile_validation_declaration_and_submission_use_server_workflow(self):
        self.login()
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        report.section_statuses.update(status=ReportSectionStatus.Status.COMPLETE, completion_percentage=100)

        validation = self.client.post(reverse("mobile_api:report-validation", args=(report.uuid,)), {}, format="json")
        self.assertEqual(validation.status_code, 200, validation.data)
        self.assertFalse(any(issue["severity"] == "critical" for issue in validation.data["issues"]))

        without_declaration = self.client.post(reverse("mobile_api:report-workflow", args=(report.uuid, "mark_ready")), {}, format="json")
        self.assertEqual(without_declaration.status_code, 400)
        declaration = self.client.post(reverse("mobile_api:report-declaration", args=(report.uuid,)), {"acknowledged": True}, format="json")
        self.assertEqual(declaration.status_code, 200, declaration.data)

        ready = self.client.post(reverse("mobile_api:report-workflow", args=(report.uuid, "mark_ready")), {}, format="json")
        self.assertEqual(ready.status_code, 200, ready.data)
        self.assertEqual(ready.data["status"], TNKReport.Status.READY_FOR_VALIDATION)
        submitted = self.client.post(reverse("mobile_api:report-workflow", args=(report.uuid, "submit")), {}, format="json")
        self.assertEqual(submitted.status_code, 200, submitted.data)
        self.assertEqual(submitted.data["status"], TNKReport.Status.SUBMITTED)

    def test_mobile_validation_is_cross_village_scoped(self):
        report = create_report(village=self.other_village, reporting_period=self.period, prepared_by=self.other_user)
        self.login()
        self.assertEqual(self.client.get(reverse("mobile_api:report-validation", args=(report.uuid,))).status_code, 404)
        self.assertEqual(self.client.post(reverse("mobile_api:report-declaration", args=(report.uuid,)), {"acknowledged": True}, format="json").status_code, 404)

    def test_returned_report_detail_includes_reviewer_comment(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        TNKReport.objects.filter(pk=report.pk).update(status=TNKReport.Status.RETURNED_TO_VILLAGE)
        ApprovalAction.objects.create(
            report=report, user=self.other_user, user_full_name="Tikina Reviewer", user_role="Mata ni Tikina",
            action_type="return", from_status=TNKReport.Status.SUBMITTED, to_status=TNKReport.Status.RETURNED_TO_VILLAGE,
            comment="Correct the water section.",
        )
        report.section_statuses.filter(section_code="water").update(status=ReportSectionStatus.Status.NEEDS_ATTENTION)
        self.login()

        response = self.client.get(reverse("mobile_api:report-detail", args=(report.uuid,)))

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["returned_review"]["reviewer"], "Tikina Reviewer")
        self.assertEqual(response.data["returned_review"]["comment"], "Correct the water section.")
        self.assertEqual(response.data["returned_review"]["affected_sections"], ["water"])

    def test_dashboard_returns_scoped_server_calculated_indicators(self):
        report = create_report(village=self.village, reporting_period=self.period, prepared_by=self.user)
        definition = IndicatorDefinition.objects.create(
            code="total_population", name_en="Total population", name_fj="Lewenivanua", description="Population",
            formula_description="Server calculation", measurement_unit="people", geographic_level="village",
            effective_from=date(2026, 1, 1),
        )
        IndicatorValue.objects.create(
            indicator=definition, reporting_period=self.period, village=self.village,
            value=Decimal("418"), calculation_status=IndicatorValue.CalculationStatus.CALCULATED,
        )
        self.login()

        response = self.client.get(reverse("mobile_api:dashboard"), {"report_uuid": report.uuid})

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["location"]["village"], "Village A1")
        self.assertEqual(response.data["reporting_period"]["quarter"], 2)
        self.assertEqual(response.data["indicators"][0]["code"], "total_population")
        self.assertEqual(response.data["indicators"][0]["name_en"], "Total population")
        self.assertEqual(response.data["indicators"][0]["name_fj"], "Lewenivanua")
        self.assertEqual(response.data["indicators"][0]["value"], "418.0000")

    def test_user_can_persist_supported_mobile_language(self):
        self.login()
        response = self.client.patch(reverse("mobile_api:me"), {"preferred_language": "fj"}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_language, "fj")

        invalid = self.client.patch(reverse("mobile_api:me"), {"preferred_language": "fr"}, format="json")
        self.assertEqual(invalid.status_code, 400)

    def test_dashboard_report_filter_cannot_cross_village(self):
        report = create_report(village=self.other_village, reporting_period=self.period, prepared_by=self.other_user)
        self.login()
        response = self.client.get(reverse("mobile_api:dashboard"), {"report_uuid": report.uuid})
        self.assertEqual(response.status_code, 404)
