import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();
const today = new Date();
const day = n => new Date(today.getTime() + n * 86400000);
const campaigns = [
  ['Clean Water for All', 'clean-water-for-all', 'Bring safe, reliable drinking water to rural communities through wells, filtration and local stewardship.', 'Water', 50000],
  ['Learning Without Limits', 'learning-without-limits', 'Equip children with books, classroom materials and the support to stay curious.', 'Education', 35000],
  ['Community Health Access', 'community-health-access', 'Make essential health screenings and care accessible to families who need them most.', 'Health', 40000],
  ['A Greener Tomorrow', 'a-greener-tomorrow', 'Restore native habitats and grow resilient, greener neighborhoods together.', 'Environment', 28000],
  ['Meals That Matter', 'meals-that-matter', 'Connect local kitchens and volunteers to families facing food insecurity.', 'Food security', 22000],
  ['Safe Homes Initiative', 'safe-homes-initiative', 'Help families rebuild safe, stable homes after severe storms.', 'Housing', 60000]
];
try {
  const adminHash = await bcrypt.hash('DemoAdmin!23', 10);
  const admin = await prisma.user.upsert({ where: { email: 'admin@goodwill.demo' }, update: {}, create: { name: 'Alex Morgan', email: 'admin@goodwill.demo', passwordHash: adminHash, role: 'ADMIN' } });
  const rows = [];
  for (const [title, slug, description, category, target] of campaigns) rows.push(await prisma.campaign.upsert({ where: { slug }, update: {}, create: { title, slug, description, category, target, startsAt: day(-30), endsAt: day(90), status: slug === 'safe-homes-initiative' ? 'PAUSED' : 'ACTIVE' } }));
  const people = [['Amara Johnson','amara@example.org'],['Ethan Chen','ethan@example.org'],['Sofia Patel','sofia@example.org'],['Noah Williams','noah@example.org'],['Grace Kim','grace@example.org'],['Oliver Brooks','oliver@example.org']];
  const donors = [];
  for (const [name,email] of people) {
    const user = await prisma.user.upsert({ where:{email}, update:{}, create:{name,email,passwordHash:await bcrypt.hash('DonorDemo!23',10),role:'DONOR'} });
    await prisma.donorPreferences.upsert({where:{userId:user.id},update:{},create:{userId:user.id}});
    await prisma.notificationPreference.upsert({where:{userId:user.id},update:{},create:{userId:user.id}});
    donors.push(await prisma.donor.upsert({ where:{userId:user.id}, update:{}, create:{userId:user.id,name,email} }));
  }
  const badges = [
    ['first_donation','First Donation','Record your first successful demo gift.',{successfulDonations:1}],
    ['regular_supporter','Regular Supporter','Complete five successful demo donations.',{successfulDonations:5}],
    ['generous_contributor','Generous Contributor','Contribute at least $5,000 in successful demo gifts.',{totalGivenUsd:5000}],
    ['campaign_champion','Campaign Champion','Support at least three unique campaigns successfully.',{campaignsSupported:3}],
    ['goodwill_supporter','Goodwill Supporter','Contribute at least $100 in successful demo gifts.',{totalGivenUsd:100}]
  ];
  for (const [key,name,description,criteria] of badges) await prisma.achievementBadge.upsert({where:{key},update:{name,description,criteria,active:true},create:{key,name,description,criteria}});
  const existing = await prisma.donation.count();
  if (!existing) for (let i=0;i<donors.length;i++) for(let n=0;n<2;n++) {
    const failed=i===2&&n===1; const donation=await prisma.donation.create({data:{campaignId:rows[(i+n)%rows.length].id,donorId:donors[i].id,amount:[125,250,75,500,100,175][(i+n)%6],status:failed?'FAILED':'SUCCEEDED',transactionRef:`SEED-${41001+i*2+n}`,createdAt:day(-i*4-n)}});
    await prisma.paymentAttempt.create({data:{donationId:donation.id,attemptNumber:1,status:failed?'FAILED':'SUCCEEDED',reference:`SEED-ATT-${51001+i*2+n}`}});
    if(!failed) await prisma.receipt.create({data:{donationId:donation.id,receiptNumber:`RCP-${today.getFullYear()}-${1001+i*2+n}`}});
  }
  const seededAudit=await prisma.auditLog.findFirst({where:{userId:admin.id,action:'DEMO_DATA_SEEDED',entity:'System'}});
  if(!seededAudit) await prisma.auditLog.create({data:{userId:admin.id,action:'DEMO_DATA_SEEDED',entity:'System',metadata:{fictional:true}}});
  console.log('Seeded demo administrator, donors, campaigns, donation attempts, receipts and audit log.');
} finally { await prisma.$disconnect(); }
