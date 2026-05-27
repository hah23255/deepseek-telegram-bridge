// test-utils/deferred.ts — Suspense Testing Utility
// Creates a Promise you can resolve/reject on demand for deterministic Suspense testing.
//
// Usage:
//   const { promise, resolve, reject } = createDeferred<string>();
//   render(<Suspense fallback={<Spinner />}><AsyncComponent dataPromise={promise} /></Suspense>);
//   expect(screen.getByText('Loading...')).toBeInTheDocument();
//   resolve('data loaded');
//   await screen.findByText('data loaded');

export function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}
