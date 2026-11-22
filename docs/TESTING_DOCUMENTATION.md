# Testing documentation

## Commands executed

| Command | Result |
| --- | --- |
| `npm run test --workspace server` (part of root run) | 23 API tests passed, 0 failed |
| `npm run test --workspace client` (part of root run) | 3 client tests passed, 0 failed |
| `npm test` | Completed successfully; 26 tests total |

**Execution date:** 14 November 2026. The tests were run in the project workspace. A first sandbox-restricted attempt could not open local loopback test servers; the successful rerun used the permitted local test-server access. No claim is made from the failed attempt.

## API coverage recorded

The Node test runner and Supertest exercise health mode, admin authentication, public campaign listing, successful/failed donations, receipt rules, idempotency, donor registration, successful-only totals, filtering and CSV, guest donation privacy, campaign save/follow, donor preferences and notification controls, PDF receipt/verification privacy, support tickets, annual statements and data export, administrator support responses, deletion request review, password recovery/session revocation, campaign administration, payment retry, authorization, report CSV, and amount validation.

## Client coverage recorded

Vitest runs `client/src/money.test.js` (3 cases). This suite checks the client money helper; it is not an end-to-end visual-browser test.

## Not run

- Prisma migration application against a live or disposable PostgreSQL database.
- Database-mode endpoint integration tests against Neon.
- Load/performance, backup/restore, accessibility, or payment-provider certification.
- Automated screenshot or cross-browser test suite.

The production build was run during the prior branding work; it is not a test suite result. See the README for current build instructions.
