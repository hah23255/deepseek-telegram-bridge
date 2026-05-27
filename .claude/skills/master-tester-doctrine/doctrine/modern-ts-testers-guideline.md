Here is the **Modern TypeScript Tester’s Guideline & Bible**.

---

## 📖 Book I: The TypeScript Philosophy

### 1. The Compiler is Your First Test
Never write a unit test to verify something TypeScript already guarantees. If TS ensures a function takes a `string` and returns a `number`, do not write a runtime test checking `typeof result === 'number'`. Trust the compiler. Reserve unit tests for *business logic* and *runtime behavior*.

### 2. Ban `as any` in Test Files
It is tempting to use `as any` or `as unknown as...` (like in your second screenshot) to quickly bypass type errors when mocking complex objects. **Don't.**
*   **The Fix:** Use the `satisfies` operator or `Partial<T>`. 
*   **Why:** If the real interface changes, `as any` will silently pass, hiding a broken test. `satisfies` enforces the shape of the properties you *do* provide, while allowing you to omit the rest.

### 3. Type-Safe Mocking is Mandatory
If you are using Jest or Vitest, ensure your mocks retain their original function signatures.
*   *Bad:* `const myMock = vi.fn();` (Loses type context)
*   *Good:* `const myMock = vi.mocked(originalFunction);` (Now TS knows exactly what arguments `myMock` accepts and what it returns).

---

## 📖 Book II: The Modern Testing Trophy (Integration over Unit)

### 4. Shift Towards Integration Tests
The old "Test Pyramid" demanded thousands of isolated unit tests. The modern **"Testing Trophy"** (championed by Kent C. Dodds) argues that **Integration Tests** provide the highest return on investment.
*   Don't just test a button component in isolation. Test the form it lives in.
*   Don't just test the API fetcher. Test the React Hook that calls the fetcher and updates the state.

### 5. Test Software the Way Users Use It
If you are testing UI (using React Testing Library), never assert on internal state. 
*   *Bad:* `expect(wrapper.state('isOpen')).toBe(true)`
*   *Good:* `expect(screen.getByRole('dialog')).toBeVisible()`
Users don't care about your boolean variables; they care about what they can see and interact with.

### 6. Query by Accessibility (a11y)
When selecting elements in a UI test, prioritize accessibility roles over test IDs.
1.  `getByRole` (Best: proves the app is accessible to screen readers)
2.  `getByText` / `getByLabelText` (Good: tests what the user actually reads)
3.  `getByTestId` (Last resort: tightly couples test to implementation)

---

## 📖 Book III: Mastering Mocks & Network

### 7. Stop Mocking `fetch` or `axios` Directly
Mocking HTTP clients leads to brittle tests that leak implementation details. 
*   **The Standard:** Use **MSW (Mock Service Worker)**. 
*   **Why:** MSW intercepts network requests at the Node/Browser level. Your code runs exactly as it would in production, but MSW returns mock JSON. It is completely agnostic to whether you use `fetch`, `axios`, or React Query.

### 8. "Don't Mock What You Don't Own"
Only mock external boundaries (APIs, WebSockets, LocalStorage, third-party libraries like Stripe). Do not mock your own internal helper functions just to isolate a test, unless that helper is doing something incredibly slow or non-deterministic (like generating a UUID).

### 9. Clear, Reset, and Restore
Test pollution is the #1 cause of flaky CI pipelines.
*   `vi.clearAllMocks()`: Clears call history (`toHaveBeenCalledTimes`). Run before every test.
*   `vi.resetAllMocks()`: Clears history AND removes mocked return values.
*   `vi.restoreAllMocks()`: Destroys the mock entirely and puts the original function back. Use this if you mutated a global object.

---

## 📖 Book IV: Architecture & Maintenance

### 10. Use the Object Mother / Factory Pattern for Test Data
In TypeScript, objects can be massive. Hardcoding a 50-property `User` object in every test is a nightmare.
*   **The Rule:** Create Test Data Builders or use libraries like `fishery`.
```typescript
// Instead of this in every test:
const user = { id: 1, name: "John", role: "ADMIN", createdAt: "...", /* 40 more props */ };

// Do this:
const user = buildMockUser({ role: "ADMIN" }); // Factory fills in the rest with valid defaults
```

### 11. Avoid `waitFor` When `findBy` Exists
In React Testing Library, `waitFor` is a blunt instrument. 
*   *Bad:* `await waitFor(() => expect(screen.getByText('Loaded')).toBeInTheDocument());`
*   *Good:* `await screen.findByText('Loaded');`
`findBy` is a built-in async wrapper that handles the retry logic elegantly and provides better error messages.

### 12. Treat Test Code as Production Code
Tests are not second-class citizens. 
*   They must be linted.
*   They must be strongly typed.
*   They must be refactored when they get messy.
If your test file is a spaghetti mess of nested `describe` blocks and shared mutable `let` variables, your team will stop writing tests because the friction is too high. 

## 💡 The Golden Rule Summary
**"Write tests. Not too many. Mostly integration."** 
A modern TypeScript tester relies on the compiler to catch structural errors, relies on tools like MSW to handle the network, and writes tests that verify the *actual outcome* of a user's action or a system's process.
