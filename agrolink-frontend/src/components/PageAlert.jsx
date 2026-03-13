import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./PageAlert.css";

const alerts = {
  "/": "Welcome to AgroLink — Empowering farmers through AI 🌾",
  "/crop-recommendation": "Get AI-based crop suggestions based on soil and weather data.",
  "/fertilizer": "Find the best fertilizer for your crop and soil type.",
  "/weather": "Monitor live weather conditions for informed farming decisions.",
  "/marketplace": "Buy and sell farm produce with ease on our digital marketplace.",
  "/crop": "Explore detailed information about various crops.",
  "/plant-disease": "Detect plant diseases with AI image recognition.",
  "/chatbot": "Talk to our AI-powered multilingual chatbot for instant support.",
  "/admin": "Admin panel for managing platform data and users."
};

const PageAlert = () => {
  const location = useLocation();
  const [message, setMessage] = useState("");

  useEffect(() => {
    const alertText = alerts[location.pathname] || "";
    setMessage(alertText);
  }, [location]);

  if (!message) return null;

  return (
    <div className="page-alert">
      {message}
    </div>
  );
};

export default PageAlert;
