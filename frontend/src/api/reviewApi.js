import api from "./client";

export async function getReviewRecords(params) {
  const response = await api.get("/api/review/records/", { params });
  return response.data;
}

export async function approveRecord(recordId, note = "") {
  const response = await api.post(`/api/review/${recordId}/approve/`, { note });
  return response.data;
}

export async function rejectRecord(recordId, reason) {
  const response = await api.post(`/api/review/${recordId}/reject/`, { reason });
  return response.data;
}

export async function flagRecord(recordId, reason, note = "") {
  const response = await api.post(`/api/review/${recordId}/flag/`, { reason, note });
  return response.data;
}

export async function bulkApprove(recordIds, note = "") {
  const response = await api.post("/api/review/bulk-approve/", { record_ids: recordIds, note });
  return response.data;
}

export async function getAuditTrail(recordId) {
  try {
    const response = await api.get(`/api/review/records/${recordId}/audit/`);
    return response.data?.results || response.data || [];
  } catch {
    return [];
  }
}
