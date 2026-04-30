import { useEffect, useMemo, useRef, useState } from "react";
import InputForm from "./components/InputForm";
import PipelineProgress from "./components/PipelineProgress";
import ResultsPanel from "./components/ResultsPanel";

const STAGES = [
  "Analyzing image",
  "Structuring symptoms",
  "Fusing evidence",
  "Computing risk level",
  "Generating reasoning",
];

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = String(reader.result || "");
      const b64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(b64);
    };
    reader.onerror = () => reject(new Error("Unable to read image file"));
    reader.readAsDataURL(file);
  });
}

export default function App() {
  const [view, setView] = useState("input");
  const [currentStage, setCurrentStage] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const status = useMemo(() => ({ apiUrl: API_URL }), []);

async function callAnalyze(payload) {
    let res;
    try {
      res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (_error) {
      throw new Error(`Unable to reach backend at ${API_URL}. Make sure the API server is running.`);
    }

    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.detail || body.message || `Request failed (${res.status})`);
    }
    return body;
  }

  async function runAnalysis(formData, imageFile) {
    setError(null);
    setView("processing");
    setCurrentStage(0);

    timerRef.current = setInterval(() => {
      setCurrentStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 850);

    try {
      let image_base64;
      let image_mime;
      if (imageFile) {
        image_base64 = await toBase64(imageFile);
        image_mime = imageFile.type || "image/jpeg";
      }

      const payload = {
        symptom_text: formData.symptom_text,
        body_location: formData.body_location,
        duration_days: Number(formData.duration_days),
        severity_score: Number(formData.severity_score),
        age: formData.age ? Number(formData.age) : null,
        known_conditions: formData.known_conditions || null,
        medications: formData.medications || null,
        image_base64,
        image_mime,
        provider: formData.provider,
      };

      const response = await callAnalyze(payload);
      setCurrentStage(STAGES.length - 1);
      setTimeout(() => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
        setResults(response);
        setView("results");
      }, 750);
    } catch (err) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      setError(err.message || "Analysis failed");
      setView("input");
    }
  }

  async function runDemo(provider, scenario) {
    setError(null);
    setView("processing");
    setCurrentStage(0);

    timerRef.current = setInterval(() => {
      setCurrentStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 300);

    try {
      const response = await callAnalyze({
        symptom_text: "Demo request placeholder text",
        body_location: "demo",
        duration_days: 1,
        severity_score: 1,
        provider,
        demo_scenario: scenario,
      });

      setCurrentStage(STAGES.length - 1);
      setTimeout(() => {
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
        setResults(response);
        setView("results");
      }, 350);
    } catch (err) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      setError(err.message || "Demo request failed");
      setView("input");
    }
  }

  function resetAll() {
    setResults(null);
    setError(null);
    setCurrentStage(0);
    setView("input");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>CliniScan</h1>
        <p>Layered multimodal triage workflow</p>
        <span className="api-status">Backend: {status.apiUrl}</span>
      </header>

      <main className="page">
        {view === "input" && (
          <InputForm onSubmit={runAnalysis} onDemo={runDemo} error={error} />
        )}

        {view === "processing" && (
          <PipelineProgress stageIndex={currentStage} stages={STAGES} />
        )}

        {view === "results" && results && (
          <ResultsPanel data={results} onReset={resetAll} />
        )}
      </main>
    </div>
  );
}
