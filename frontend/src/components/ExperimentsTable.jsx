import "./ExperimentsTable.css";

export default function ExperimentsTable({ experiments }) {
  return (
    <div className="panel experiments-panel">
      <div className="eyebrow">Experiments log</div>

      {!experiments?.length ? (
        <p className="experiments-empty">
          No fixes applied yet — apply a fix from the Chat view's diagnosis panel to log one here.
        </p>
      ) : (
        <table className="experiments-table">
          <thead>
            <tr>
              <th>#</th>
              <th>fix type</th>
              <th>before</th>
              <th>after</th>
              <th>Δ</th>
              <th>applied</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((exp) => {
              const pre = exp.pre_score ?? 0;
              const post = exp.post_score ?? 0;
              const delta = post - pre;
              const improved = delta > 0;
              return (
                <tr key={exp.id}>
                  <td className="mono">{exp.id}</td>
                  <td className="mono">{exp.applied_fix?.fix_type?.replaceAll("_", " ")}</td>
                  <td className="mono">{pre.toFixed(2)}</td>
                  <td className="mono">{post.toFixed(2)}</td>
                  <td className={`mono delta ${improved ? "good" : delta < 0 ? "bad" : ""}`}>
                    {delta > 0 ? "+" : ""}
                    {delta.toFixed(2)}
                  </td>
                  <td className="mono dim">{new Date(exp.applied_at).toLocaleString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
