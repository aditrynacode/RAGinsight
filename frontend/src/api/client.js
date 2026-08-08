const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON, keep statusText
    }
    throw new Error(`${res.status} ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const askQuestion = (question) =>
  request("/ask", { method: "POST", body: JSON.stringify({ question }) });

export const submitFeedback = (queryId, rating, note) =>
  request("/feedback", {
    method: "POST",
    body: JSON.stringify({ query_id: queryId, rating, note: note || null }),
  });

export const listDiagnoses = () => request("/diagnoses");

export const getDiagnosis = (diagnosisId) => request(`/diagnoses/${diagnosisId}`);

export const applyFix = (diagnosisId, { targetDocumentId, referenceAnswer } = {}) =>
  request(`/diagnoses/${diagnosisId}/apply-fix`, {
    method: "POST",
    body: JSON.stringify({
      target_document_id: targetDocumentId ?? null,
      reference_answer: referenceAnswer ?? null,
    }),
  });

export const listExperiments = () => request("/experiments");

export const getSummary = () => request("/dashboard/summary");

export const getTimeline = () => request("/dashboard/timeline");

export const getFailureBreakdown = () => request("/dashboard/failures");

export const listDocuments = () => request("/documents");

export const getChunks = (documentId) => request(`/documents/${documentId}/chunks`);
