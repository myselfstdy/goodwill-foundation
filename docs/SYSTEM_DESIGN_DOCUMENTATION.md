# System design documentation

## Context and deployment

The React/Vite client is deployed to Vercel. `client/vercel.json` forwards `/api/*` to `https://goodwill-foundation.onrender.com/api/*` and routes other paths to the SPA entry point. The Express service selects the PostgreSQL Prisma router when `DATABASE_URL` is set and `DEMO_MODE` is not `true`; otherwise it uses the JSON demo store. PostgreSQL is configured for Neon by deployment documentation. Runtime health and seed state are environment-dependent.

## Request path

1. Browser sends a request to the same-origin `/api` path.
2. Vercel forwards it to the Render Express service.
3. Express applies security headers, CORS, body-size handling, and auth rate limits.
4. Protected route middleware verifies the JWT, active user, token version, and role; owner-scoped handlers constrain data by authenticated user ID.
5. Zod validates request bodies.
6. Prisma reads/writes PostgreSQL in database mode; the demo store persists JSON only for the local showcase.
7. API returns JSON, CSV, HTML printable receipt, or generated PDF according to route.

## Donation transaction

Campaign status and amount are validated before a donation is recorded. The payment provider is a local simulator. A successful result records the payment attempt, successful donation and receipt and updates related totals within the implementation's transaction flow. A failed result remains failed and has no receipt; retry is separately represented as another attempt. An optional idempotency key protects repeated requests.

## Data model

The schema defines 23 models: User, Donor, Campaign, Donation, PaymentAttempt, Receipt, AuditLog, RefreshToken, Notification, DonorPreferences, SavedCampaign, CampaignFollow, NotificationPreference, AchievementBadge, DonorAchievement, SupportTicket, SupportTicketReply, LoginActivity, AccountDeletionRequest, CampaignUpdate, DonorDashboardPreferences, EmailVerification, and PasswordReset. 

Primary identifiers are UUIDs. Gift/campaign amounts use Decimal(12,2). Unique values include User.email, Campaign.slug, Donation.idempotencyKey and transactionRef, PaymentAttempt.reference and (donationId, attemptNumber), Receipt.donationId and receiptNumber, token hashes, and user/campaign or donor/badge pairs. The authoritative schema and complete field/relationship details are in `server/prisma/schema.prisma`.

## Design decisions and boundaries

- Guest gifts can exist without an account-linked donor; registering with the same email does not automatically claim a guest record.
- Donor endpoints scope gifts, receipts, profile, support, notifications, and security history to the authenticated account.
- Admin endpoints provide organization-wide operational access.
- Receipts are unique per donation and created only on successful simulated outcomes.
- Password reset and email verification tokens are persisted as hashes, but production delivery requires a configured mail service.
- Deletion approval disables sign-in; it does not automatically erase historical records.

## Diagram source and exports

Editable Mermaid sources are under `docs/diagrams/`; rendered SVG and PNG assets are under `docs/diagrams/rendered/`. Diagrams use consistent navy/teal styling with short labels. The ER diagram emphasizes the core giving model; the system design and database inventory document supporting relations so the visual remains readable.
