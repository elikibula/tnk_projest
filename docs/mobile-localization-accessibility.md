# Phase 11: localization and accessibility

The mobile shell supports English (`en`) and iTaukei/Fijian (`fj`) through
Flutter ARB localization files. The dashboard language selector persists the
selection in secure device storage and attempts to update `PATCH /api/v1/me/`;
the local selection continues to work when the API is unavailable.

Only translations already present in the project's reviewed Django iTaukei
catalogue are used. Unreviewed text falls back to English. Server reference
labels expose `name_en` and `name_fj`, and the client falls back to English
when the iTaukei value is blank.

Dashboard controls use 56 dp action targets, icons plus text for operational
states, semantic metric labels, and a one-column metric layout on narrow
screens or when large text is enabled. Flutter text scaling remains enabled.
