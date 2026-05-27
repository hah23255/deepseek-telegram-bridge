// mocks/server.ts — MSW Server Setup
// Import in vitest.setup.ts for automatic API mocking in all tests.
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// vitest.setup.ts should contain:
// import { server } from '@/test/mocks/server';
// beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
// afterEach(() => server.resetHandlers());
// afterAll(() => server.close());
