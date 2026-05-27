// vitest.config.ts — Master Tester Doctrine Configuration
// Drop-in Vitest config following the 10 non-negotiable laws.
import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    // Law 5: Isolated tests — no shared state
    globals: true,
    environment: 'jsdom',

    // Law 8: Deterministic — fake timers enforced by convention
    // Use vi.useFakeTimers() per test file, not globally (some libs need real timers)

    // Setup file for MSW + Testing Library
    setupFiles: ['./vitest.setup.ts'],

    // Coverage thresholds (enforce quality, not just metrics)
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/test-utils/**',
        'src/mocks/**',
        'src/factories/**',
        '**/*.test.*',
        '**/*.spec.*',
        '**/types/**',
      ],
      thresholds: {
        branches: 70,
        functions: 75,
        lines: 80,
        statements: 80,
      },
    },

    // Law 9: One concept per test — keep files focused
    // No test file should exceed 200 lines (enforced by code review)

    // CI-optimised settings
    pool: 'threads', // Better memory behaviour than forks
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },

    // Timeouts
    testTimeout: 10000,   // 10s per test
    hookTimeout: 10000,   // 10s for hooks
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/test': path.resolve(__dirname, './src/__tests__/helpers'),
    },
  },
});
