// test-utils/flush-promises.ts — Microtask Queue Flusher
// Forces the event loop to process all pending microtasks (Promise callbacks).
// Use when a component's state update is queued via Promises but timers aren't involved.
//
// Usage:
//   fireEvent.click(button);
//   await flushPromises();
//   expect(screen.getByText('Updated')).toBeInTheDocument();

export const flushPromises = () => new Promise<void>((resolve) => {
  setTimeout(resolve, 0);
});
