import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import {
  FaHome,
  FaLeaf,
  FaFlask,
  FaCloudSunRain,
  FaStore,
  FaGlobe,
  FaBug,
  FaSignInAlt,
  FaUserPlus,
  FaSignOutAlt,
  FaBars,
  FaTimes
} from "react-icons/fa";
import icon from "../assets/icon.png";

import "./Navbar.css";

const Navbar = () => {
  const { t } = useTranslation();
  const { currentLanguage, changeLanguage } = useLanguage();
  const { isAuthenticated, user, role, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
      setMenuOpen(false);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const handleNavClick = () => setMenuOpen(false);

  // Base nav items (available to all visitors)
  const baseNavItems = [
    { to: "/", label: t('nav.home'), icon: <FaHome /> },
    { to: "/weather", label: t('nav.weather'), icon: <FaCloudSunRain /> },
    { to: "/marketplace", label: t('nav.marketplace'), icon: <FaStore /> },
  ];

  // Farmer-only nav items
  const farmerNavItems = [
    { to: "/crop-recommendation", label: t('nav.cropRecommendation'), icon: <FaLeaf /> },
    { to: "/fertilizer", label: t('nav.fertilizer'), icon: <FaFlask /> },
    { to: "/plant-disease", label: t('nav.plantDisease'), icon: <FaBug /> },
  ];

  // Combine nav items based on role
  const navItems = role === 'farmer'
    ? [...baseNavItems, ...farmerNavItems]
    : baseNavItems;

  // Language options for website
  const languageOptions = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'ta', name: 'தமிழ்' },
    { code: 'te', name: 'తెలుగు' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'mr', name: 'मराठी' },
    { code: 'bn', name: 'বাংলা' },
    { code: 'or', name: 'ଓଡ଼ିଆ' }
  ];

  const handleLanguageChange = (event) => {
    changeLanguage(event.target.value);
  };

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <div className="logo">
        <img src={icon} alt="AgroLink Icon" className="navbar-icon" />
        <span>AgroLink</span>
      </div>

      {/* Hamburger toggle button — only visible on mobile */}
      <button
        className={`hamburger-btn ${menuOpen ? 'open' : ''}`}
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label={menuOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={menuOpen}
        aria-controls="nav-menu"
      >
        {menuOpen ? <FaTimes /> : <FaBars />}
      </button>

      {/* Nav Menu */}
      <AnimatePresence>
        {(menuOpen || true) && (
          <motion.div
            id="nav-menu"
            className={`nav-menu ${menuOpen ? 'nav-menu--open' : ''}`}
            initial={false}
          >
            <ul className="nav-links">
              {navItems.map(({ to, label, icon }) => (
                <li key={to}>
                  <NavLink
                    to={to}
                    className={({ isActive }) => (isActive ? "active-link" : "")}
                    onClick={handleNavClick}
                  >
                    <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                      <span className="nav-icon">{icon}</span>
                      {label}
                    </motion.div>
                  </NavLink>
                </li>
              ))}
            </ul>

            {/* Right side: Language selector and Auth */}
            <div className="navbar-right">
              {/* Language Selector */}
              <div className="language-selector">
                <div className="language-link">
                  <FaGlobe className="language-icon" aria-hidden="true" />
                  <select
                    value={currentLanguage}
                    onChange={handleLanguageChange}
                    className="language-dropdown"
                    aria-label="Select language"
                  >
                    {languageOptions.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Authentication UI */}
              <div className="auth-section">
                {isAuthenticated ? (
                  <>
                    <span className="user-info">
                      {user?.email} ({role})
                    </span>
                    <button onClick={handleLogout} className="auth-button logout-button">
                      <FaSignOutAlt aria-hidden="true" /> Logout
                    </button>
                  </>
                ) : (
                  <>
                    <NavLink to="/login" className="auth-button login-button" onClick={handleNavClick}>
                      <FaSignInAlt aria-hidden="true" /> Login
                    </NavLink>
                    <NavLink to="/register" className="auth-button register-button" onClick={handleNavClick}>
                      <FaUserPlus aria-hidden="true" /> Register
                    </NavLink>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;