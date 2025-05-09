// Prisma client implementation
import { PrismaClient } from '@prisma/client';

// Set up global instance to prevent multiple instances during development
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

// Use existing Prisma instance or create a new one
export const prisma = globalForPrisma.prisma ?? new PrismaClient();

// In development, attach to global object to prevent multiple instances
if (process.env.NODE_ENV !== &apos;production&apos;) {
  globalForPrisma.prisma = prisma;
} 