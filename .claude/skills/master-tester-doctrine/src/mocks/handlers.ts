// mocks/handlers.ts — MSW Request Handlers
// Simulates GW2 compliance agent API endpoints.
// Pattern: Happy path first, then error scenarios.
import { http, HttpResponse, delay } from 'msw';
import { createProject, createProjectList } from '../factories/project';

const API_BASE = '/api';

export const handlers = [
  // ── Projects ──
  http.get(`${API_BASE}/projects`, async () => {
    await delay(100); // Realistic network latency
    return HttpResponse.json({
      success: true,
      data: createProjectList(5),
    });
  }),

  http.get(`${API_BASE}/projects/:id`, async ({ params }) => {
    await delay(50);
    return HttpResponse.json({
      success: true,
      data: createProject({ id: params.id as string }),
    });
  }),

  // ── Compliance Assessment ──
  http.post(`${API_BASE}/compliance/assess`, async () => {
    await delay(200); // Agent assessment takes time
    return HttpResponse.json({
      success: true,
      data: {
        assessment_id: 'GW2-001',
        compliance_status: 'compliant',
        evidence: ['fire_risk_assessment.pdf'],
        recommendations: ['Install additional smoke detectors'],
      },
    });
  }),

  // ── Error Scenarios (use server.use() to override in specific tests) ──

  // Network failure
  http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.error();
  }, { once: true }),

  // Server error
  http.post(`${API_BASE}/compliance/assess`, () => {
    return HttpResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }, { once: true }),

  // Slow response (for timeout testing)
  http.get(`${API_BASE}/projects/:id`, async () => {
    await delay(10000); // 10s delay
    return HttpResponse.json({ success: true, data: null });
  }, { once: true }),
];
