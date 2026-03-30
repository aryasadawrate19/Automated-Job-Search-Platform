const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(`API Error ${status}`);
    this.status = status;
    this.data = data;
  }
}

async function apiFetch<T = any>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...fetchOpts } = options;

  let url = `${API_BASE}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const res = await fetch(url, {
    ...fetchOpts,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOpts.headers,
    },
  });

  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new ApiError(res.status, data);
  }

  return res.json();
}

export const api = {
  // Users
  register: (data: { email: string }) =>
    apiFetch('/api/users/register', { method: 'POST', body: JSON.stringify(data) }),

  uploadResume: (formData: FormData) =>
    apiFetch('/api/users/resume', {
      method: 'POST',
      body: formData,
      headers: {}, // let browser set content-type for multipart
    }),

  getProfile: (userId: string) =>
    apiFetch(`/api/users/${userId}/profile`),

  // Jobs
  getJobs: (params?: Record<string, string>) =>
    apiFetch('/api/jobs', { params }),

  getJob: (jobId: string) =>
    apiFetch(`/api/jobs/${jobId}`),

  // Matches
  getMatches: (userId: string) =>
    apiFetch(`/api/matches/${userId}`),

  getMatchDetail: (userId: string, jobId: string) =>
    apiFetch(`/api/matches/${userId}/${jobId}`),

  // Assist
  generateCoverLetter: async function* (jobId: string, userId: string) {
    const res = await fetch(`${API_BASE}/api/assist/cover-letter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, user_id: userId }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => null);
      throw new ApiError(res.status, data);
    }

    const reader = res.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  },

  getResumeTips: (jobId: string, userId: string) =>
    apiFetch('/api/assist/resume-tips', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId, user_id: userId }),
    }),

  // Settings
  saveApiKey: (provider: string, key: string) =>
    apiFetch(`/api/settings/${provider}-key`, {
      method: 'POST',
      body: JSON.stringify({ api_key: key }),
    }),

  setAiProvider: (provider: string) =>
    apiFetch('/api/settings/ai-provider', {
      method: 'POST',
      body: JSON.stringify({ ai_provider: provider }),
    }),
};

export { ApiError };
export default api;
