import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import all translation files
import translationEN from './locales/en.json';
import translationHI from './locales/hi.json';
import translationTE from './locales/te.json';
import translationTA from './locales/ta.json';
import translationKN from './locales/kn.json';
import translationMR from './locales/mr.json';
import translationBN from './locales/bn.json';
import translationOR from './locales/or.json';

const resources = {
  en: {
    translation: translationEN,
  },
  hi: {
    translation: translationHI,
  },
  te: {
    translation: translationTE,
  },
  ta: {
    translation: translationTA,
  },
  kn: {
    translation: translationKN,
  },
  mr: {
    translation: translationMR,
  },
  bn: {
    translation: translationBN,
  },
  or: {
    translation: translationOR,
  },
};

i18next
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('preferredLanguage') || 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18next;