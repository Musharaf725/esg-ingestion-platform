import api from "./client";

export async function uploadIngestionFile({ file, sourceType, onUploadProgress }) {
  const form = new FormData();
  form.append("file", file);
  form.append("source_type", sourceType);

  const response = await api.post("/api/ingestion/upload/", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return response.data;
}

export async function getRecentIngestionJobs() {
  try {
    const response = await api.get("/api/ingestion/jobs/");
    const fromApi = response.data?.results || response.data || [];
    if (Array.isArray(fromApi) && fromApi.length) {
      return fromApi.map((job) => ({
        id: job.id,
        fileName: job.file_name,
        sourceType: job.source_type,
        total: job.records_total,
        saved: Math.max(0, Number(job.records_total || 0) - Number(job.records_failed || 0)),
        failed: job.records_failed,
        createdAt: job.uploaded_at,
        errors: job.error_log?.errors || [],
      }));
    }
  } catch {
    // Fallback to local cache for demo resilience.
  }

  const jobsRaw = localStorage.getItem("esg.recentJobs");
  if (!jobsRaw) return [];

  try {
    const jobs = JSON.parse(jobsRaw);
    return Array.isArray(jobs) ? jobs : [];
  } catch {
    return [];
  }
}

export function pushRecentIngestionJob(jobSummary) {
  const existing = localStorage.getItem("esg.recentJobs");
  let jobs = [];

  try {
    jobs = existing ? JSON.parse(existing) : [];
  } catch {
    jobs = [];
  }

  const next = [jobSummary, ...jobs].slice(0, 12);
  localStorage.setItem("esg.recentJobs", JSON.stringify(next));
}
