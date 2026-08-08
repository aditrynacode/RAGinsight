import "./StatCards.css";

export default function StatCards({ summary }) {
  if (!summary) return null;

  const cards = [
    { label: "Queries logged", value: summary.total_queries },
    { label: "Diagnoses run", value: summary.total_diagnoses },
    { label: "Fixes tested", value: summary.total_experiments },
    {
      label: "Avg eval score",
      value: summary.average_eval_score != null ? summary.average_eval_score.toFixed(2) : "—",
    },
    { label: "Fixes that improved score", value: summary.experiments_that_improved },
  ];

  return (
    <div className="stat-row">
      {cards.map((c) => (
        <div className="stat-card panel" key={c.label}>
          <div className="stat-value">{c.value}</div>
          <div className="eyebrow">{c.label}</div>
        </div>
      ))}
    </div>
  );
}
