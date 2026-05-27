# The Unit Testing Rule Book
Here is a top 10 Unit Test Rule Book, built on industry best practices and directly addressing the lessons from the code reviews we just did. 

## 📖 The Unit Testing Rule Book

### 1. Test Behavior, Not Implementation Details
**The Rule:** Your tests should focus on *what* the code does (the outcome), not *how* it does it (the internal mechanics).
**Why:** If you test internal mechanics (like checking if a specific private variable changed, or testing the "shape" of an object like in your previous image), your tests become brittle. Every time you refactor the code to improve it without changing its output, your tests will break. Test the Public API.

### 2. Follow the AAA Pattern (Arrange, Act, Assert)
**The Rule:** Structure every test into three distinct visual sections:
*   **Arrange:** Set up the exact state, data, and mocks needed.
*   **Act:** Execute the single function or method you are testing.
*   **Assert:** Verify that the output or side effects are exactly what you expect.
**Why:** It makes tests incredibly easy to read. Another developer should be able to look at your test and instantly understand the setup, the trigger, and the expected result.

### 3. Tests Must Be Completely Isolated
**The Rule:** Test A should never depend on Test B. You should be able to run your test suite in completely random order, or run a single test in isolation, and always get the same result.
**Why:** Shared state (like a modified global variable or an uncleared database mock) causes "test leakage." This leads to tests that pass locally but fail in CI/CD, which destroys trust in the test suite. Always use `beforeEach` and `afterEach` to reset state.

### 4. Name Tests Like Bug Reports
**The Rule:** A failing test name should tell you exactly what is broken without you having to read the test code. Use the pattern: `FunctionName_StateUnderTest_ExpectedBehavior` or `it("should [do something] when [condition]")`.
*   *Bad:* `it("tests the login function")`
*   *Good:* `it("should return a 401 error when the password is empty")`
**Why:** When a pipeline fails with 50 broken tests, descriptive names let you instantly pinpoint the root cause.

### 5. Don't Over-Mock
**The Rule:** Only mock external dependencies (APIs, databases, file systems) or incredibly slow operations. Do not mock internal helper functions or data structures just for the sake of it.
**Why:** If you mock everything, you are no longer testing your application; you are just testing that your mocks work. (This relates to why simplifying the `vi.fn()` in your first image was a good idea—keep mocks simple).

### 6. DAMP over DRY (Descriptive And Meaningful Phrases)
**The Rule:** In production code, we use DRY (Don't Repeat Yourself). In test code, slight repetition is preferred if it makes the test easier to read from top to bottom. 
**Why:** If a developer has to scroll through three files and five nested helper functions just to understand what data is being passed into a test, the test is too complex. A little copy-pasting in tests is fine if it keeps the "Arrange" step explicit and readable.

### 7. Test One Logical Concept Per Test
**The Rule:** A single `it()` or `test()` block should test one specific behavior. This doesn't strictly mean "only one `expect()` statement," but all assertions should relate to the same action.
**Why:** If a test has 15 assertions checking 5 different behaviors, and the 2nd assertion fails, the test stops running. You have no idea if the other 3 behaviors are also broken. 

### 8. Test the Edges and the Errors (Negative Testing)
**The Rule:** Writing tests for the "Happy Path" (where everything goes right) is only 20% of the job. You must test nulls, undefined values, empty arrays, invalid inputs, and simulated network failures.
**Why:** The Happy Path rarely crashes your application in production. Edge cases and unhandled exceptions do. 

### 9. Tests Must Be Fast and Deterministic
**The Rule:** Unit tests should execute in milliseconds. They must never rely on network speed, actual API calls, or functions like `Math.random()` or `Date.now()` without mocking them.
**Why:** If a test suite takes 10 minutes to run, developers will stop running it before they commit. If a test randomly fails 1 out of 10 times (a "flaky test"), developers will start ignoring failures. 

### 10. Avoid Tautological Tests
**The Rule:** Never write a test that simply repeats the implementation logic or tests a fundamental language feature.
**Why:** (This is exactly why the code in your second image was deleted). Testing that an object has a property of `typeof "function"` provides zero value. Testing that `2 + 2 = 4` is a waste of time. Test the *business logic* of your app, not the mechanics of JavaScript.
