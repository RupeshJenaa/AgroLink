import React, { createContext, useState, useContext, useEffect } from 'react';
import i18next from 'i18next';

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState(
    localStorage.getItem('preferredLanguage') || 'en'
  );

  useEffect(() => {
    // Initialize language
    const initLanguage = async () => {
      await i18next.changeLanguage(currentLanguage);
    };

    initLanguage();
  }, [currentLanguage]);

  const changeLanguage = async (language) => {
    setCurrentLanguage(language);
    localStorage.setItem('preferredLanguage', language);
    await i18next.changeLanguage(language);
  };

  const value = {
    currentLanguage,
    changeLanguage
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export default LanguageContext;