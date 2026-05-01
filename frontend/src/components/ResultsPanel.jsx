import { AlertOctagon, AlertTriangle, ArrowRight, Info, ShieldAlert, Stethoscope } from "lucide-react";
import ConflictCallout from "./ConflictCallout";
import DisclaimerBanner from "./DisclaimerBanner";
import UrgencyBadge from "./UrgencyBadge";

function normalizeConfidence(confidence) {
  const value = String(confidence || "Medium");
  return `${value.charAt(0).toUpperCase()}${value.slice(1).toLowerCase()}`;
}

function ConditionCard({ name, confidence }) {
  const confidenceLabel = normalizeConfidence(confidence);

  return (
    <article className={`condition-card confidence-border-${confidenceLabel.toLowerCase()}`}>
      <div>
        <span>Possible condition</span>
        <h3>{name}</h3>
      </div>
      <span className={`confidence confidence-${confidenceLabel.toLowerCase()}`}>{confidenceLabel}</span>
    </article>
  );
}

function classifyRiskSignal(signal) {
  const text = String(signal).toLowerCase();
  if (
    text.includes("bleeding") ||
    text.includes("severe") ||
    text.includes("emergency") ||
    text.includes("high") ||
    text.includes("red flag")
  ) {
    return { level: "critical", width: "92%", Icon: AlertOctagon };
  }

  if (
    text.includes("worsening") ||
    text.includes("spreading") ||
    text.includes("discharge") ||
    text.includes("infection") ||
    text.includes("conflict") ||
    text.includes("mismatch") ||
    text.includes("risk")
  ) {
    return { level: "warning", width: "74%", Icon: AlertTriangle };
  }

  return { level: "info", width: "52%", Icon: Info };
}

function RiskSignalRow({ signal }) {
  const { level, width, Icon } = classifyRiskSignal(signal);

  return (
    <li className={`risk-signal-row risk-${level}`}>
      <div className="risk-signal-name">
        <Icon size={18} strokeWidth={2.3} aria-hidden="true" />
        <span>{signal}</span>
      </div>
      <div className="risk-signal-bar" aria-hidden="true">
        <span style={{ width }} />
      </div>
    </li>
  );
}

function EmptyPanel({ children }) {
  return <p className="empty-copy">{children}</p>;
}

export default function ResultsPanel({ data, onReset }) {
  const diagnosis = data.diagnosis || {};
  const quality = data.quality || {};
  const imageFallbackReason = data.no_image_reason;
  const possibleConditions = Array.isArray(diagnosis.possible_conditions) ? diagnosis.possible_conditions : [];
  const clinicalReasoning = Array.isArray(diagnosis.clinical_reasoning) ? diagnosis.clinical_reasoning : [];
  const riskSignals = Array.isArray(data.risk_signals) ? data.risk_signals : [];
  const redFlags = Array.isArray(diagnosis.red_flags) ? diagnosis.red_flags : [];

  return (
    <section className="results-layout">
      <div className="results-main">
        <DisclaimerBanner />
        <UrgencyBadge urgency={data.urgency} />
        <ConflictCallout conflict={data.conflict} />

        <section className="card result-card">
          <div className="result-card-header">
            <div>
              <span className="eyebrow">Clinical insight panel</span>
              <h2>Possible conditions</h2>
            </div>
            <p>Educational possibilities to discuss with a clinician. Not a diagnosis.</p>
          </div>

          {possibleConditions.length > 0 ? (
            <div className="condition-grid">
              {possibleConditions.map((condition, index) => (
                <ConditionCard
                  key={`${condition}-${index}`}
                  name={condition}
                  confidence={diagnosis.confidence_levels?.[index] || "Medium"}
                />
              ))}
            </div>
          ) : (
            <EmptyPanel>No possible conditions were returned for this assessment.</EmptyPanel>
          )}
        </section>

        <section className="card result-card assessment-card">
          <div className="result-card-header">
            <div className="clinical-summary-heading">
              <span className="summary-heading-icon">
                <Stethoscope size={24} strokeWidth={2.3} aria-hidden="true" />
              </span>
              <div>
                <span className="eyebrow">Structured summary</span>
                <h2>Clinical assessment</h2>
              </div>
            </div>
          </div>

          {clinicalReasoning.length > 0 ? (
            <ol className="assessment-list">
              {clinicalReasoning.map((line, index) => (
                <li key={`reason-${index}`}>
                  <span>{index + 1}</span>
                  <p>{line}</p>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyPanel>No clinical assessment text was returned.</EmptyPanel>
          )}
        </section>

        {riskSignals.length > 0 ? (
          <section className="card result-card risk-signals-card">
            <div className="result-card-header">
              <div>
                <span className="eyebrow">Evidence fusion</span>
                <h2>Risk signals detected</h2>
              </div>
            </div>
            <ul className="risk-signal-list">
              {riskSignals.map((signal, index) => (
                <RiskSignalRow key={`risk-${index}`} signal={signal} />
              ))}
            </ul>
          </section>
        ) : null}

        {redFlags.length > 0 ? (
          <section className="card result-card red-flags">
            <div className="result-card-header">
              <div>
                <span className="eyebrow">Care escalation</span>
                <h2 className="heading-with-icon">
                  <ShieldAlert size={24} strokeWidth={2.3} aria-hidden="true" />
                  Red flags
                </h2>
              </div>
            </div>
            <ul className="signal-list red-list">
              {redFlags.map((flag, index) => (
                <li key={`flag-${index}`}>
                  <span aria-hidden="true" />
                  <p>{flag}</p>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
      </div>

      <aside className="results-side">
        <section className="next-step-card">
          <span className="eyebrow">Recommended next step</span>
          <h2 className="heading-with-icon">
            {data.urgency === "high" ? "Seek prompt medical care" : "Plan your next care step"}
            <ArrowRight size={24} strokeWidth={2.4} aria-hidden="true" />
          </h2>
          <p>{diagnosis.recommendation || "Seek medical evaluation if symptoms persist or worsen."}</p>
        </section>

        {quality.show_uncertain_badge ? (
          <section className="support-card warning-support">
            <strong>Uncertain triage</strong>
            <p>Input data was limited. A clearer image or more symptom detail may improve the assessment.</p>
          </section>
        ) : null}

        {data.no_image_mode ? (
          <section className="support-card">
            <strong>Text-only mode</strong>
            <p>
              {imageFallbackReason === "no_image_provided"
                ? "No image was provided. The assessment used symptom text only."
                : imageFallbackReason === "image_not_medically_relevant"
                  ? "The uploaded image was not medically relevant, so the assessment used symptom text only."
                  : imageFallbackReason === "vision_processing_error" || imageFallbackReason === "vision_schema_validation_error"
                    ? "The image was received, but visual analysis failed. The assessment used symptom text only."
                    : "No image was used for this assessment."}
            </p>
          </section>
        ) : null}

        <button className="secondary-button full-width" onClick={onReset}>
          Start a new assessment
        </button>
      </aside>
    </section>
  );
}
