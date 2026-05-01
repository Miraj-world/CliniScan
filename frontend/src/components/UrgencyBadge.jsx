const URGENCY_CONTENT = {
  high: {
    className: "urgency-high",
    label: "High urgency",
    headline: "Seek medical attention promptly",
    detail: "Risk signals indicate this should be reviewed by a clinician without delay.",
  },
  medium: {
    className: "urgency-medium",
    label: "Medium urgency",
    headline: "Schedule a medical visit",
    detail: "Symptoms deserve timely review, especially if they worsen or persist.",
  },
  low: {
    className: "urgency-low",
    label: "Low urgency",
    headline: "Monitor and seek care if worsening",
    detail: "Current inputs suggest lower immediate risk, with continued observation recommended.",
  },
};

export default function UrgencyBadge({ urgency }) {
  const content = URGENCY_CONTENT[urgency] || URGENCY_CONTENT.medium;

  return (
    <section className={`urgency-panel ${content.className}`} aria-label={`${content.label} triage result`}>
      <div className="urgency-marker" aria-hidden="true" />
      <div>
        <span>{content.label}</span>
        <h2>{content.headline}</h2>
        <p>{content.detail}</p>
      </div>
    </section>
  );
}
