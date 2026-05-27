# Workflow Example — Brutal Critique → Master-Class Rewrite

> A complete end-to-end walk through the four-phase workflow on a realistic test file.

---

## The Inherited Test (Phase 0 — What We Started With)

```ts
// src/components/ProjectSubmit.test.tsx
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { ProjectSubmit } from './ProjectSubmit';

jest.mock('axios');

describe('ProjectSubmit', () => {
  let mockData: any;

  beforeAll(() => {
    mockData = { id: '1', status: 'draft' };
  });

  it('tests the submit button', async () => {
    (axios.post as any).mockResolvedValue({ data: mockData });
    const wrapper = render(<ProjectSubmit projectId="1" />);
    expect(typeof wrapper.container).toBe('object');

    const button = wrapper.container.querySelector('.btn-submit');
    fireEvent.click(button!);

    await waitFor(() => {
      expect((wrapper.container.querySelector('.status') as any).textContent).toContain('submitted');
    }, { timeout: 5000 });

    expect(axios.post).toHaveBeenCalled();
    expect(wrapper.container.innerHTML).toMatchSnapshot();
  });
});
```

---

## Phase 1 — The Brutal Critique

**Verdict.** This test does **not** guarantee production readiness. It produces a green check while proving close to nothing. Eleven distinct doctrine violations:

| # | Line                                                         | Violation                                                  | Rule |
|---|---------------------------------------------------------------|------------------------------------------------------------|------|
| 1 | `let mockData: any`                                          | Module-level mutable state + `any`                         | 5, 7 |
| 2 | `beforeAll(() => { mockData = ... })`                        | Shared state across tests                                  | 5    |
| 3 | `jest.mock('axios')`                                         | Mocking the HTTP client directly                           | 6    |
| 4 | `(axios.post as any).mockResolvedValue(...)`                 | `as any`                                                   | 7    |
| 5 | `it('tests the submit button', ...)`                         | Test name describes mechanics, not behavior                | 9    |
| 6 | `expect(typeof wrapper.container).toBe('object')`            | Tautology — tests JS, not business logic                   | 10   |
| 7 | `wrapper.container.querySelector('.btn-submit')`             | CSS-class selector, implementation coupling                | 2    |
| 8 | `await waitFor(..., { timeout: 5000 })`                       | `waitFor` instead of `findBy`; 5s timeout is a flake source | 8    |
| 9 | `.status as any`                                              | `as any` again                                             | 7    |
| 10| `expect(axios.post).toHaveBeenCalled()`                      | Asserts on the mock, not on the user-visible outcome        | 2    |
| 11| `toMatchSnapshot()` on `innerHTML`                            | Unreviewable 200-line snapshot                              | (snap discipline) |

The "test" passes whether or not the submit actually works, because every assertion is either tautological, mock-coupled, or against implementation details. Production deploys based on this test are gambling.

---

## Phase 2 — Strategic Realignment

What this component must prove, by behavior dimension:

| Dimension          | Behavior                                                                                        |
|--------------------|-------------------------------------------------------------------------------------------------|
| **Happy**          | User clicks Submit → backend receives the correct payload → UI shows the "Submitted" confirmation. |
| **Edge — empty**   | If the project has no required fields filled, Submit is disabled and shows the validation message. |
| **Edge — duplicate** | If user double-clicks Submit, only one request is sent.                                       |
| **Error — 4xx**    | If backend returns 400 with `{ field_errors: [...] }`, errors render inline next to the fields. |
| **Error — 5xx**    | If backend returns 500, a retry-able error toast appears; project status remains `draft`.       |
| **Error — network** | If `fetch` rejects (offline), an offline indicator appears; submit is re-triggerable when online. |
| **Race**           | If user clicks Submit, then navigates away mid-flight, the in-flight request is cancelled (AbortController). |
| **State**          | Successful submit transitions the local state to `submitted` and disables the Submit button.    |

Eight behaviors, eight tests.

---

## Phase 3 — The Master-Class Rewrite

```ts
// src/components/ProjectSubmit.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse, delay } from 'msw';
import { createProject, createDraftProject } from '@/test/factories/project';
import { server } from '@/test/mocks/server';
import { ProjectSubmit } from './ProjectSubmit';

describe('ProjectSubmit', () => {
  describe('happy path', () => {
    it('submits the project and shows confirmation when the user clicks Submit', async () => {
      // ARRANGE
      const project = createDraftProject({ id: 'proj_123', complianceProgress: 100 });
      let receivedBody: unknown = null;
      server.use(
        http.post('/api/projects/:id/submit', async ({ request }) => {
          receivedBody = await request.json();
          return HttpResponse.json({ success: true, data: { ...project, status: 'submitted' } });
        }),
      );
      const user = userEvent.setup();
      render(<ProjectSubmit project={project} />);

      // ACT
      await user.click(screen.getByRole('button', { name: /submit/i }));

      // ASSERT
      expect(await screen.findByRole('status', { name: /submitted/i })).toBeVisible();
      expect(receivedBody).toEqual({ projectId: 'proj_123' });
      expect(screen.getByRole('button', { name: /submit/i })).toBeDisabled();
    });
  });

  describe('validation', () => {
    it('disables Submit and shows guidance when required fields are incomplete', () => {
      // ARRANGE
      const incomplete = createDraftProject({ complianceProgress: 50 });

      // ACT
      render(<ProjectSubmit project={incomplete} />);

      // ASSERT
      expect(screen.getByRole('button', { name: /submit/i })).toBeDisabled();
      expect(screen.getByText(/complete required fields/i)).toBeVisible();
    });
  });

  describe('idempotency', () => {
    it('sends only one request when the user double-clicks Submit', async () => {
      // ARRANGE
      const project = createDraftProject({ complianceProgress: 100 });
      let callCount = 0;
      server.use(
        http.post('/api/projects/:id/submit', async () => {
          callCount += 1;
          await delay(100);
          return HttpResponse.json({ success: true, data: { ...project, status: 'submitted' } });
        }),
      );
      const user = userEvent.setup();
      render(<ProjectSubmit project={project} />);

      // ACT
      const button = screen.getByRole('button', { name: /submit/i });
      await user.dblClick(button);

      // ASSERT
      expect(await screen.findByRole('status', { name: /submitted/i })).toBeVisible();
      expect(callCount).toBe(1);
    });
  });

  describe('error: validation 4xx', () => {
    it('renders field errors inline when the backend returns 400 with field_errors', async () => {
      // ARRANGE
      const project = createDraftProject({ complianceProgress: 100 });
      server.use(
        http.post('/api/projects/:id/submit', () =>
          HttpResponse.json(
            { success: false, field_errors: [{ field: 'address', message: 'Required' }] },
            { status: 400 },
          ),
        ),
      );
      const user = userEvent.setup();
      render(<ProjectSubmit project={project} />);

      // ACT
      await user.click(screen.getByRole('button', { name: /submit/i }));

      // ASSERT
      expect(await screen.findByText(/address: required/i)).toBeVisible();
      expect(screen.getByRole('button', { name: /submit/i })).toBeEnabled();
    });
  });

  describe('error: server 5xx', () => {
    it('shows a retry-able toast and keeps status draft when the backend returns 500', async () => {
      // ARRANGE
      const project = createDraftProject({ complianceProgress: 100 });
      server.use(
        http.post('/api/projects/:id/submit', () =>
          HttpResponse.json({ success: false, error: 'Service unavailable' }, { status: 500 }),
        ),
      );
      const user = userEvent.setup();
      render(<ProjectSubmit project={project} />);

      // ACT
      await user.click(screen.getByRole('button', { name: /submit/i }));

      // ASSERT
      expect(await screen.findByRole('alert', { name: /something went wrong/i })).toBeVisible();
      expect(screen.getByRole('button', { name: /retry/i })).toBeVisible();
    });
  });

  describe('error: network', () => {
    it('shows an offline indicator when fetch rejects', async () => {
      // ARRANGE
      const project = createDraftProject({ complianceProgress: 100 });
      server.use(http.post('/api/projects/:id/submit', () => HttpResponse.error()));
      const user = userEvent.setup();
      render(<ProjectSubmit project={project} />);

      // ACT
      await user.click(screen.getByRole('button', { name: /submit/i }));

      // ASSERT
      expect(await screen.findByRole('status', { name: /offline/i })).toBeVisible();
    });
  });

  describe('race: navigation cancels in-flight request', () => {
    it('aborts the request when the component unmounts before the response', async () => {
      // ARRANGE
      const project = createDraftProject({ complianceProgress: 100 });
      let wasAborted = false;
      server.use(
        http.post('/api/projects/:id/submit', async ({ request }) => {
          request.signal.addEventListener('abort', () => { wasAborted = true; });
          await delay(1000);
          return HttpResponse.json({ success: true });
        }),
      );
      const user = userEvent.setup();
      const { unmount } = render(<ProjectSubmit project={project} />);

      // ACT
      await user.click(screen.getByRole('button', { name: /submit/i }));
      unmount();

      // ASSERT
      await screen.findByText(/.*/); // flush microtasks
      expect(wasAborted).toBe(true);
    });
  });
});
```

---

## Phase 4 — Defense Of The Architecture

**Why this suite guarantees deployment readiness.**

1. **Every assertion targets user-visible state.** No mock is asserted on directly. No internal state is read. The suite proves what the user actually experiences.
2. **The error matrix is complete.** Happy + validation + idempotency + 4xx + 5xx + network + race. Each is its own named test; a failure tells you exactly what is broken.
3. **The HTTP boundary is real.** MSW intercepts at the network level. The component's `fetch`/retry/abort logic runs unchanged from production.
4. **The test names are bug reports.** A CI failure named `"renders field errors inline when the backend returns 400 with field_errors"` tells the reader the regression without opening the file.

**How this suite survives the next refactor.**

- The button is queried by ARIA role (`name: /submit/i`), not by CSS class. Restyling does not break tests.
- The submitted state is queried by `role: 'status'`, not by container structure. Re-architecting the layout does not break tests.
- The backend contract is asserted at the request body level. Swapping `fetch` for `axios`, or `axios` for React Query, does not break tests.

**Where mutation testing should pay attention.**

- The `complianceProgress === 100` gating logic in `ProjectSubmit`. Mutation flipping `===` to `!==` or the threshold `100` to `0` should be caught by the "validation" test.
- The `AbortController.abort()` call on unmount. Removing it should be caught by the "race" test (the `wasAborted` assertion).
- The double-click guard. Removing it should be caught by the "idempotency" test (`callCount` would rise to 2).

**Explicit gaps and risk acceptance.**

- Visual regression of the toast / status indicator: not covered here; covered separately by a visual-regression suite in Playwright.
- Server-side validation rules: not covered here; covered in the backend's own test suite.

This is a suite I would stake the production deployment on. That is the only metric that matters.
