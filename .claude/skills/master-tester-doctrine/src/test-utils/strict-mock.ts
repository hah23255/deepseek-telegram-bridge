// test-utils/strict-mock.ts — Poison Pill Proxy
// Throws on ANY unmocked property access. Catches incomplete mocks instantly.
//
// Usage:
//   const user = createStrictMock<User>({ id: '1', name: 'Test' });
//   user.id  → '1'
//   user.email → throws: "unmocked property 'email'"

export function createStrictMock<T extends object>(overrides: Partial<T>): T {
  return new Proxy(overrides as T, {
    get(target, prop) {
      if (prop in target) {
        return (target as Record<string | symbol, unknown>)[prop];
      }
      throw new Error(
        `Test failed: Code attempted to access unmocked property '${String(prop)}'. ` +
        `Add it to the mock overrides or check if the code is reaching outside its expected bounds.`
      );
    },
  });
}
