export const CATEGORY_META = {
  RETRIEVAL_MISS: { label: "Retrieval miss", color: "var(--cat-retrieval)" },
  CHUNKING_PROBLEM: { label: "Chunking problem", color: "var(--cat-chunking)" },
  AMBIGUOUS_QUERY: { label: "Ambiguous query", color: "var(--cat-ambiguous)" },
  GENERATION_ERROR: { label: "Generation error", color: "var(--cat-generation)" },
  NO_INFORMATION: { label: "No information", color: "var(--cat-noinfo)" },
};

export function categoryMeta(category) {
  return CATEGORY_META[category] || { label: category || "Unknown", color: "var(--text-dim)" };
}
