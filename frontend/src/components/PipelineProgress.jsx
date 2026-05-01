const STAGE_META = [
  { label: "Vision", colorClass: "stage-blue" },
  { label: "Text", colorClass: "stage-green" },
  { label: "Fusion", colorClass: "stage-purple" },
  { label: "Risk", colorClass: "stage-orange" },
  { label: "Reason", colorClass: "stage-teal" },
];

export default function PipelineProgress({ stageIndex, stages }) {
  return (
    <section className="processing-card">
      <div className="section-heading center">
        <span className="eyebrow">Analysis in progress</span>
        <h2>Running layered triage workflow</h2>
        <p>CliniScan is structuring evidence, computing risk, and preparing the assessment summary.</p>
      </div>

      <ol className="pipeline-list">
        {stages.map((stage, index) => {
          const state = index < stageIndex ? "complete" : index === stageIndex ? "running" : "pending";
          return (
            <li key={stage} className={`pipeline-item ${state} ${STAGE_META[index]?.colorClass || ""}`}>
              <span className="pipeline-node" aria-hidden="true">
                {state === "complete" ? "" : index + 1}
              </span>
              <div>
                <span>{STAGE_META[index]?.label}</span>
                <strong>{stage}</strong>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
