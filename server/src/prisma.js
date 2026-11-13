import { PrismaClient } from '@prisma/client';

const key = Symbol.for('goodwill.prisma');
export const prisma = globalThis[key] ?? new PrismaClient({ log: process.env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'] });
if (process.env.NODE_ENV !== 'production') globalThis[key] = prisma;
