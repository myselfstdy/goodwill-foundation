# API documentation

Base URL in local development: `http://localhost:4000/api`. JSON responses use HTTP status codes and a concise `{ "error": "..." }` body on failure. Authenticated endpoints use `Authorization: Bearer <access-token>`.

## Authentication

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| POST | `/auth/login` | Public | `{email,password}` → access token, refresh token, user |
| POST | `/auth/register` | Public | `{name,email,password}` → donor account and access token |
| POST | `/auth/refresh` | Public | `{refreshToken}` → rotated access and refresh tokens |
| POST | `/auth/logout` | Signed in | Revoke refresh sessions |
| GET | `/auth/me` | Signed in | Current token claims |

## Campaigns and gifts

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/campaigns` | Public | List campaigns and raised totals |
| GET | `/campaigns/:id` | Public | Campaign by ID or slug |
| POST | `/campaigns` | Admin | Create campaign; required title, description, category and positive target |
| PATCH | `/campaigns/:id` | Admin | Update provided campaign fields |
| DELETE | `/campaigns/:id` | Admin | Soft-pause campaign |
| POST | `/donations` | Guest or signed in | `{campaignId,amount,name,email,anonymous,simulate}`; `simulate` is `success` or `failure` |
| GET | `/donations` | Signed in | Admin sees all; donor sees their linked history |
| POST | `/donations/:id/retry` | Owner or admin | Retry a failed donation in the simulator |
| GET | `/receipts` | Signed in | Admin sees all; donor sees their receipts |
| GET | `/receipts/:id` | Owner or admin | Printable HTML receipt; browser print can save as PDF |

## Administration, reports, profile

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/dashboard` | Admin | Organization totals, chart series, campaign progress, recent donations |
| GET | `/donors?q=` | Admin | Donor search with aggregate giving details |
| POST | `/donors` | Admin | Create donor contact record `{name,email,phone?}` |
| PATCH | `/donors/:id` | Admin | Update donor name, email or phone |
| GET | `/reports` | Admin | Successful giving totals grouped by campaign, day, month, and donor |
| GET | `/reports/export.csv` | Admin | Download donation CSV |
| GET | `/activity` | Admin | Audit history |
| GET/PATCH | `/profile` | Signed in | View/update account profile |
| PATCH | `/profile/password` | Signed in | Change password and revoke refresh sessions |
| GET | `/health` | Public | API mode and status (not a database connectivity check) |

All donation amounts must be positive and no more than two decimal places. This API uses a locally simulated payment outcome only; no card number or banking data is accepted.

## Donor self-service portal endpoints

All routes below are under `/api`. Except receipt verification and password recovery, routes require a bearer access token. Donor endpoints derive the donor identity from that token; request bodies never select a donor ID. Paginated list responses use `{ items, pagination: { page, limit, total, pages } }` where indicated.

### Overview, giving, and receipts

| Method and path | Access | Purpose |
| --- | --- | --- |
| `GET /donor/dashboard` | Donor | Successful-gift totals, receipts, recent gifts, supported campaigns, and recommendations. |
| `GET /donor/impact` | Donor | Monthly/yearly/campaign totals, timeline, configured badges, and followed-campaign updates. |
| `GET /donations` | Donor or admin | Search/filter donation records; donor results are always ownership-scoped. Query: `q`, `status`, `campaignId`, `method`, `from`, `to`, `page`, `limit`, `sort`, `order`. |
| `GET /donations/:id` | Owner or admin | One donation and its payment attempts. Other donors receive 404. |
| `GET /donor/donations/export.csv` | Donor | Download own donation history. |
| `GET /receipts` | Donor or admin | Receipt list; donor result is scoped through the linked donation. |
| `GET /receipts/:id/pdf` | Owner or admin | Server-generated PDF. Only successful gifts with a receipt are returned. |
| `GET /receipt-verification/:receiptNumber` | Public | Verifies a receipt and returns receipt ID, amount, currency, campaign, and date; no donor identity. |
| `GET /donor/annual-statement.pdf?year=YYYY` | Donor | Successful gifts for a selected year as a PDF statement. |

### Campaigns and preferences

| Method and path | Access | Purpose |
| --- | --- | --- |
| `GET /donor/saved-campaigns` | Donor | List saved campaigns. |
| `POST /donor/saved-campaigns/:campaignId` | Donor | Save a campaign without donating. |
| `DELETE /donor/saved-campaigns/:campaignId` | Donor | Remove a saved campaign. |
| `GET /donor/followed-campaigns` | Donor | List campaigns followed for updates. |
| `POST /donor/followed-campaigns/:campaignId` | Donor | Follow a campaign. |
| `DELETE /donor/followed-campaigns/:campaignId` | Donor | Unfollow a campaign. |
| `GET /campaigns/:id/updates` | Campaign follower or admin | Read posted campaign updates. |
| `POST /campaigns/:id/updates` | Admin | Post a campaign update and notify its followers. Body: `{ title, body }`. |
| `GET/PATCH /donor/preferences` | Donor | Read or update amount/category, anonymity, demo payment method, privacy, and message defaults. |
| `GET/PATCH /donor/dashboard-preferences` | Authenticated user | Read or update donor dashboard section visibility. |

### Profile, notifications, security, and support

| Method and path | Access | Purpose |
| --- | --- | --- |
| `GET/PATCH /donor/profile` | Donor | Read or update name, phone, and validated small profile image. |
| `POST /donor/profile/email-verification` | Donor | Validate current password and issue a short-lived email verification token. |
| `POST /donor/profile/email-verification/confirm` | Donor | Confirm email change; revokes refresh sessions and increments token version. |
| `POST /auth/forgot-password` | Public, rate-limited | Start account recovery. Production response is generic. |
| `POST /auth/reset-password` | Public, rate-limited | Redeem a short-lived reset token and revoke existing sessions. |
| `GET/PATCH /donor/notifications/preferences` | Donor | Read/update notification categories. |
| `PATCH /notifications/read-all` | Authenticated user | Mark own notifications read. |
| `GET /donor/security/sessions` | Donor | List unexpired refresh sessions without returning token material. |
| `DELETE /donor/security/sessions/:id` | Donor | Revoke one of the donor's sessions. |
| `GET /donor/security/activity` | Donor | Recent own login/security events. |
| `POST /donor/security/delete-request` | Donor | Submit a password-confirmed deletion request. |
| `GET /donor/data-export` | Donor | Download own account, donations, receipts, preferences, notifications, and support history. |
| `GET/POST /donor/support/tickets` | Donor | List or create own support tickets. Creation body: `{ subject, category, message }`. |
| `POST /donor/support/tickets/:id/replies` | Ticket owner | Add a reply to an open ticket. |
| `GET /admin/support/tickets` | Admin | View support queue. |
| `PATCH /admin/support/tickets/:id` | Admin | Set ticket status and optionally reply. |

The project uses JSON demo mode only when explicitly configured for a showcase. PostgreSQL mode mounts the Prisma API and does not fall back to the JSON store.
