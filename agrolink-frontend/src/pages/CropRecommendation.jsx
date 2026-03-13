import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './CropRecommendation.css';

function CropRecommendation() {
  const { t, i18n } = useTranslation();
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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`http://localhost:8000/api/crop/predict?lang=${i18n.language}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setResult(`Recommended crop: ${data.recommended_crop}`);
      } else {
        setResult(`Error: ${data.error || 'Something went wrong'}`);
      }
    } catch (error) {
      console.error('API Error:', error);
      setResult(t('crop.connectionError'));
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