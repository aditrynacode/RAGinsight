import { useState } from "react";
import "./ChunkList.css";

export default function ChunkList({ chunks }) {
  const [open, setOpen] = useState(false);
  if (!chunks?.length) return null;

  return (
    <div className="chunk-list">
      <button className="chunk-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? "▾" : "▸"} {chunks.length} source{chunks.length !== 1 ? "s" : ""}
      </button>
      {open && (
        <div className="chunk-items">
          {chunks.map((c, i) => (
            <div className="chunk-item" key={c.chunk_id ?? i}>
              <div className="chunk-item-head">
                <span>chunk {c.chunk_id ?? "?"}</span>
                {c.similarity_score != null && (
                  <span className="chunk-score">score {c.similarity_score.toFixed(3)}</span>
                )}
              </div>
              <p>{c.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
