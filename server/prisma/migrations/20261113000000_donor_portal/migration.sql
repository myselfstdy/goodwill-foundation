-- Donor self-service portal additions
ALTER TABLE "Notification" ADD COLUMN "category" VARCHAR(30) NOT NULL DEFAULT 'GENERAL';

ALTER TABLE "RefreshToken" ADD COLUMN "userAgent" VARCHAR(300), ADD COLUMN "ipAddress" VARCHAR(80);

ALTER TABLE "Donation" ADD COLUMN "message" VARCHAR(500);

ALTER TABLE "User" ADD COLUMN "avatarUrl" TEXT;

-- CreateTable
CREATE TABLE "DonorPreferences" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "preferredAmount" DECIMAL(12,2),
    "preferredCategory" VARCHAR(80),
    "anonymousDefault" BOOLEAN NOT NULL DEFAULT false,
    "paymentMethod" "PaymentMethod" NOT NULL DEFAULT 'DEMO_CARD',
    "privateProfile" BOOLEAN NOT NULL DEFAULT false,
    "donationMessage" VARCHAR(500),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "DonorPreferences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SavedCampaign" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "campaignId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "donorId" UUID,

    CONSTRAINT "SavedCampaign_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CampaignFollow" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "campaignId" UUID NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "donorId" UUID,

    CONSTRAINT "CampaignFollow_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "NotificationPreference" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "donationUpdates" BOOLEAN NOT NULL DEFAULT true,
    "receiptUpdates" BOOLEAN NOT NULL DEFAULT true,
    "campaignUpdates" BOOLEAN NOT NULL DEFAULT true,
    "securityAlerts" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "NotificationPreference_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AchievementBadge" (
    "id" UUID NOT NULL,
    "key" VARCHAR(60) NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "description" VARCHAR(300) NOT NULL,
    "criteria" JSONB NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "AchievementBadge_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DonorAchievement" (
    "id" UUID NOT NULL,
    "donorId" UUID NOT NULL,
    "badgeId" UUID NOT NULL,
    "awardedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "DonorAchievement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SupportTicket" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "subject" VARCHAR(180) NOT NULL,
    "category" VARCHAR(40) NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "SupportTicket_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "SupportTicketReply" (
    "id" UUID NOT NULL,
    "ticketId" UUID NOT NULL,
    "userId" UUID,
    "body" VARCHAR(3000) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "SupportTicketReply_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LoginActivity" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "action" VARCHAR(40) NOT NULL,
    "userAgent" VARCHAR(300),
    "ipAddress" VARCHAR(80),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "LoginActivity_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AccountDeletionRequest" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "reason" VARCHAR(500),
    "status" VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    "requestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolvedAt" TIMESTAMP(3),

    CONSTRAINT "AccountDeletionRequest_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CampaignUpdate" (
    "id" UUID NOT NULL,
    "campaignId" UUID NOT NULL,
    "title" VARCHAR(160) NOT NULL,
    "body" VARCHAR(3000) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "donorId" UUID,

    CONSTRAINT "CampaignUpdate_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DonorDashboardPreferences" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "preferences" JSONB NOT NULL DEFAULT '{}',

    CONSTRAINT "DonorDashboardPreferences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "EmailVerification" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "tokenHash" VARCHAR(64) NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "usedAt" TIMESTAMP(3),

    CONSTRAINT "EmailVerification_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PasswordReset" (
    "id" UUID NOT NULL,
    "userId" UUID NOT NULL,
    "tokenHash" VARCHAR(64) NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "usedAt" TIMESTAMP(3),

    CONSTRAINT "PasswordReset_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "DonorPreferences_userId_key" ON "DonorPreferences"("userId");

-- CreateIndex
CREATE INDEX "SavedCampaign_userId_createdAt_idx" ON "SavedCampaign"("userId", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "SavedCampaign_userId_campaignId_key" ON "SavedCampaign"("userId", "campaignId");

-- CreateIndex
CREATE INDEX "CampaignFollow_userId_createdAt_idx" ON "CampaignFollow"("userId", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "CampaignFollow_userId_campaignId_key" ON "CampaignFollow"("userId", "campaignId");

-- CreateIndex
CREATE UNIQUE INDEX "NotificationPreference_userId_key" ON "NotificationPreference"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "AchievementBadge_key_key" ON "AchievementBadge"("key");

-- CreateIndex
CREATE INDEX "DonorAchievement_donorId_awardedAt_idx" ON "DonorAchievement"("donorId", "awardedAt");

-- CreateIndex
CREATE UNIQUE INDEX "DonorAchievement_donorId_badgeId_key" ON "DonorAchievement"("donorId", "badgeId");

-- CreateIndex
CREATE INDEX "SupportTicket_userId_createdAt_idx" ON "SupportTicket"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "SupportTicketReply_ticketId_createdAt_idx" ON "SupportTicketReply"("ticketId", "createdAt");

-- CreateIndex
CREATE INDEX "LoginActivity_userId_createdAt_idx" ON "LoginActivity"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "AccountDeletionRequest_userId_status_idx" ON "AccountDeletionRequest"("userId", "status");

-- CreateIndex
CREATE INDEX "CampaignUpdate_campaignId_createdAt_idx" ON "CampaignUpdate"("campaignId", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "DonorDashboardPreferences_userId_key" ON "DonorDashboardPreferences"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "EmailVerification_tokenHash_key" ON "EmailVerification"("tokenHash");

-- CreateIndex
CREATE INDEX "EmailVerification_userId_expiresAt_idx" ON "EmailVerification"("userId", "expiresAt");

-- CreateIndex
CREATE UNIQUE INDEX "PasswordReset_tokenHash_key" ON "PasswordReset"("tokenHash");

-- CreateIndex
CREATE INDEX "PasswordReset_userId_expiresAt_idx" ON "PasswordReset"("userId", "expiresAt");

-- AddForeignKey
ALTER TABLE "DonorPreferences" ADD CONSTRAINT "DonorPreferences_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SavedCampaign" ADD CONSTRAINT "SavedCampaign_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SavedCampaign" ADD CONSTRAINT "SavedCampaign_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SavedCampaign" ADD CONSTRAINT "SavedCampaign_donorId_fkey" FOREIGN KEY ("donorId") REFERENCES "Donor"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CampaignFollow" ADD CONSTRAINT "CampaignFollow_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CampaignFollow" ADD CONSTRAINT "CampaignFollow_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CampaignFollow" ADD CONSTRAINT "CampaignFollow_donorId_fkey" FOREIGN KEY ("donorId") REFERENCES "Donor"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "NotificationPreference" ADD CONSTRAINT "NotificationPreference_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DonorAchievement" ADD CONSTRAINT "DonorAchievement_donorId_fkey" FOREIGN KEY ("donorId") REFERENCES "Donor"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DonorAchievement" ADD CONSTRAINT "DonorAchievement_badgeId_fkey" FOREIGN KEY ("badgeId") REFERENCES "AchievementBadge"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SupportTicket" ADD CONSTRAINT "SupportTicket_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SupportTicketReply" ADD CONSTRAINT "SupportTicketReply_ticketId_fkey" FOREIGN KEY ("ticketId") REFERENCES "SupportTicket"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SupportTicketReply" ADD CONSTRAINT "SupportTicketReply_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LoginActivity" ADD CONSTRAINT "LoginActivity_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AccountDeletionRequest" ADD CONSTRAINT "AccountDeletionRequest_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CampaignUpdate" ADD CONSTRAINT "CampaignUpdate_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CampaignUpdate" ADD CONSTRAINT "CampaignUpdate_donorId_fkey" FOREIGN KEY ("donorId") REFERENCES "Donor"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DonorDashboardPreferences" ADD CONSTRAINT "DonorDashboardPreferences_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "EmailVerification" ADD CONSTRAINT "EmailVerification_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PasswordReset" ADD CONSTRAINT "PasswordReset_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "User" ADD COLUMN "tokenVersion" INTEGER NOT NULL DEFAULT 0;
