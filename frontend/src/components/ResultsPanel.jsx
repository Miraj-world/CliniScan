import ConflictCallout from "./ConflictCallout";
import DisclaimerBanner from "./DisclaimerBanner";
import UrgencyBadge from "./UrgencyBadge";

function ConditionCard({ name, confidence }) {
  return (
    <div className="condition-card">
      <p>{name}</p>
      <span className={`confidence confidence-${String(confidence || "").toLowerCase()}`}>{confidence}</span>
    </div>
  );
}

export default function ResultsPanel({ data, onReset }) {
  const diagnosis = data.diagnosis || {};
  const quality = data.quality || {};
  const imageFallbackReason = data.no_image_reason;

  return (
    <section className="stack gap-md">
      <DisclaimerBanner />
      <UrgencyBadge urgency={data.urgency} />
      <ConflictCallout conflict={data.conflict} />

      <div className="card stack gap-sm">
        <h3>Possible conditions</h3>
        <div className="grid two-col gap-sm">
          {(diagnosis.possible_conditions || []).map((condition, idx) => (
            <ConditionCard
              key={`${condition}-${idx}`}
              name={condition}
              confidence={diagnosis.confidence_levels?.[idx] || "Medium"}
            />
          ))}
        </div>
      </div>

      <div className="card stack gap-sm">
        <h3>Clinical assessment</h3>
        <ul>
          {(diagnosis.clinical_reasoning || []).map((line, idx) => (
            <li key={`reason-${idx}`}>{line}</li>
          ))}
        </ul>
      </div>

      {Array.isArray(data.risk_signals) && data.risk_signals.length > 0 ? (
        <div className="card stack gap-sm">
          <h3>Risk signals detected</h3>
          <ul>
            {data.risk_signals.map((signal, idx) => (
              <li key={`risk-${idx}`}>{signal}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {Array.isArray(diagnosis.red_flags) && diagnosis.red_flags.length > 0 ? (
        <div className="card stack gap-sm red-flags">
          <h3>Red flags</h3>
          <ul>
            {diagnosis.red_flags.map((flag, idx) => (
              <li key={`flag-${idx}`}>{flag}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="card stack gap-sm">
        <h3>Recommended next step</h3>
        <p>{diagnosis.recommendation}</p>
      </div>

      {quality.show_uncertain_badge ? (
        <div className="banner banner-warning">
          Uncertain Triage - Input data was insufficient for high-confidence assessment.
        </div>
      ) : null}

      {data.no_image_mode ? (
        <div className="banner">
          {imageFallbackReason === "no_image_provided"
            ? "Text-only mode - No image was provided."
            : imageFallbackReason === "image_not_medically_relevant"
              ? "Text-only mode - The uploaded image was not medically relevant."
              : imageFallbackReason === "vision_processing_error" || imageFallbackReason === "vision_schema_validation_error"
                ? "Text-only mode - Image upload was received, but vision analysis failed. The result used symptom text only."
                : "Text-only mode - No image was used."}
        </div>
      ) : null}

      <button className="primary" onClick={onReset}>
        Start over
      </button>
    </section>
  );
}
