// src/pages/PlantDisease.jsx
import React, { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { API_BASE_URL } from '../services/api';
import "./PlantDisease.css";

const PlantDisease = () => {
  const { i18n } = useTranslation();
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError("");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setImageFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) return setError("Please upload a leaf image first.");
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", imageFile);

      const response = await fetch(`${API_BASE_URL}/api/disease/predict?lang=${i18n.language}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to analyse image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImageFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Format disease name for display
  const formatDiseaseName = (label) => {
    if (!label) return "";
    const parts = label.split("___");
    const plant = parts[0]?.replace(/_/g, " ");
    const disease = parts[1]?.replace(/_/g, " ").replace(/\(/g, " (");
    return disease ? `${plant} — ${disease}` : plant;
  };

  const isHealthy = result?.disease?.includes("healthy");

  return (
    <div className="pd-page">
      <div className="pd-hero">
        <div className="pd-hero-icon">🌿</div>
        <h1 className="pd-title">Plant Disease Detection</h1>
        <p className="pd-subtitle">
          Upload a photo of a crop leaf and our AI will identify any diseases and recommend treatments.
        </p>
      </div>

      <div className="pd-card">
        {/* Upload Zone */}
        <div
          className={`pd-dropzone ${previewUrl ? "pd-dropzone--has-image" : ""}`}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => !previewUrl && fileInputRef.current?.click()}
        >
          {previewUrl ? (
            <div className="pd-preview-wrapper">
              <img src={previewUrl} alt="Uploaded leaf" className="pd-preview-img" />
              <button className="pd-change-btn" onClick={(e) => { e.stopPropagation(); handleReset(); }}>
                ✕ Remove
              </button>
            </div>
          ) : (
            <div className="pd-dropzone-content">
              <div className="pd-upload-icon">📷</div>
              <p className="pd-upload-primary">Drag &amp; drop a leaf image here</p>
              <p className="pd-upload-secondary">or click to browse</p>
              <p className="pd-upload-hint">Supports JPG, PNG, WEBP</p>
            </div>
          )}
        </div>

        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          ref={fileInputRef}
          style={{ display: "none" }}
        />

        {error && <div className="pd-error">⚠️ {error}</div>}

        <button
          className="pd-analyze-btn"
          onClick={handleSubmit}
          disabled={loading || !imageFile}
        >
          {loading ? (
            <span className="pd-spinner-group"><span className="pd-spinner" /> Analysing…</span>
          ) : (
            "🔬 Analyse Leaf"
          )}
        </button>
      </div>

      {/* Results Card */}
      {result && (
        <div className={`pd-result-card ${isHealthy ? "pd-result-card--healthy" : "pd-result-card--disease"}`}>
          <div className="pd-result-header">
            <span className="pd-result-icon">{isHealthy ? "✅" : "⚠️"}</span>
            <div>
              <h2 className="pd-result-title">{formatDiseaseName(result.disease)}</h2>
            </div>
          </div>

          <div className="pd-result-section">
            <h3 className="pd-section-label">🩺 Recommended Treatment</h3>
            <p className="pd-treatment-text">{result.treatment}</p>
          </div>

          {result.heatmap_image && (
            <div className="pd-result-section">
              <h3 className="pd-section-label">🔍 AI Explainability</h3>
              <p className="pd-heatmap-desc">The heatmap below highlights the physical areas of the leaf that led to the AI's diagnosis.</p>
              <img src={result.heatmap_image} alt="Disease Heatmap" className="pd-heatmap-img" />
            </div>
          )}

          {result.all_predictions && result.all_predictions.length > 1 && (
            <div className="pd-result-section">
              <h3 className="pd-section-label">📊 Other Possibilities</h3>
              <div className="pd-alt-list">
                {result.all_predictions.slice(1).map((p, i) => (
                  <div key={i} className="pd-alt-item">
                    <span>{formatDiseaseName(p.disease)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlantDisease;
