# User manual

## Visitors and donors

1. Open the home page and select **Explore our causes**. Search the campaign list by name or category.
2. Open a campaign to read its goal and description, then choose **Support this cause**.
3. Select a suggested amount or enter another amount. Provide a name and email; tick the anonymity option if you prefer the public record not to show your name.
4. The checkout is a demo. Leave the failed-payment checkbox off for a successful simulated gift, or select it to see a failure. No real payment occurs and card details are never requested.
5. Successful gifts display a receipt number. Use the printable receipt page's print control to save a PDF. Failed gifts have no receipt.
6. To save a personal donation history, create an account and give while signed in with the same email.

## Demo administrator

Sign in at `/login` with `VVITU@ac.in` and `VVITU@123`. The login form is blank and does not display account credentials. The dashboard shows successful totals, donor count, active campaign count, donation trend, campaign progress and recent gifts.

- **Donors:** search the list and review giving totals.
- **Campaigns:** create campaigns and pause them using the overflow action.
- **Donations / Receipts:** search records; open receipt links to print.
- **Reports:** inspect campaign totals and download CSV.
- **Activity:** review administrative events.
- **Settings:** update the signed-in display name.

## Reset and troubleshooting

Stop the development process and delete `server/data/demo.json` to restore the fictional seed data. If the API is unavailable, ensure port 4000 is free. If the web app cannot reach the API, start the root `npm run dev` command so the Vite `/api` proxy is active. PostgreSQL migrations need a running local or Neon database URL; the demo store does not need PostgreSQL.
