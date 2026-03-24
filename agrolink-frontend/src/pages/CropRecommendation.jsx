import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { crop } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './CropRecommendation.css';

const OWM_API_KEY = 'be2858ba0d7ed98919cb67658c1a5da6';

function CropRecommendation() {
  const { t, i18n } = useTranslation();
  const { userState } = useAuth();
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorous: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: '',
  });

  const [result, setResult] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherNote, setWeatherNote] = useState('');

  // Auto-fill weather fields from user's state
  useEffect(() => {
    if (!userState) return;
    const fetchWeather = async () => {
      setWeatherLoading(true);
      try {
        const res = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?q=${userState},IN&units=metric&appid=${OWM_API_KEY}`
        );
        const data = await res.json();
        if (data.cod === 200) {
          const rainfall = data.rain ? (data.rain['1h'] || data.rain['3h'] || 0) : 0;
          setFormData((prev) => ({
            ...prev,
            temperature: data.main.temp.toFixed(1),
            humidity: data.main.humidity.toFixed(1),
            rainfall: rainfall.toFixed(1),
          }));
          setWeatherNote(`🌤️ Weather auto-filled from ${data.name} (${userState})`);
        }
      } catch {
        // Silently fail; user can fill manually
      } finally {
        setWeatherLoading(false);
      }
    };
    fetchWeather();
  }, [userState]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = await crop.predict(formData, i18n.language);

      setResult(`Recommended crop: ${data.recommended_crop}`);
    } catch (error) {
      console.error('API Error:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Something went wrong';
      if (error.response) {
        setResult(`Error: ${errorMsg}`);
      } else {
        setResult(t('crop.connectionError'));
      }
    }
  };

  const fields = [
    { name: 'nitrogen', label: t('crop.nitrogen') },
    { name: 'phosphorous', label: t('crop.phosphorous') },
    { name: 'potassium', label: t('crop.potassium') },
    { name: 'temperature', label: t('crop.temperature') },
    { name: 'humidity', label: t('crop.humidity') },
    { name: 'ph', label: t('crop.ph') },
    { name: 'rainfall', label: t('crop.rainfall') }
  ];

  return (
    <div className="crop-container">
      <h2>{t('crop.title')}</h2>
      {weatherLoading && <p style={{ color: '#7ecb6f', fontSize: '0.9rem' }}>⏳ Fetching weather for {userState}…</p>}
      {!weatherLoading && weatherNote && (
        <p style={{ color: '#7ecb6f', fontSize: '0.9rem', marginBottom: '0.75rem' }}>{weatherNote}</p>
      )}
      <form className="crop-form" onSubmit={handleSubmit}>
        {fields.map((field) => (
          <div key={field.name}>
            <label>{field.label}:</label>
            <input
              type="number"
              name={field.name}
              value={formData[field.name]}
              onChange={handleChange}
              required
              step="any"
            />
          </div>
        ))}

        <button type="submit">{t('crop.getRecommendation')}</button>
      </form>

      {result && (
        <div className="crop-result">
          <strong>{result}</strong>
        </div>
      )}
    </div>
  );
}

export default CropRecommendation;