# Software Requirements Specification

## Purpose and scope

Goodwill is a web application for a small nonprofit to publish fundraising campaigns, record simulated gifts, issue successful-gift receipts, manage donor records, and review activity and reports. Guests can browse and give without creating an account. Donors can register and view their own account records. Administrators manage campaigns and review the organization-wide record.

## Stakeholders and roles

| Role | Capabilities |
| --- | --- |
| Guest | Browse active campaigns; make an identified or anonymous simulated gift |
| Donor | Guest capabilities plus register/sign in, view personal donations and receipts, edit profile |
| Administrator | View organization dashboard; manage campaigns and donors; review donations, receipts, reports, activity, and settings |

## Functional requirements

1. The system shall authenticate users with email/password, hash passwords, issue expiring JWT access tokens, support refresh-token rotation, and revoke sessions on logout/password change.
2. Public users shall browse campaigns and submit a donation with campaign, amount, donor contact, and anonymity preference.
3. The payment simulator shall record successful or failed attempts, a reference, timestamp, and final donation state; it shall never request or process card data.
4. Successful gifts shall receive one unique receipt number. Failed gifts shall not receive a receipt. Failed gifts may be retried.
5. Administrators shall view aggregate successful giving, donor count, active campaign count, transaction count, monthly giving, recent activity, and campaign progress.
6. Administrators shall search donors; create, edit, and pause campaigns; and view/export donations and report data.
7. Donors shall only view their own private donations and receipts; administrators shall have organization-wide access.
8. Important record and administration changes shall produce timestamped audit events.
9. The system shall validate API inputs, limit authentication attempts, set secure HTTP headers, and avoid exposing password hashes or refresh-token hashes.

## Nonfunctional requirements

- Responsive public pages and administration pages, with clear loading, empty, and error states.
- PostgreSQL as the intended relational store with UUID identifiers, foreign keys, monetary decimals, uniqueness, and indexes.
- Currency amounts shall be validated to two decimal places. The current demonstration stores cents-compatible decimal values as JSON numbers; PostgreSQL columns use `Decimal(12,2)`.
- API error responses shall be concise and not expose stack traces.
- No external payment provider integration is in scope.

## Constraints and assumptions

Runtime data currently uses a local JSON demonstration store because a PostgreSQL service is not present in the supplied environment. Prisma models, initial migration, and seed script are provided, but runtime database integration still needs completion. Simulated payment outcomes are selected explicitly in the demo checkout.

## Acceptance criteria

- Campaign browsing and search work without authentication.
- Both successful and failed demo donation outcomes are visible and traceable.
- A successful donation has a printable receipt; a failed donation does not.
- Admin and donor access are separated by role and private records are scoped to the donor.
- Admin reports can be downloaded as CSV.
- Project setup, test intent, data model, and limitations are documented.
