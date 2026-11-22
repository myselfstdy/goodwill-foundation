-- New donations default to INR. Existing Donation.currency values are intentionally preserved.
ALTER TABLE "Donation" ALTER COLUMN "currency" SET DEFAULT 'INR';
