CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE TYPE "Role" AS ENUM ('ADMIN', 'DONOR');
CREATE TYPE "CampaignStatus" AS ENUM ('DRAFT', 'ACTIVE', 'COMPLETED', 'PAUSED');
CREATE TYPE "DonationStatus" AS ENUM ('PENDING', 'SUCCEEDED', 'FAILED', 'REFUNDED');
CREATE TYPE "PaymentStatus" AS ENUM ('SUCCEEDED', 'FAILED');
CREATE TYPE "PaymentMethod" AS ENUM ('DEMO_CARD', 'DEMO_BANK');

CREATE TABLE "User" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "email" VARCHAR(255) NOT NULL, "passwordHash" VARCHAR(255) NOT NULL,
  "role" "Role" NOT NULL DEFAULT 'DONOR', "active" BOOLEAN NOT NULL DEFAULT true, "name" VARCHAR(160) NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL, CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
CREATE INDEX "User_role_idx" ON "User"("role");

CREATE TABLE "Donor" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "userId" UUID, "email" VARCHAR(255) NOT NULL, "name" VARCHAR(160) NOT NULL,
  "phone" VARCHAR(40), "address" VARCHAR(300), "anonymous" BOOLEAN NOT NULL DEFAULT false, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "Donor_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Donor_userId_key" ON "Donor"("userId");
CREATE INDEX "Donor_email_idx" ON "Donor"("email");
CREATE INDEX "Donor_name_idx" ON "Donor"("name");

CREATE TABLE "Campaign" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "title" VARCHAR(160) NOT NULL, "slug" VARCHAR(180) NOT NULL,
  "description" TEXT NOT NULL, "category" VARCHAR(80) NOT NULL, "target" DECIMAL(12,2) NOT NULL, "startsAt" TIMESTAMP(3) NOT NULL,
  "endsAt" TIMESTAMP(3) NOT NULL, "status" "CampaignStatus" NOT NULL DEFAULT 'DRAFT', "imageUrl" VARCHAR(500),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "Campaign_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Campaign_slug_key" ON "Campaign"("slug");
CREATE INDEX "Campaign_status_endsAt_idx" ON "Campaign"("status", "endsAt");

CREATE TABLE "Donation" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "campaignId" UUID NOT NULL, "donorId" UUID, "amount" DECIMAL(12,2) NOT NULL,
  "currency" CHAR(3) NOT NULL DEFAULT 'USD', "status" "DonationStatus" NOT NULL DEFAULT 'PENDING', "anonymous" BOOLEAN NOT NULL DEFAULT false,
  "idempotencyKey" VARCHAR(100), "transactionRef" VARCHAR(80), "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "Donation_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Donation_idempotencyKey_key" ON "Donation"("idempotencyKey");
CREATE UNIQUE INDEX "Donation_transactionRef_key" ON "Donation"("transactionRef");
CREATE INDEX "Donation_campaignId_status_idx" ON "Donation"("campaignId", "status");
CREATE INDEX "Donation_donorId_createdAt_idx" ON "Donation"("donorId", "createdAt");
CREATE INDEX "Donation_createdAt_idx" ON "Donation"("createdAt");

CREATE TABLE "PaymentAttempt" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "donationId" UUID NOT NULL, "attemptNumber" INTEGER NOT NULL,
  "status" "PaymentStatus" NOT NULL, "method" "PaymentMethod" NOT NULL DEFAULT 'DEMO_CARD', "reference" VARCHAR(80) NOT NULL, "message" VARCHAR(300),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "PaymentAttempt_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "PaymentAttempt_reference_key" ON "PaymentAttempt"("reference");
CREATE UNIQUE INDEX "PaymentAttempt_donationId_attemptNumber_key" ON "PaymentAttempt"("donationId", "attemptNumber");
CREATE INDEX "PaymentAttempt_createdAt_idx" ON "PaymentAttempt"("createdAt");

CREATE TABLE "Receipt" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "donationId" UUID NOT NULL, "receiptNumber" VARCHAR(80) NOT NULL,
  "issuedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT "Receipt_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Receipt_donationId_key" ON "Receipt"("donationId");
CREATE UNIQUE INDEX "Receipt_receiptNumber_key" ON "Receipt"("receiptNumber");

CREATE TABLE "AuditLog" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "userId" UUID, "action" VARCHAR(100) NOT NULL, "entity" VARCHAR(80) NOT NULL,
  "entityId" VARCHAR(80), "metadata" JSONB, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "AuditLog_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "AuditLog_createdAt_idx" ON "AuditLog"("createdAt");
CREATE INDEX "AuditLog_entity_entityId_idx" ON "AuditLog"("entity", "entityId");

CREATE TABLE "RefreshToken" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "userId" UUID NOT NULL, "tokenHash" VARCHAR(255) NOT NULL,
  "expiresAt" TIMESTAMP(3) NOT NULL, "revokedAt" TIMESTAMP(3), "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "RefreshToken_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "RefreshToken_tokenHash_key" ON "RefreshToken"("tokenHash");
CREATE INDEX "RefreshToken_userId_expiresAt_idx" ON "RefreshToken"("userId", "expiresAt");

CREATE TABLE "Notification" (
  "id" UUID NOT NULL DEFAULT gen_random_uuid(), "userId" UUID NOT NULL, "title" VARCHAR(160) NOT NULL,
  "message" VARCHAR(500) NOT NULL, "readAt" TIMESTAMP(3), "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "Notification_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "Notification_userId_readAt_createdAt_idx" ON "Notification"("userId", "readAt", "createdAt");

ALTER TABLE "Donor" ADD CONSTRAINT "Donor_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "Donation" ADD CONSTRAINT "Donation_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "Donation" ADD CONSTRAINT "Donation_donorId_fkey" FOREIGN KEY ("donorId") REFERENCES "Donor"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "PaymentAttempt" ADD CONSTRAINT "PaymentAttempt_donationId_fkey" FOREIGN KEY ("donationId") REFERENCES "Donation"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Receipt" ADD CONSTRAINT "Receipt_donationId_fkey" FOREIGN KEY ("donationId") REFERENCES "Donation"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "AuditLog" ADD CONSTRAINT "AuditLog_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "RefreshToken" ADD CONSTRAINT "RefreshToken_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "Notification" ADD CONSTRAINT "Notification_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
