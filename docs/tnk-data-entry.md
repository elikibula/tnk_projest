# Turaga ni Koro data-entry workflow

An authorised Turaga ni Koro opens **Reports**, creates or selects a draft report, and opens one of its 17 section cards. Fifteen substantive sections now expose 42 explicit record types covering village profile, governance, visits/training, population/households, infrastructure, water, sanitation, energy, health, disability, agriculture, economy, projects, resilience and culture. Report/village/period ownership is assigned server-side and related choices are limited to the report village.

Each record saves independently and moves a new section to **In progress**. The user checks entries, updates section progress, uploads protected evidence, completes the declaration, validates and submits. Once submitted, approved or locked, normal entry routes become read-only. Review roles may inspect scoped records but cannot use Turaga ni Koro authoring routes.

## Form behaviour

- Report, village and quarter are assigned on the server and cannot be changed through form data.
- Date-based quarterly entries must fall inside the report period.
- `0` means a confirmed none; an empty optional value means it was not answered.
- A Turaga ni Koro can submit an item for verification but cannot mark it verified.
- Legacy direct attachment fields are not exposed. Use the protected evidence upload so access checks and checksums always apply.
- The current report shows record counts and the entries from its linked previous approved quarter.
- Validation recalculates completeness, evidence, timeliness, verification and consistency scores, and shows issues on the report page.

## Correcting mistakes

Open the relevant section and use **Edit** beside the record. The report must still be Draft or Returned to village. Submitted, approved and locked reports cannot be silently changed. If a reviewer returns a report, the correction instructions appear as a workflow message and the village user can edit and resubmit.

## iTaukei wording

Static interface wording is stored in `backend/locale/fj/LC_MESSAGES/django.po`. Dynamic form labels and choices are stored in `backend/apps/reporting/itaukei.py`. The current translations are clearly treated as drafts and should receive an authorised language review before production use.
