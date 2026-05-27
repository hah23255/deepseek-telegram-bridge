# Master Tester Doctrine — Patterns Reference

## AAA Pattern (Law 3)

```typescript
it('should return assessment when project exists', async () => {
  // ARRANGE
  const project = createProject({ id: 'proj_001' });
  server.use(
    http.get('/api/projects/:id', () => HttpResponse.json({ success: true, data: project }))
  );

  // ACT
  render(<AssessmentPage projectId="proj_001" />);
  const result = await screen.findByTestId('assessment-result');

  // ASSERT
  expect(result).toHaveTextContent('Compliance Status');
});
```

## Factory Pattern (Law 4 — DAMP)

```typescript
// Instead of:
const project = { id: '1', name: 'Test', address: '123 Main', type: 'residential', 
  status: 'draft', documentCount: 0, complianceProgress: 0, 
  createdAt: '2026-01-01', updatedAt: '2026-01-01' };

// Use:
const project = createProject({ status: 'draft' });
const submitted = createSubmittedProject();
```

## MSW Handler Pattern (Law 6)

```typescript
// In test file, override specific handler for error scenario:
it('shows error when assessment fails', async () => {
  server.use(
    http.post('/api/compliance/assess', () => 
      HttpResponse.json({ error: 'Service unavailable' }, { status: 503 }),
      { once: true }  // Only for this test
    )
  );
  // ... test error UI
});
```

## Strict Mock Pattern (Law 7)

```typescript
// Instead of:
const mock = { id: '1' } as any;

// Use:
const mock = createStrictMock<Project>({ id: '1', name: 'Test' });
// mock.email → throws: "unmocked property 'email'"
```

## Property-Based Testing (Advanced)

```typescript
import { test, fc } from '@fast-check/vitest';

test.prop([fc.string(), fc.integer({ min: 0, max: 100 })])(
  'compliance progress is always within 0-100',
  (projectName, progress) => {
    const project = createProject({ name: projectName, complianceProgress: progress });
    expect(project.complianceProgress).toBeGreaterThanOrEqual(0);
    expect(project.complianceProgress).toBeLessThanOrEqual(100);
  }
);
```

## Race Condition Testing (Advanced)

```typescript
it('shows latest search results when requests resolve out of order', async () => {
  server.use(
    http.get('/api/search', async ({ request }) => {
      const q = new URL(request.url).searchParams.get('q');
      if (q === 'a') { await delay(1000); return HttpResponse.json(['Apple']); }
      return HttpResponse.json(['Absolute']);
    })
  );

  const { user } = render(<SearchPage />);
  await user.type(screen.getByRole('searchbox'), 'a');
  await user.type(screen.getByRole('searchbox'), 'ab');
  
  await screen.findByText('Absolute');
  expect(screen.queryByText('Apple')).not.toBeInTheDocument();
});
```

## Suspense Testing (Advanced)

```typescript
it('shows loading spinner then content', async () => {
  const { promise, resolve } = createDeferred<Project[]>();

  render(
    <Suspense fallback={<Spinner />}>
      <ProjectList dataPromise={promise} />
    </Suspense>
  );

  expect(screen.getByTestId('spinner')).toBeInTheDocument();
  resolve([createProject()]);
  await screen.findByTestId('project-list');
  expect(screen.queryByTestId('spinner')).not.toBeInTheDocument();
});
```

## Architecture Boundary Test (Advanced)

```typescript
// tests/architecture/boundaries.test.ts
import { describe, it, expect } from 'vitest';
import { cruise } from 'dependency-cruiser';

describe('architecture boundaries', () => {
  it('agent layer never imports from components', async () => {
    const result = await cruise(['src/lib/agent'], {
      forbid: { from: { path: 'src/lib/agent' }, to: { path: 'src/components' } }
    });
    expect(result.summary.violations).toBe(0);
  });
});
```
