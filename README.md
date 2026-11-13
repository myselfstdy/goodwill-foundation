# Goodwill Foundation — Donation Management System

Goodwill Foundation is an academic demonstration app for nonprofit campaigns and donor self-service. It includes a React donor portal, Express API, PostgreSQL persistence through Prisma, and a clearly simulated donation checkout. Demo transactions do not transfer money.

## Architecture

- `client/` — React 18, Vite, React Router, Axios, Recharts, and Lucide React.
- `server/src/` — Express API, JWT authentication, Zod validation, demo store, Prisma API, and PDF generation.
- `server/prisma/` — PostgreSQL schema, incremental migrations, and fictional seed data.
- `server/tests/` — API security and donor workflow tests; `client/src/` includes frontend utility tests.
- PostgreSQL is the persistent application database when `DATABASE_URL` is set and `DEMO_MODE=false`. JSON persistence is for local/demo showcase use only.

## Requirements

- Node.js 20+ and npm.
- PostgreSQL 14+ for database mode.
- No external payment, email, or SMS account is required for the core demonstration.

## Install and run the demo

1. From the project root, install packages:

   ```sh
   npm install
   ```

2. Copy `.env.example` to `server/.env`. Keep `DEMO_MODE=true` for a local showcase.
3. Start the API and client:

   ```sh
   npm run dev
   ```

4. Open `http://localhost:5173`. The health endpoint is `http://localhost:4000/api/health`.

Demo administrator: `VVITU@ac.in` / `VVITU@123`.

Seeded donor accounts use the listed addresses in `server/prisma/seed.js` and password `DonorDemo!23`. Donors can also register at `/register`.

## PostgreSQL setup

1. Create a PostgreSQL database named `donation_management_db`.
2. Set `DATABASE_URL` in `server/.env` to that database.
3. Set long, random values for `JWT_SECRET` and `JWT_REFRESH_SECRET`; set `DEMO_MODE=false`.
4. Generate the Prisma client and apply migrations:

   ```sh
   npm run db:generate
   npm run db:migrate
   npm run db:seed
   ```

For an existing database seeded with the earlier demo admin, run `npm run db:seed` once to change that account to the VVITU login above.

5. Start the app with `npm run dev`. `/api/health` reports `mode: postgres` and database connectivity.

The initial migration creates the existing application tables. `20261113000000_donor_portal` adds the donor portal models and security/profile fields. Apply migrations before starting a new database. Database migration and database-mode endpoint behavior require a reachable PostgreSQL instance; schema validation and client generation can be run without one.

## Donor portal walkthrough

1. Register a donor or sign in with a seeded donor account.
2. Open **Overview** to see successful giving totals, supported campaigns, receipts, recent activity, and recommendations.
3. Use **My Donations** to search and filter by status, campaign, payment method, date range, and sort order. Download the CSV history or open a record for its demo reference and payment attempt.
4. Use **My Receipts** to download a receipt PDF, verify a receipt number, or download a yearly giving statement. Only successful donations have receipts.
5. Browse public campaigns and save or follow a cause. **Saved Campaigns** and **Supported Campaigns** keep those lists separate; campaign follows receive in-app updates.
6. Open **My Impact** for monthly, yearly, and campaign charts, a successful-gift timeline, and badges with visible criteria. No beneficiary counts are fabricated.
7. **Account Settings** stores giving and notification preferences and dashboard section choices. Preferences prefill the donation form.
8. **My Profile** updates name, phone, and a small profile image; email changes require a verification token. **Security & Privacy** provides password changes, session review/revocation, activity history, data export, and deletion requests.
9. **Help & Support** creates private tickets and lets the donor reply. Administrators can respond from **Support** in their workspace.
10. Every checkout is labeled as a demo payment. Select the failure option to confirm that failed gifts do not count toward totals or receive a receipt.

## Password and email recovery

The project does not have an email delivery service configured. In local development, forgot-password and email-verification endpoints return a short-lived development token so the flows can be demonstrated. In production mode, the API returns a generic response and does not disclose tokens; production recovery therefore requires an email provider to be configured before deployment.

## API summary

Protected donor routes use the authenticated donor account and check ownership server-side. The detailed endpoint list is in [`docs/API-documentation.md`](docs/API-documentation.md).

- `/api/donor/dashboard`, `/api/donor/impact`
- `/api/donations`, `/api/donations/:id`, `/api/donor/donations/export.csv`
- `/api/receipts`, `/api/receipts/:id/pdf`, `/api/receipt-verification/:receiptNumber`, `/api/donor/annual-statement.pdf`
- `/api/donor/saved-campaigns`, `/api/donor/followed-campaigns`, `/api/donor/campaign-updates`
- `/api/donor/profile`, `/api/donor/preferences`, `/api/donor/dashboard-preferences`
- `/api/notifications`, `/api/donor/notifications/preferences`
- `/api/donor/security/*`, `/api/donor/data-export`
- `/api/donor/support/tickets`, `/api/admin/support/tickets`

## Tests and build

```sh
npm test
npm run build
$env:DATABASE_URL="postgresql://postgres:replace-me@localhost:5432/donation_management_db?schema=public"; npx prisma validate --schema server/prisma/schema.prisma
npm run db:generate
```

The API tests run against the demo store and cover donor ownership, totals, receipts, filters, preferences, support, and recovery. PostgreSQL migrations and Prisma-backed routes should also be exercised against a configured local/test database before deployment.

## Known limitations

- All payment attempts are simulated; this project does not collect or transfer money.
- Email and SMS delivery are not configured. Recovery tokens are only exposed in non-production development mode.
- Profile pictures are stored as small validated image data URLs in the database; use object storage for larger production uploads.
- Deletion is a request-and-review workflow. Donor access can be disabled after administrative approval; automated anonymization and retention policy are not configured.
- The PDF receipts and annual statements are generated server-side as simple printable documents, not tax documents.
- The production bundle currently reports a Vite chunk-size warning; the build succeeds.
- No live PostgreSQL service was available in the development workspace, so the new migration was not applied here.
