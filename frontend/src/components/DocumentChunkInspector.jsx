import { useState, useEffect } from "react";
import { getChunks } from "../api/client";
import "./DocumentChunkInspector.css";

export default function DocumentChunkInspector({ documents }) {
  const [selectedId, setSelectedId] = useState("");
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedId) {
      setChunks([]);
      return;
    }
    setLoading(true);
    setError(null);
    getChunks(selectedId)
      .then(setChunks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [selectedId]);

  const selectedDoc = documents?.find((d) => String(d.id) === String(selectedId));

  return (
    <div className="panel inspector-panel">
      <div className="eyebrow">Chunk inspector</div>

      {!documents?.length ? (
        <p className="inspector-empty">No documents ingested yet.</p>
      ) : (
        <>
          <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
            <option value="">Select a document…</option>
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title} ({d.source})
              </option>
            ))}
          </select>

          {selectedDoc && (
            <div className="inspector-meta mono">
              chunk_size={selectedDoc.chunk_size} chunk_overlap={selectedDoc.chunk_overlap}
            </div>
          )}

          {loading && <div className="inspector-loading">loading chunks…</div>}
          {error && <div className="inspector-error">{error}</div>}

          {!loading && chunks.length > 0 && (
            <div className="inspector-chunks">
              {chunks.map((c) => (
                <div className="inspector-chunk" key={c.id}>
                  <div className="inspector-chunk-head mono">
                    #{c.chunk_index} · chunk_id {c.id}
                    {c.page != null && ` · page ${c.page}`}
                  </div>
                  <p>{c.content}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
