
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const email = 'VVITU@ac.in'.toLowerCase();
  const password = process.env.ADMIN_PASSWORD;

  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL is not configured.');
  }

 if (!password || password.length < 5) {
  throw new Error('Password must be at least 8 characters.');
}

  const passwordHash = await bcrypt.hash(password, 12);

  const admin = await prisma.user.upsert({
    where: { email },
    update: {
      name: 'Goodwill Foundation',
      passwordHash,
      role: 'ADMIN',
      active: true
    },
    create: {
      name: 'Goodwill Foundation',
      email,
      passwordHash,
      role: 'ADMIN',
      active: true
    },
    select: {
      email: true,
      role: true,
      active: true
    }
  });

  console.log('Admin account successfully created/updated:');
  console.log(admin);
}

main()
  .catch(error => {
    console.error('Admin setup failed:', error.message);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
