// .dependency-cruiser.js — Architecture Boundary Enforcement
// Law 2: Test behaviour, not implementation.
// This config enforces architectural boundaries at the CI level.
//
// Install: npm install --save-dev dependency-cruiser
// Run: npx depcruise src --config .dependency-cruiser.js

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'no-circular-dependencies',
      severity: 'error',
      comment: 'Circular dependencies paralyze the codebase over time.',
      from: { path: 'src' },
      to: { path: 'src' },
      circular: true,
    },
    {
      name: 'agent-layer-isolation',
      severity: 'error',
      comment: 'Agent logic must not import from UI components.',
      from: { path: 'src/lib/agent' },
      to: { path: 'src/components' },
    },
    {
      name: 'data-layer-isolation',
      severity: 'error',
      comment: 'Data layer must not import from UI.',
      from: { path: 'src/lib/db' },
      to: { path: 'src/components' },
    },
    {
      name: 'no-test-utils-in-production',
      severity: 'error',
      comment: 'Test utilities must never be imported in production code.',
      from: { path: 'src/((?!__tests__|test-utils).)*' },
      to: { path: 'src/test-utils' },
    },
  ],
  options: {
    doNotFollow: {
      path: 'node_modules',
    },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: 'tsconfig.json' },
  },
};
