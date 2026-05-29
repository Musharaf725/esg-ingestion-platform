import { getRecentIngestionJobs } from "./ingestionApi";
import { getReviewRecords } from "./reviewApi";

async function fetchAllReviewRecords() {
  const records = [];
  let page = 1;
  const pageSize = 100;

  while (page <= 10) {
    const data = await getReviewRecords({ page, page_size: pageSize });
    const chunk = data?.results || [];
    records.push(...chunk);

    if (!data?.next || chunk.length < pageSize) break;
    page += 1;
  }

  return records;
}

export async function getDashboardData() {
  const [records, recentJobs] = await Promise.all([fetchAllReviewRecords(), getRecentIngestionJobs()]);

  const totals = {
    total: records.length,
    pendingReview: records.filter((r) => r.status === "pending_review").length,
    approved: records.filter((r) => r.status === "approved").length,
    rejected: records.filter((r) => r.status === "rejected").length,
    suspicious: records.filter((r) => (r.flag_reasons || []).length > 0).length,
    failedRows: recentJobs.reduce((sum, job) => sum + Number(job.failed || 0), 0),
  };

  const sourceBreakdown = ["sap", "utility", "travel"].map((source) => ({
    source,
    count: records.filter((r) => r.source_type === source).length,
  }));

  const suspiciousRecords = records
    .filter((r) => (r.flag_reasons || []).length > 0)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 8);

  return {
    totals,
    sourceBreakdown,
    suspiciousRecords,
    recentJobs: recentJobs.slice(0, 8),
  };
}
