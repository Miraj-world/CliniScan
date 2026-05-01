import { useEffect, useMemo, useRef, useState } from "react";

const DEMO_SCENARIOS = [
  {
    id: 1,
    label: "Skin Rash",
    description: "Spreading rash with mild fever",
    tone: "medium",
  },
  {
    id: 2,
    label: "Minor Burn",
    description: "Small blister on fingertip",
    tone: "low",
  },
  {
    id: 3,
    label: "Eye Redness",
    description: "Red eye with discharge",
    tone: "high",
  },
];

const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024;

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
  const [imageError, setImageError] = useState("");
  const [isDraggingImage, setIsDraggingImage] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const characterCount = formData.symptom_text.trim().length;
  const remainingCharacters = Math.max(10 - characterCount, 0);

  const canSubmit = useMemo(() => {
    return (
      formData.symptom_text.trim().length >= 10 &&
      formData.body_location.trim().length > 0 &&
      !isSubmitting
    );
  }, [formData, isSubmitting]);

  function setField(name, value) {
    setFormData((previousData) => ({ ...previousData, [name]: value }));
  }

  function selectImageFile(file) {
    setImageError("");
    if (!file) return;

    if (!ACCEPTED_IMAGE_TYPES.includes(file.type)) {
      setImageError("Upload a JPG, PNG, or WEBP image.");
      return;
    }

    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      setImageError("Image must be smaller than 10 MB.");
      return;
    }

    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function removeImage() {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setImageFile(null);
    setImagePreview("");
    setImageError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function submitForm() {
    if (!canSubmit) return;
    setIsSubmitting(true);
    try {
      await onSubmit(formData, imageFile);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function runDemoScenario(id) {
    setIsSubmitting(true);
    try {
      await onDemo(formData.provider, id);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="intake-layout">
      <section className="card intake-card">
        <div className="section-heading">
          <span className="eyebrow">Patient intake</span>
          <h2>Symptom Intake</h2>
          <p>
            Describe what is happening, add context, and optionally upload an image for a structured triage summary.
          </p>
        </div>

        {error ? (
          <div className="alert alert-error" role="alert">
            <strong>Analysis could not start.</strong>
            <span>{error}</span>
          </div>
        ) : null}

        <div className="form-grid">
          <label className="field span-2">
            <span>Symptom description *</span>
            <textarea
              value={formData.symptom_text}
              placeholder="Describe what you are experiencing, when it started, whether it is changing, and any related symptoms."
              onChange={(event) => setField("symptom_text", event.target.value)}
              minLength={10}
            />
            <small>
              {remainingCharacters > 0
                ? `${remainingCharacters} more character${remainingCharacters === 1 ? "" : "s"} needed`
                : `${characterCount} characters entered`}
            </small>
          </label>

          <label className="field">
            <span>Body location *</span>
            <input
              value={formData.body_location}
              placeholder="Left forearm, right eye, chest"
              onChange={(event) => setField("body_location", event.target.value)}
            />
          </label>

          <label className="field">
            <span>Duration</span>
            <div className="input-with-unit">
              <input
                type="number"
                min={0}
                max={365}
                value={formData.duration_days}
                onChange={(event) => setField("duration_days", event.target.value)}
              />
              <span>days</span>
            </div>
          </label>

          <div className="field span-2 severity-field">
            <div className="field-row">
              <span>Severity score</span>
              <strong>{formData.severity_score} / 10</strong>
            </div>
            <input
              aria-label="Severity score"
              type="range"
              min={1}
              max={10}
              value={formData.severity_score}
              onChange={(event) => setField("severity_score", event.target.value)}
            />
            <div className="range-labels" aria-hidden="true">
              <span>Mild</span>
              <span>Moderate</span>
              <span>Severe</span>
            </div>
          </div>

          <label className="field">
            <span>Age</span>
            <input
              type="number"
              min={0}
              value={formData.age}
              onChange={(event) => setField("age", event.target.value)}
              placeholder="Optional"
            />
          </label>

          <label className="field">
            <span>Known conditions</span>
            <input
              value={formData.known_conditions}
              onChange={(event) => setField("known_conditions", event.target.value)}
              placeholder="Diabetes, asthma, immune condition"
            />
          </label>

          <label className="field span-2">
            <span>Current medications</span>
            <input
              value={formData.medications}
              onChange={(event) => setField("medications", event.target.value)}
              placeholder="Ibuprofen, antibiotics, daily medications"
            />
          </label>

          <label className="field span-2">
            <span>AI provider</span>
            <select value={formData.provider} onChange={(event) => setField("provider", event.target.value)}>
              <option value="anthropic">Anthropic Claude</option>
              <option value="openai">OpenAI GPT-4o</option>
            </select>
          </label>
        </div>

        <div className="upload-section">
          <div className="section-subhead">
            <h3>Image upload</h3>
            <p>Optional. A clear image can help the system compare visual evidence with the symptom description.</p>
          </div>

          <div
            className={`upload-dropzone ${isDraggingImage ? "dragging" : ""} ${imagePreview ? "has-image" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDraggingImage(true);
            }}
            onDragLeave={() => setIsDraggingImage(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDraggingImage(false);
              selectImageFile(event.dataTransfer.files?.[0]);
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(event) => selectImageFile(event.target.files?.[0])}
            />

            {imagePreview ? (
              <div className="image-preview-grid">
                <img src={imagePreview} alt="Selected symptom" />
                <div>
                  <strong>{imageFile?.name}</strong>
                  <p>Image ready for visual triage support.</p>
                  <button type="button" className="secondary-button" onClick={removeImage}>
                    Remove image
                  </button>
                </div>
              </div>
            ) : (
              <button type="button" className="upload-prompt" onClick={() => fileInputRef.current?.click()}>
                <span className="upload-icon" aria-hidden="true" />
                <strong>Drop an image here or browse</strong>
                <small>JPG, PNG, or WEBP. Max 10 MB.</small>
              </button>
            )}
          </div>

          {imageError ? <p className="field-error">{imageError}</p> : null}
          {!imagePreview ? <p className="note">No image selected. Text-only triage is supported.</p> : null}
        </div>

        <div className="demo-section">
          <div className="section-subhead">
            <h3>Demo scenarios</h3>
            <p>Use cached results for a fast presentation flow without live API calls.</p>
          </div>
          <div className="demo-grid">
            {DEMO_SCENARIOS.map((demoScenario) => (
              <button
                key={demoScenario.id}
                className={`demo-card demo-${demoScenario.tone}`}
                onClick={() => runDemoScenario(demoScenario.id)}
                disabled={isSubmitting}
              >
                <span>{demoScenario.label}</span>
                <small>{demoScenario.description}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="form-actions">
          <button className="primary-button" onClick={submitForm} disabled={!canSubmit}>
            {isSubmitting ? (
              <>
                <span className="button-spinner" aria-hidden="true" />
                Analyzing...
              </>
            ) : (
              "Analyze Symptoms"
            )}
          </button>
          <p>Results are triage support only and should be reviewed with a licensed professional.</p>
        </div>
      </section>

      <aside className="side-panel">
        <div className="card guidance-card">
          <span className="eyebrow">Workflow</span>
          <h2>How CliniScan works</h2>
          <ol className="step-list">
            <li>
              <span>1</span>
              <div>
                <strong>Describe symptoms</strong>
                <p>Enter the symptom story, location, duration, and severity.</p>
              </div>
            </li>
            <li>
              <span>2</span>
              <div>
                <strong>Add context</strong>
                <p>Optional image and medical context improve the structured risk picture.</p>
              </div>
            </li>
            <li>
              <span>3</span>
              <div>
                <strong>Review triage signals</strong>
                <p>See urgency, risk signals, possible conditions, and next steps.</p>
              </div>
            </li>
          </ol>
        </div>

        <div className="card safety-card">
          <span className="eyebrow">Safety posture</span>
          <h2>Triage support, not diagnosis</h2>
          <p>
            CliniScan highlights urgency and care direction. It does not replace medical evaluation or provide a
            clinical diagnosis.
          </p>
        </div>
      </aside>
    </div>
  );
}
