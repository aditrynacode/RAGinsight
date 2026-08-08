import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";
import "./EvalTimelineChart.css";

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="trace-tooltip">
      <div>score {p.score.toFixed(2)}</div>
      <div className="trace-tooltip-time">{new Date(p.timestamp).toLocaleString()}</div>
    </div>
  );
}

export default function EvalTimelineChart({ data }) {
  if (!data?.length) {
    return (
      <div className="panel trace-panel trace-empty">
        <div className="eyebrow">Eval score over time</div>
        <p>No scored queries yet — ask some questions to start the trace.</p>
      </div>
    );
  }

  const chartData = data.map((d, i) => ({ index: i + 1, score: d.score, timestamp: d.timestamp }));

  return (
    <div className="panel trace-panel">
      <div className="eyebrow">Eval score over time</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 16, right: 16, left: -12, bottom: 0 }}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="2 4" vertical={false} />
          <XAxis
            dataKey="index"
            stroke="var(--text-dim)"
            tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "var(--text-dim)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--border-bright)" }}
          />
          <YAxis
            domain={[1, 5]}
            stroke="var(--text-dim)"
            tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "var(--text-dim)" }}
            tickLine={false}
            axisLine={false}
            width={28}
          />
          <ReferenceLine y={3} stroke="var(--border-bright)" strokeDasharray="3 3" />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: "var(--border-bright)" }} />
          <Line
            type="linear"
            dataKey="score"
            stroke="var(--amber)"
            strokeWidth={2}
            dot={{ r: 2.5, fill: "var(--amber)", strokeWidth: 0 }}
            activeDot={{ r: 4 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
