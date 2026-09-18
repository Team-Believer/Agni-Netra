import { EventItem, EventDetail, DashboardSummary, TimelinePoint, DataSourceItem } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const getHeaders = (extraHeaders: Record<string, string> = {}) => {
  const headers: Record<string, string> = { ...extraHeaders };
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return headers;
};

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    cache: 'no-store',
    ...options,
    headers: getHeaders(options.headers as Record<string, string>)
  });

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('auth_unauthorized'));
    }
    throw new Error('Unauthorized');
  }

  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  try {
    return await fetchAPI('/dashboard/summary');
  } catch (err) {
    return {
      total_active: 0,
      high_priority: 0,
      under_verification: 0,
      resolved_24h: 0,
      total_events: 0,
      active_change_vs_yesterday: 0,
      high_priority_change: 0,
      under_verification_change: 0,
      resolved_change: 0,
      system_status: 'Offline',
      last_synced: new Date().toISOString()
    };
  }
}

export async function fetchEvents(params?: { status?: string; priority?: string; search?: string }): Promise<EventItem[]> {
  try {
    const query = new URLSearchParams();
    if (params?.status && params.status !== 'All') query.append('status', params.status);
    if (params?.priority && params.priority !== 'All') query.append('priority', params.priority);
    if (params?.search) query.append('search', params.search);
    
    const queryString = query.toString();
    return await fetchAPI(`/events${queryString ? '?' + queryString : ''}`);
  } catch (err) {
    return [];
  }
}

export async function fetchEventDetail(eventId: string): Promise<EventDetail | null> {
  try {
    return await fetchAPI(`/events/${eventId}`);
  } catch (err) {
    return null;
  }
}

export async function fetchEventTimeline(eventId: string): Promise<TimelinePoint[]> {
  try {
    return await fetchAPI(`/events/${eventId}/timeline`);
  } catch (err) {
    return [];
  }
}

export async function verifyEvent(
  eventId: string,
  payload: { decision: string; comment?: string; reviewer?: string }
): Promise<{ success: boolean; new_status?: string; error?: string }> {
  try {
    return await fetchAPI(`/events/${eventId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        decision: payload.decision,
        comment: payload.comment || 'Verified via analyst portal',
        reviewer: payload.reviewer || 'Ananya Sharma'
      })
    });
  } catch (err: any) {
    return { success: false, error: err?.message || 'Verification failed' };
  }
}

export async function fetchSources(): Promise<DataSourceItem[]> {
  try {
    return await fetchAPI('/sources');
  } catch (err) {
    return [];
  }
}

// --- Analytics API ---
export async function fetchAnalyticsEventsOverTime(): Promise<{ date: string; count: number }[]> {
  try {
    return await fetchAPI('/analytics/events-over-time');
  } catch (err) {
    return [];
  }
}

export async function fetchAnalyticsClassifications(): Promise<{ classification: string; count: number }[]> {
  try {
    return await fetchAPI('/analytics/classifications');
  } catch (err) {
    return [];
  }
}

export async function fetchAnalyticsPriorities(): Promise<{ priority: string; count: number }[]> {
  try {
    return await fetchAPI('/analytics/priorities');
  } catch (err) {
    return [];
  }
}

export async function fetchAnalyticsStatus(): Promise<{ status: string; count: number }[]> {
  try {
    return await fetchAPI('/analytics/status');
  } catch (err) {
    return [];
  }
}

export async function fetchAnalyticsEvidenceSources(): Promise<any[]> {
  try {
    return await fetchAPI('/analytics/evidence-sources');
  } catch (err) {
    return [];
  }
}

// --- Facilities API ---
export async function fetchFacilities(): Promise<any[]> {
  try {
    return await fetchAPI('/facilities');
  } catch (err) {
    return [];
  }
}

export async function fetchFacilityDetails(facilityId: string): Promise<any> {
  try {
    return await fetchAPI(`/facilities/${facilityId}`);
  } catch (err) {
    return null;
  }
}
