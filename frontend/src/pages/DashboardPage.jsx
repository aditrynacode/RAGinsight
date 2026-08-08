import { useState, useEffect } from "react";
import { getSummary, getTimeline, getFailureBreakdown, listExperiments, listDocuments } from "../api/client";
import StatCards from "../components/StatCards";
import EvalTimelineChart from "../components/EvalTimelineChart";
import FailureBreakdownChart from "../components/FailureBreakdownChart";
import ExperimentsTable from "../components/ExperimentsTable";
import DocumentChunkInspector from "../components/DocumentChunkInspector";
import "./DashboardPage.css";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [breakdown, setBreakdown] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadAll() {
    setError(null);
    try {
      const [s, t, b, e, d] = await Promise.all([
        getSummary(),
        getTimeline(),
        getFailureBreakdown(),
        listExperiments(),
        listDocuments(),
      ]);
      setSummary(s);
      setTimeline(t);
      setBreakdown(b);
      setExperiments(e);
      setDocuments(d);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  return (
    <div className="dashboard-page">
      <div className="dashboard-head">
        <div className="eyebrow">System status</div>
        <button className="refresh-btn" onClick={loadAll}>
          ↻ refresh
        </button>
      </div>

      {loading && <div className="dashboard-loading">loading dashboard…</div>}
      {error && <div className="dashboard-error">{error}</div>}

      {!loading && (
        <>
          <StatCards summary={summary} />

          <EvalTimelineChart data={timeline} />

          <div className="dashboard-grid">
            <FailureBreakdownChart data={breakdown} />
            <DocumentChunkInspector documents={documents} />
          </div>

          <ExperimentsTable experiments={experiments} />
        </>
      )}
    </div>
  );
}
