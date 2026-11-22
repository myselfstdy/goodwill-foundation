# API documentation

## Conventions

- Base path: `/api` (no `/api/v1` prefix).
- JSON requests/responses unless a route returns CSV, PDF, or printable HTML.
- Authenticated requests send `Authorization: Bearer <access-token>`.
- Route definitions are in `server/src/prisma-router.js`; equivalent showcase routes are in `server/src/index.js`.
- Admin means authenticated `ADMIN`; donor means authenticated `DONOR` with server-side ownership checks where the resource is private.

## Authentication and public campaigns

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health` | Public | Health check; database mode checks connection |
| POST | `/auth/register` | Public | Create donor account |
| POST | `/auth/login` | Public | Verify credentials and issue tokens |
| POST | `/auth/refresh` | Refresh token | Rotate refresh token |
| POST | `/auth/logout` | Signed in | Revoke refresh sessions and invalidate token version |
| GET | `/auth/me` | Signed in | Current identity |
| POST | `/auth/forgot-password` | Public | Create short-lived reset token; production response is generic |
| POST | `/auth/reset-password` | Reset token | Change password and revoke sessions |
| GET | `/campaigns` | Public | Search/list campaigns with pagination and filters |
| GET | `/campaigns/:id` | Public | Read by id or slug |
| POST | `/campaigns` | Admin | Create campaign |
| PATCH | `/campaigns/:id` | Admin | Update campaign |
| DELETE | `/campaigns/:id` | Admin | Pause campaign rather than hard-delete |
| GET | `/campaigns/:id/updates` | Public/role-aware | Read campaign updates |
| POST | `/campaigns/:id/updates` | Admin | Publish update and notify followers |

## Donations, receipts, reports

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/donations` | Guest or donor | Create gift and simulate payment |
| GET | `/donations` | Donor/admin | List authorized donation records with filters |
| GET | `/donations/:id` | Owner/admin | Read one donation |
| POST | `/donations/:id/retry` | Owner | Retry eligible failed donation |
| GET | `/donor/donations/export.csv` | Donor | Export own giving history |
| GET | `/receipts` | Donor/admin | List authorized receipt records |
| GET | `/receipts/:id` | Owner/admin | Printable receipt page |
| GET | `/receipts/:id/pdf` | Owner/admin | Receipt PDF |
| GET | `/receipt-verification/:receiptNumber` | Public | Verify a receipt number |
| GET | `/donor/annual-statement.pdf` | Donor | Own annual statement PDF |
| GET | `/dashboard` | Admin | Admin aggregate dashboard |
| GET | `/reports` | Admin | Report summary data |
| GET | `/reports/export.csv` | Admin | Donation report CSV |
| GET | `/activity` | Admin | Audit/activity feed |
| GET | `/donors` | Admin | Search/paginate donor records |
| POST | `/donors` | Admin | Create donor record |
| GET/PATCH | `/donors/:id` | Admin | Read/update donor record/account status |
| GET | `/donors/export.csv` | Admin | Donor CSV export |

## Donor profile and self-service

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET/PATCH | `/donor/profile` | Donor | Read/update own profile |
| POST | `/donor/profile/email-verification` | Donor | Start verified email change |
| POST | `/donor/profile/email-verification/confirm` | Donor + token | Confirm new email |
| GET | `/donor/dashboard` | Donor | Own giving overview |
| GET | `/donor/impact` | Donor | Impact history and badge criteria |
| GET/POST/DELETE | `/donor/saved-campaigns[/:campaignId]` | Donor | List/save/remove saved campaign |
| GET/POST/DELETE | `/donor/followed-campaigns[/:campaignId]` | Donor | List/follow/unfollow cause |
| GET | `/donor/campaign-updates` | Donor | Updates from followed campaigns |
| GET/PATCH | `/donor/preferences` | Donor | Giving preferences |
| GET/PATCH | `/donor/dashboard-preferences` | Donor | Dashboard layout preferences |
| GET/PATCH | `/donor/notifications/preferences` | Donor | Notification preferences |
| GET | `/notifications` | Signed in | List own notifications |
| PATCH | `/notifications/:id/read` | Owner | Mark one notification read |
| PATCH | `/notifications/read-all` | Signed in | Mark all own notifications read |
| GET | `/donor/security/sessions` | Donor | List own sessions |
| DELETE | `/donor/security/sessions/:id` | Donor | Revoke own refresh session |
| GET | `/donor/security/activity` | Donor | Own login/security activity |
| POST | `/donor/security/delete-request` | Donor | Submit password-confirmed deletion request |
| GET | `/donor/data-export` | Donor | Export own account data as JSON |
| GET/POST | `/donor/support/tickets` | Donor | List/create own tickets |
| POST | `/donor/support/tickets/:id/replies` | Ticket owner | Reply to own open ticket |
| GET | `/admin/support/tickets` | Admin | List support queue |
| PATCH | `/admin/support/tickets/:id` | Admin | Update status and respond |
| GET | `/admin/deletion-requests` | Admin | Review deletion requests |
| PATCH | `/admin/deletion-requests/:id` | Admin | Approve/reject; approval disables account |

## General signed-in profile routes

`GET/PATCH /profile` and `PATCH /profile/password` exist for the general authenticated profile/password flow. The donor-specific profile endpoints above add donor account details and email verification.

## Error and validation behavior

Zod rejects invalid request bodies with a client error. Missing/invalid JWTs return unauthorized responses; donor/admin role mismatches return forbidden responses; private resources outside the current donor scope are hidden or denied. Exact status codes and DTOs are defined in the matching handler. Receipt creation and payment behavior are simulated.
