import { useMemo, useState } from "react";

const DEMOS = [
  { id: 1, label: "Demo 1: Skin Rash" },
  { id: 2, label: "Demo 2: Minor Burn" },
  { id: 3, label: "Demo 3: Eye Redness" },
];

export default function InputForm({ onSubmit, onDemo, error }) {
  const [formData, setFormData] = useState({
    symptom_text: "",
    body_location: "",
    duration_days: 1,
    severity_score: 5,
    age: "",
    known_conditions: "",
    medications: "",
    provider: "anthropic",
  });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const charCount = formData.symptom_text.trim().length;

  const canSubmit = useMemo(() => {
    return (
      formData.symptom_text.trim().length >= 10 &&
      formData.body_location.trim().length > 0 &&
      !isSubmitting
    );
  }, [formData, isSubmitting]);

  function setField(name, value) {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function onSelectFile(file) {
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      return;
    }
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  async function submit() {
    if (!canSubmit) return;
    setIsSubmitting(true);
    try {
      await onSubmit(formData, imageFile);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function runScenario(id) {
    setIsSubmitting(true);
    try {
      await onDemo(formData.provider, id);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="card stack gap-lg">
      <div>
        <h2>Symptom Intake</h2>
        <p>Provide symptom details and optionally upload an image.</p>
      </div>

      <div className="grid two-col gap-md">
        <label className="field span-2">
          <span>Symptom description *</span>
          <textarea
            value={formData.symptom_text}
            placeholder="Describe your symptoms in detail..."
            onChange={(e) => setField("symptom_text", e.target.value)}
            minLength={10}
          />
          <small>{charCount < 10 ? `Need ${10 - charCount} more characters` : `${charCount} characters`}</small>
        </label>

        <label className="field">
          <span>Body location *</span>
          <input
            value={formData.body_location}
            placeholder="e.g. left forearm, right eye"
            onChange={(e) => setField("body_location", e.target.value)}
          />
        </label>

        <label className="field">
          <span>Duration (days)</span>
          <input
            type="number"
            min={0}
            max={365}
            value={formData.duration_days}
            onChange={(e) => setField("duration_days", e.target.value)}
          />
        </label>

        <label className="field span-2">
          <span>Severity score: {formData.severity_score}/10</span>
          <input
            type="range"
            min={1}
            max={10}
            value={formData.severity_score}
            onChange={(e) => setField("severity_score", e.target.value)}
          />
          <small>This scale is for the severity of your pain (1 = mild, 10 = severe).</small>
        </label>

        <label className="field">
          <span>Age (optional)</span>
          <input type="number" min={0} value={formData.age} onChange={(e) => setField("age", e.target.value)} />
        </label>

        <label className="field">
          <span>Known conditions (optional)</span>
          <input
            value={formData.known_conditions}
            onChange={(e) => setField("known_conditions", e.target.value)}
            placeholder="e.g. diabetes"
          />
        </label>

        <label className="field span-2">
          <span>Current medications (optional)</span>
          <input
            value={formData.medications}
            onChange={(e) => setField("medications", e.target.value)}
            placeholder="e.g. ibuprofen"
          />
        </label>

        <label className="field span-2">
          <span>AI provider</span>
          <select value={formData.provider} onChange={(e) => setField("provider", e.target.value)}>
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="openai">OpenAI (GPT-4o)</option>
          </select>
        </label>
      </div>

      <div className="stack gap-sm">
        <h3>Image upload</h3>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => onSelectFile(e.target.files?.[0])}
        />
        {imagePreview ? (
          <div className="preview-wrap stack gap-sm">
            <img src={imagePreview} alt="Selected symptom" />
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setImageFile(null);
                setImagePreview("");
              }}
            >
              Remove image
            </button>
          </div>
        ) : (
          <p className="note">No image - text only mode.</p>
        )}
      </div>

      <div className="stack gap-sm">
        <h3>Demo mode</h3>
        <div className="row wrap gap-sm">
          {DEMOS.map((demo) => (
            <button key={demo.id} className="ghost" onClick={() => runScenario(demo.id)} disabled={isSubmitting}>
              {demo.label}
            </button>
          ))}
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="row gap-sm">
        <button className="primary" onClick={submit} disabled={!canSubmit}>
          Analyze Symptoms
        </button>
      </div>
    </section>
  );
}
