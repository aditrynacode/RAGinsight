import { useState } from "react";
import { categoryMeta } from "../categoryMeta";
import { applyFix } from "../api/client";
import "./DiagnosisPanel.css";

export default function DiagnosisPanel({ diagnosis, documentId }) {
  const [applying, setApplying] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const meta = categoryMeta(diagnosis.failure_category);
  const fix = diagnosis.proposed_fix || {};

  async function handleApply() {
    setApplying(true);
    setError(null);
    try {
      const res = await applyFix(diagnosis.id, { targetDocumentId: documentId });
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setApplying(false);
    }
  }

  return (
    <div className="diagnosis-panel">
      <div className="diagnosis-header">
        <span className="badge" style={{ borderColor: meta.color, color: meta.color }}>
          <span className="badge-dot" style={{ background: meta.color }} />
          {meta.label}
        </span>
        <span className="diagnosis-confidence">
          confidence {Math.round(diagnosis.diagnosis_confidence * 100)}%
        </span>
      </div>

      <p className="diagnosis-reasoning">{diagnosis.reasoning}</p>

      <div className="diagnosis-fix">
        <div className="eyebrow">Proposed fix — {fix.fix_type?.replaceAll("_", " ")}</div>
        <p>{fix.description}</p>
        {fix.target && <p className="diagnosis-fix-target">target: {fix.target}</p>}
        <div className="diagnosis-impact">
          expected impact: <strong>{diagnosis.expected_impact}</strong>
          {diagnosis.expected_impact_reasoning && ` — ${diagnosis.expected_impact_reasoning}`}
        </div>
      </div>

      {!result && (
        <button className="btn-primary" onClick={handleApply} disabled={applying}>
          {applying ? "Applying + re-testing…" : "Apply fix & re-test"}
        </button>
      )}

      {error && <div className="diagnosis-error">{error}</div>}

      {result && (
        <div className="diagnosis-result">
          <div className="score-compare">
            <div className="score-block">
              <div className="eyebrow">Before</div>
              <div className="score-value">{result.pre_score?.toFixed(2)}</div>
            </div>
            <div className="score-arrow">→</div>
            <div className="score-block">
              <div className="eyebrow">After</div>
              <div className="score-value" style={{ color: result.improved ? "var(--good)" : "var(--bad)" }}>
                {result.post_score?.toFixed(2)}
              </div>
            </div>
          </div>
          <div className={`score-verdict ${result.improved ? "good" : "bad"}`}>
            {result.improved ? "Score improved" : "No improvement — may need a different fix"}
          </div>
        </div>
      )}
    </div>
  );
}
