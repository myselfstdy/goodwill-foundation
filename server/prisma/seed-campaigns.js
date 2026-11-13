
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';

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
  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL is missing');
  }

  for (const [title, slug, description, category, target] of campaigns) {
    await prisma.campaign.upsert({
      where: { slug },
      update: {
        title,
        description,
        category,
        target,
        status: 'ACTIVE',
        startsAt: day(-30),
        endsAt: day(90)
      },
      create: {
        title,
        slug,
        description,
        category,
        target,
        startsAt: day(-30),
        endsAt: day(90),
        status: 'ACTIVE'
      }
    });

    console.log(`Campaign ready: ${title}`);
  }

  console.log('Successfully added all 6 active campaigns.');
} catch (error) {
  console.error('Campaign seeding failed:', error);
  process.exitCode = 1;
} finally {
  await prisma.$disconnect();
}
