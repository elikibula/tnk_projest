# Reference vocabulary migration plan

Date reviewed: 7 August 2026
Scope: Phase G vocabulary review. This document is a plan; it does not approve terminology or alter official records.

## Decision summary

Most reviewed fields are unrestricted text. They should become controlled choices or governed reference records, but the final English and iTaukei labels and policy meanings require approval from the TNK data owner. No non-empty operational values were found in the local database for the reviewed safety, business, project, climate, or infrastructure-condition fields. Crop default units contain only `count` and `kg`.

No data migration is included in Phase G. With no representative production value inventory, mapping terms based only on spelling similarity would be unsafe. The only mappings considered deterministic are whitespace/case normalisation after collision review and exact aliases explicitly approved in a signed mapping table.

## Current and proposed vocabulary

| Area | Current fields | Current control | Proposed canonical codes | Migration decision |
|---|---|---|---|---|
| Community safety | `severity` | Free text | `low`, `moderate`, `high`, `critical`, `unknown` | Owner must approve definitions and whether offence defaults may prefill but never override an incident. |
| Community safety | `case_status` | Free text/blank | `not_reported`, `reported`, `under_investigation`, `referred`, `resolved`, `closed`, `unknown` | Do not infer status from `reported_to_authority`, action notes, or dates. |
| Business | `revenue_band` | Free text/blank | Governed reference rows with code, lower/upper FJD bounds, effective dates, and bilingual labels | Thresholds are policy decisions; never derive a band from narrative text. |
| Business | `licence_status` | Free text/blank | `not_required`, `unlicensed`, `application_pending`, `licensed`, `expired`, `suspended`, `unknown` | Licence expiry alone does not prove status; review conflicts manually. |
| Business | `operating_status` | Free text | `planned`, `operating`, `temporarily_closed`, `closed`, `unknown` | Exact approved aliases only. Existing validation for `closed` and closure date must use the canonical code. |
| Business | `support_required` | Narrative text | Preserve narrative; optionally add a many-to-many support-needs reference such as finance, licensing, market access, training, equipment, premises, digital, and other | Never replace or parse the narrative automatically. A structured field should be additive. |
| Project | `project_category` | Free text | Governed bilingual reference model | Categories must align with the approved IVDP taxonomy. |
| Project | `priority` | Free text | `low`, `medium`, `high`, `critical`, `unknown` | Do not calculate priority from budget, risk, or narrative. |
| Project | `project_status` | Free text | `proposed`, `approved`, `not_started`, `in_progress`, `on_hold`, `completed`, `cancelled`, `unknown` | Exact aliases only; completion cannot be inferred without the required actual completion date. |
| Project risk | `risk_type` | Free text | Governed bilingual reference model | Risk taxonomy needs programme-owner approval. |
| Project risk | `likelihood` | Free text | `rare`, `unlikely`, `possible`, `likely`, `almost_certain`, `unknown` | Do not translate numeric or narrative ratings without an approved matrix. |
| Project risk | `impact` | Free text | `insignificant`, `minor`, `moderate`, `major`, `severe`, `unknown` | Definitions and thresholds require approval. |
| Project risk | `status` | Free text | `open`, `monitoring`, `mitigated`, `accepted`, `closed`, `unknown` | Do not infer from mitigation text. |
| Climate | `hazard_type` | Free text | Governed bilingual reference model aligned to Fiji disaster/climate terminology | Multi-hazard observations may require a relationship rather than one choice. |
| Climate | `severity` | Free text | `low`, `moderate`, `high`, `critical`, `unknown` | Impact thresholds must be approved; do not infer from affected counts or estimated loss. |
| Infrastructure | asset, water source, energy asset, and evacuation-centre `condition`; housing `condition` | Housing already uses `good`, `fair`, `poor`, `unsafe`, `destroyed`, `under_construction`; other models are free text | Reuse those six codes plus `unknown`, subject to owner confirmation | Only exact approved aliases may be mapped. Preserve model-specific operational status separately from physical condition. |
| Measurement units | analytical `measurement_unit`, crop default/area/quantity units, project units, waste units, energy capacity units | Free text; local crop defaults are `count` and `kg` | Governed unit reference with stable code, symbol, dimension, multiplier where applicable, bilingual label, and active/effective dates | Retain `count` and `kg`. Do not convert values or map ambiguous terms such as bag, bundle, load, tank, or acre without source-specific rules. |

## Safe migration sequence

1. Export distinct values and counts from a production copy, split by model and field. Include blanks, Unicode variants, and values used by approved/locked/archived reports.
2. Obtain a signed bilingual vocabulary and definitions from the data owner. Give every canonical item a stable machine code independent of its display label.
3. Produce a mapping table with `source_model`, `source_field`, `old_value`, `canonical_code`, `mapping_reason`, `approved_by`, and `approved_at`. Flag every unmapped or one-to-many value for manual resolution.
4. Run a dry-run migration that reports row counts, collisions, unmapped values, affected official reports, and before/after hashes. It must make no writes.
5. Add reference tables or `TextChoices` and temporary nullable canonical fields. Preserve original text during transition.
6. Backfill only approved deterministic mappings in a transactional, reversible data migration. Record the migration actor/version and retain the mapping artefact.
7. Reconcile counts and samples, run the complete test suite, and obtain business-owner acceptance before making canonical fields required.
8. Update forms, filters, analytics, exports, APIs, data dictionary, and English/iTaukei catalogues together. Retire legacy fields only under an approved retention plan.

## Deterministic mapping rule

A mapping is deterministic only when one old value has exactly one approved canonical meaning in that model and context. Trimming surrounding whitespace, Unicode normalisation, and case folding may be used to identify candidates, but only after proving that they create no semantic collision. Blank must remain unknown/not supplied; it must not be converted to zero, `none`, `closed`, or `not_required`.

## Rollback and audit

The transition should be additive. Keep original values until reconciliation and retention approval, make the mapping version reproducible, and create an audit event for the governed migration. Rollback restores the prior canonical field values from the migration ledger; it must never delete the original text or rewrite immutable official snapshots in place.
