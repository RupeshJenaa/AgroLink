import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { fertilizer } from "../services/api";
import "./Fertilizer.css";

const Fertilizer = () => {
  const { t, i18n } = useTranslation();
  const [formData, setFormData] = useState({
    crop_type: "",
    soil_type: "",
    temperature: "",
    humidity: "",
    moisture: "",
    nitrogen: "",
    phosphorous: "",
    potassium: "",
  });

  const [result, setResult] = useState(null);
  const [availableCrops, setAvailableCrops] = useState([]);
  const [availableSoils, setAvailableSoils] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch available options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [cropsData, soilsData] = await Promise.all([
          fertilizer.getCropTypes(),
          fertilizer.getSoilTypes()
        ]);
        setAvailableCrops(cropsData.crop_types || []);
        setAvailableSoils(soilsData.soil_types || []);
      } catch (err) {
        console.error('Error fetching options:', err);
      }
    };
    fetchOptions();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const response = await fertilizer.recommend({
        crop_type: formData.crop_type,
        soil_type: formData.soil_type,
        temperature: parseFloat(formData.temperature),
        humidity: parseFloat(formData.humidity),
        moisture: parseFloat(formData.moisture),
        nitrogen: parseFloat(formData.nitrogen),
        phosphorous: parseFloat(formData.phosphorous),
        potassium: parseFloat(formData.potassium)
      }, i18n.language);

      setResult(response);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(t('fertilizer.failedRecommendation'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fertilizer-container">
      <h2>🌱 {t('fertilizer.title')}</h2>
      <p className="subtitle">{t('fertilizer.subtitle')}</p>

      <div className="fertilizer-content">
        <form onSubmit={handleSubmit} className="fertilizer-form">
          <div className="form-section">
            <h3>{t('fertilizer.cropInfo')}</h3>

            <div className="form-group">
              <label htmlFor="crop_type">{t('fertilizer.cropType')}</label>
              <select
                name="crop_type"
                id="crop_type"
                value={formData.crop_type}
                onChange={handleChange}
                required
              >
                <option value="">{t('fertilizer.selectCropType')}</option>
                {availableCrops.map(crop => (
                  <option key={crop} value={crop}>{crop}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="soil_type">{t('fertilizer.soilType')}</label>
              <select
                name="soil_type"
                id="soil_type"
                value={formData.soil_type}
                onChange={handleChange}
                required
              >
                <option value="">{t('fertilizer.selectSoilType')}</option>
                {availableSoils.map(soil => (
                  <option key={soil} value={soil}>{soil}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-section">
            <h3>{t('fertilizer.envConditions')}</h3>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="temperature">{t('fertilizer.temperature')}</label>
                <input
                  type="number"
                  name="temperature"
                  id="temperature"
                  placeholder="e.g., 30"
                  value={formData.temperature}
                  onChange={handleChange}
                  required
                  min="-10"
                  max="60"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="humidity">{t('fertilizer.humidity')}</label>
                <input
                  type="number"
                  name="humidity"
                  id="humidity"
                  placeholder="e.g., 60"
                  value={formData.humidity}
                  onChange={handleChange}
                  required
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="moisture">{t('fertilizer.soilMoisture')}</label>
                <input
                  type="number"
                  name="moisture"
                  id="moisture"
                  placeholder="e.g., 40"
                  value={formData.moisture}
                  onChange={handleChange}
                  required
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>{t('fertilizer.nutrientLevels')}</h3>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="nitrogen">{t('fertilizer.nitrogen')}</label>
                <input
                  type="number"
                  name="nitrogen"
                  id="nitrogen"
                  placeholder="e.g., 20"
                  value={formData.nitrogen}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phosphorous">{t('fertilizer.phosphorous')}</label>
                <input
                  type="number"
                  name="phosphorous"
                  id="phosphorous"
                  placeholder="e.g., 10"
                  value={formData.phosphorous}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="potassium">{t('fertilizer.potassium')}</label>
                <input
                  type="number"
                  name="potassium"
                  id="potassium"
                  placeholder="e.g., 15"
                  value={formData.potassium}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.1"
                />
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? t('fertilizer.gettingRecommendation') : `🔬 ${t('fertilizer.getRecommendation')}`}
          </button>
        </form>

        {result && (
          <div className="result-section">
            <h3>✅ {t('fertilizer.recommendationResult')}</h3>

            <div className="main-result">
              <div className="fertilizer-name">{result.recommended_fertilizer}</div>
              {/* <div className="confidence">
                {t('fertilizer.confidence')}: {result.confidence.toFixed(2)}%
              </div> */}
            </div>

            {result.usage_tips && (
              <div className="usage-tips">
                <h4>💡 {t('fertilizer.usageInfo')}</h4>
                <p>{result.usage_tips}</p>
              </div>
            )}

            {result.alternative_fertilizers && result.alternative_fertilizers.length > 0 && (
              <div className="alternatives">
                <h4>{t('fertilizer.alternativeOptions')}</h4>
                {result.alternative_fertilizers.map((alt, index) => (
                  <div key={index} className="alternative-item">
                    <span className="alt-name">{alt.name}</span>
                    {/* <span className="alt-confidence">{alt.confidence.toFixed(2)}%</span> */}
                  </div>
                ))}
              </div>
            )}

            <div className="result-details">
              <p><strong>{t('fertilizer.forCropInSoil')}:</strong> {result.crop_type} {t('fertilizer.inSoil')} {result.soil_type} {t('fertilizer.soil')}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Fertilizer;