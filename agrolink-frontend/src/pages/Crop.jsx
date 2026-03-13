import React, { useState } from "react";
import "./Crop.css";

const Crop = () => {
  const [formData, setFormData] = useState({
    nitrogen: "",
    phosphorus: "",
    potassium: "",
    temperature: "",
    humidity: "",
    ph: "",
    rainfall: "",
  });

  const [recommendedCrop, setRecommendedCrop] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 👇 Replace this later with a real API call
    setRecommendedCrop("Wheat"); // Dummy response
  };

  return (
    <div className="crop-container">
      <h2>🌾 Crop Recommendation</h2>

      <form onSubmit={handleSubmit} className="crop-form">
        {["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"].map((field) => (
          <input
            key={field}
            type="number"
            name={field}
            value={formData[field]}
            onChange={handleChange}
            placeholder={`Enter ${field}`}
            required
          />
        ))}

        <button type="submit">Get Recommendation</button>
      </form>

      {recommendedCrop && (
        <div className="result">
          ✅ Recommended Crop: <strong>{recommendedCrop}</strong>
        </div>
      )}
    </div>
  );
};

export default Crop;
