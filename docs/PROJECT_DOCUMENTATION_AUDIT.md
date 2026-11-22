# Goodwill Foundation documentation audit

**Audit date:** 14 November 2026  
**Evidence reviewed:** repository source, Prisma schema and migrations, package manifests, Vercel configuration, automated tests, and the two supplied Word documents. The reference financial-report generator is used for organization and visual presentation only; no accounting features are carried into the Goodwill report.

## Executive summary

The donation-system document provides useful context and role descriptions, but several technical claims do not match the current repository. The source and Prisma schema are authoritative. The updated report and supporting documents correct endpoint paths, database model names, stack details, payment semantics, current features, test evidence, and deployment boundaries.

## Implemented and verified in source

- Public campaign browsing/search/detail and admin campaign create/update/pause.
- Guest and donor simulated donation workflows, payment attempts, retry behavior, success-only receipt generation, receipt PDF, verification, and annual statement PDF.
- JWT registration/login/refresh/logout, bcryptjs password hashing, role checks, donor ownership checks, Zod validation, Helmet, and auth rate limiting.
- Admin dashboard, donor/campaign management, reports and CSV export, activity/audit feed.
- Donor dashboard, giving history and CSV, impact/badges, campaign saves/follows, preferences, notification controls, profile, support tickets, data export, session/activity review, and deletion requests.
- PostgreSQL Prisma schema, initial migration and donor-portal migration; explicit JSON demo store.
- Tests: 23 API integration cases and 3 client utility unit cases passed in the recorded run on 14 November 2026.

## Partially implemented or environment-dependent

- Email verification and password reset flows create short-lived tokens, but no mail provider is configured; production delivery requires integration.
- Account deletion is a request/review flow. Approval disables the account; automated anonymization and retention are not implemented.
- Admin deletion review and donor security flows are implemented in application logic but live database behavior depends on the deployed schema and migrations.
- The deployment configuration names Vercel, Render, and Neon. This audit does not certify current uptime or live database correctness.
- The JSON demo mode and Prisma production mode are alternate runtime paths; automated API tests exercise demo mode.

## Incorrect or outdated statements corrected

| Earlier documentation claim | Current evidence / correction |
| --- | --- |
| API base `/api/v1` | Routes are mounted under `/api`; Vercel rewrites `/api/*` to Render. |
| `Payment` model | Actual Prisma model is `PaymentAttempt`. |
| `targetAmount`, `collectedAmount`, `startDate`, `endDate` | Actual Campaign fields include `target`, `startsAt`, `endsAt`; raised totals are computed from successful donation records. |
| Receipt route `/receipts/my` and `/download` | Actual routes include `/receipts`, `/receipts/:id`, `/receipts/:id/pdf`, and `/receipt-verification/:receiptNumber`. |
| Profile routes as global GET/PUT `/profile` | Current donor self-service routes are `/donor/profile` with GET/PATCH; a general signed-in profile route also exists. |
| Reports have daily/weekly/monthly/yearly filters and under-500 ms response | Exact claims were unsupported; the code has report queries/exports but no measured latency objective or benchmark. |
| Email/SMS notifications, real payment gateway, or banking integration | No providers are configured; checkout and notification delivery are simulations/in-app only. |
| Every listed test case automated | Only the cases represented in `server/tests/api.test.js` and client tests are reported as executed. |

## Gaps in the original report

- Missing substantive contents, accurate field inventory for the current 22 Prisma models, deployment flow, and diagrams from actual schema/routes.
- Legacy ERD omitted donor-portal entities and used nonexistent model names.
- API table described hypothetical routes and an incorrect version prefix.
- Non-functional section included unmeasured performance figures.
- Screenshot section was an instruction to add screenshots; repository screenshot folder had no app captures at audit time.
- The report did not distinguish current implementation from planned real payments/email/MFA enhancements consistently.

## Not verified

- No migration apply or Prisma-backed end-to-end test was run against live Neon/PostgreSQL during this audit.
- No uptime/SLA, backup restore, load benchmark, independent accessibility audit, or payment compliance assessment was performed.
- No real payment or outbound email/SMS service was exercised.
