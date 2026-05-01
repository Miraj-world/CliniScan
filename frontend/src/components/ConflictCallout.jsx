function formatSeverity(value) {
  if (!value) return "Unknown";
  return `${String(value).charAt(0).toUpperCase()}${String(value).slice(1)}`;
}

export default function ConflictCallout({ conflict }) {
  if (!conflict?.conflict_detected) return null;

  return (
    <section className="conflict-panel">
      <div className="conflict-icon" aria-hidden="true" />
      <div className="conflict-content">
        <span className="eyebrow">Clinical mismatch detected</span>
        <h2>Visual evidence differs from reported severity</h2>
        <div className="severity-comparison">
          <div>
            <span>Reported</span>
            <strong>{formatSeverity(conflict.text_severity)}</strong>
          </div>
          <div>
            <span>Observed visual</span>
            <strong>{formatSeverity(conflict.vision_severity)}</strong>
          </div>
        </div>
        <p>CliniScan weighted the visual evidence more heavily for this triage assessment.</p>
      </div>
    </section>
  );
}
