// src/App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import CropRecommendation from './pages/CropRecommendation';
import Fertilizer from './pages/Fertilizer';
import Weather from './pages/Weather';
import Marketplace from "./pages/Marketplace";
import Crop from "./pages/Crop";
import PlantDisease from "./pages/PlantDisease";
import Chatbot from "./pages/Chatbot";
import AdminPanel from "./pages/AdminPanel";
import Login from "./pages/Login";
import Register from "./pages/Register";

import Navbar from "./components/Navbar";
import PageAlert from './components/PageAlert';
import ProtectedRoute from './components/ProtectedRoute';
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider } from './context/AuthContext';

// Import i18n initialization
import './i18n';

function App() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  return (
    <Router>
      <AuthProvider>
        <LanguageProvider>
          <Navbar />
          <PageAlert />
          {/* Only render the chatbot with props when controlled by other components */}
          <Chatbot isOpen={isChatbotOpen} onClose={setIsChatbotOpen} />

          <Routes>
            <Route path="/" element={<Home setIsChatbotOpen={setIsChatbotOpen} />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Public routes (visible to all) */}
            <Route path="/weather" element={<Weather />} />
            <Route path="/marketplace" element={<Marketplace />} />

            {/* Farmer-only routes */}
            <Route
              path="/crop-recommendation"
              element={
                <ProtectedRoute requiredRole="farmer">
                  <CropRecommendation />
                </ProtectedRoute>
              }
            />
            <Route
              path="/fertilizer"
              element={
                <ProtectedRoute requiredRole="farmer">
                  <Fertilizer />
                </ProtectedRoute>
              }
            />
            <Route
              path="/plant-disease"
              element={
                <ProtectedRoute requiredRole="farmer">
                  <PlantDisease />
                </ProtectedRoute>
              }
            />
            <Route
              path="/crop"
              element={
                <ProtectedRoute requiredRole="farmer">
                  <Crop />
                </ProtectedRoute>
              }
            />

            {/* Admin route */}
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </LanguageProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;