// factories/project.ts — Test Data Factory Pattern
// Uses faker for realistic, varied test data. Overrides for specific test scenarios.
import { faker } from '@faker-js/faker';
import type { Project } from '@/lib/types/project';

export const createProject = (overrides: Partial<Project> = {}): Project => ({
  id: faker.string.uuid(),
  name: faker.company.name(),
  address: faker.location.streetAddress(),
  type: faker.helpers.arrayElement(['residential', 'commercial', 'industrial', 'mixed_use']),
  status: faker.helpers.arrayElement(['draft', 'in_progress', 'submitted', 'approved', 'rejected']),
  documentCount: faker.number.int({ min: 0, max: 50 }),
  complianceProgress: faker.number.int({ min: 0, max: 100 }),
  createdAt: faker.date.recent().toISOString(),
  updatedAt: faker.date.recent().toISOString(),
  ...overrides,
});

export const createProjectList = (count: number, overrides?: Partial<Project>): Project[] =>
  Array.from({ length: count }, () => createProject(overrides));

// Specific scenario factories
export const createSubmittedProject = (overrides?: Partial<Project>) =>
  createProject({ status: 'submitted', complianceProgress: 100, ...overrides });

export const createDraftProject = (overrides?: Partial<Project>) =>
  createProject({ status: 'draft', complianceProgress: 0, ...overrides });

export const createLargeProject = (overrides?: Partial<Project>) =>
  createProject({ documentCount: 500, complianceProgress: 45, ...overrides });
