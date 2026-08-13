# Security architecture

Access is deny-by-default and enforced using active role, explicit section permission, confidentiality clearance, and Province/Tikina/Village scope. Evidence downloads additionally validate document level, linked object, linked location, and report status; Nginx does not serve protected media. Analytical exports call the same central policy, contain location/report aggregates only, and are audited. The authoritative role and data matrix is in `confidentiality-access-control.md`.

Export presentation is documented in `export-quality.md`. Analysts receive scoped aggregate/report-summary rows only; named approval history, project details, and evidence references require detailed report/section/document permission. Spreadsheet formulas are neutralised and sensitive record fields are excluded at dataset construction rather than hidden after rendering.

Production disables DEBUG, uses environment secrets, secure cookies, HTTPS proxy headers, session expiry, CSRF protection and PostgreSQL. This design does not itself claim legal or policy compliance.
