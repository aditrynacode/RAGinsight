import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { categoryMeta } from "../categoryMeta";
import "./FailureBreakdownChart.css";

function resolveColor(varName) {
  if (typeof window === "undefined") return varName;
  const clean = varName.replace("var(", "").replace(")", "");
  return getComputedStyle(document.documentElement).getPropertyValue(clean).trim() || varName;
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0];
  return (
    <div className="trace-tooltip">
      {p.name}: {p.value}
    </div>
  );
}

export default function FailureBreakdownChart({ data }) {
  if (!data?.length) {
    return (
      <div className="panel breakdown-panel breakdown-empty">
        <div className="eyebrow">Failures diagnosed</div>
        <p>No diagnoses yet — thumbs-down an answer to trigger one.</p>
      </div>
    );
  }

  const chartData = data.map((d) => ({
    name: categoryMeta(d.category).label,
    value: d.count,
    color: resolveColor(categoryMeta(d.category).color),
  }));

  return (
    <div className="panel breakdown-panel">
      <div className="eyebrow">Failures diagnosed</div>
      <div className="breakdown-body">
        <ResponsiveContainer width={140} height={140}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={38}
              outerRadius={62}
              paddingAngle={2}
              isAnimationActive={false}
              stroke="var(--panel)"
              strokeWidth={2}
            >
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="breakdown-legend">
          {chartData.map((d) => (
            <div className="breakdown-legend-row" key={d.name}>
              <span className="badge-dot" style={{ background: d.color }} />
              <span className="breakdown-legend-label">{d.name}</span>
              <span className="breakdown-legend-value">{d.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
