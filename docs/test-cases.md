# Test cases

The API test file uses Node's built-in test runner and Supertest. Run `npm test` after dependency installation. Tests use a fresh JSON demo store and remove it at teardown.

| ID | Scenario | Expected result |
| --- | --- | --- |
| AUTH-01 | Sign in with seeded admin credentials | 200, ADMIN role and access token |
| AUTH-02 | Sign in with incorrect password | 401; no token |
| AUTHZ-01 | Request admin dashboard without token | 401 |
| AUTHZ-02 | Donor requests admin-only resource | 403 |
| CAMP-01 | List active campaigns as guest | 200 with campaign records |
| CAMP-02 | Create campaign with admin bearer token | 201 and audit entry |
| DON-01 | Guest records successful anonymous donation | 201, SUCCEEDED and unique transaction reference |
| DON-02 | Guest records failed demo payment | 201, FAILED and no receipt |
| DON-03 | Submit zero amount | 400 validation failure |
| PAY-01 | Retry failed payment | Successful final state and receipt |
| REC-01 | Read receipt for successful donation | Printable receipt; owner/admin only |
| REP-01 | Download report export as admin | CSV content type and column header |
| DONOR-01 | Donor requests another donor's record | Forbidden / excluded by donor scope |
| AUD-01 | Admin changes campaign state | Audit event includes actor, entity and timestamp |

Current automated coverage includes health, admin login, public campaign list, successful anonymous donation and receipt, failed donation without receipt, admin dashboard authorization, CSV report export, and amount validation. The remaining rows are documented test cases but are not all automated. No test result should be inferred until the commands have been run successfully in an environment with installed dependencies.
