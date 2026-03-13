import React from "react";
import { DotLottieReact } from "@lottiefiles/dotlottie-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  FaLeaf,
  FaFlask,
  FaCloudSunRain,
  FaStore,
  FaRobot,
  FaBug,
  FaGlobeAmericas,
  FaSeedling,
  FaChartLine,
  FaArrowRight
} from "react-icons/fa";
import { useTranslation } from 'react-i18next';
import "./Home.css";

const Home = ({ setIsChatbotOpen }) => {
  const { t } = useTranslation();

  const features = [
    {
      icon: <FaLeaf />,
      title: t('home.cropRecommendation'),
      description: t('home.cropRecommendationDesc'),
      link: "/crop-recommendation"
    },
    {
      icon: <FaFlask />,
      title: t('home.fertilizerAdvisor'),
      description: t('home.fertilizerAdvisorDesc'),
      link: "/fertilizer"
    },
    {
      icon: <FaCloudSunRain />,
      title: t('home.weatherForecast'),
      description: t('home.weatherForecastDesc'),
      link: "/weather"
    },
    {
      icon: <FaStore />,
      title: t('home.marketplace'),
      description: t('home.marketplaceDesc'),
      link: "/marketplace"
    },
    {
      icon: <FaBug />,
      title: t('home.plantDisease'),
      description: t('home.plantDiseaseDesc'),
      link: "/plant-disease"
    }
  ];

  const benefits = [
    {
      icon: <FaRobot />,
      title: t('home.aiInsights'),
      description: t('home.aiInsightsDesc')
    },
    {
      icon: <FaGlobeAmericas />,
      title: t('home.multilingualSupport'),
      description: t('home.multilingualSupportDesc')
    },
    {
      icon: <FaSeedling />,
      title: t('home.sustainableFarming'),
      description: t('home.sustainableFarmingDesc')
    },
    {
      icon: <FaChartLine />,
      title: t('home.increasedYield'),
      description: t('home.increasedYieldDesc')
    }
  ];

  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-container">
        <div className="hero-content">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            {t('home.welcome')} <br /><span className="highlight">Eco Solution</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          >
            {t('home.subtitle')}
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
            className="hero-buttons"
          >
            <Link to="/crop-recommendation" className="cta-button primary">
              {t('home.getStarted')}
            </Link>
            <button
              className="cta-button secondary"
              onClick={() => setIsChatbotOpen(true)}
            >
              {t('home.chatNow')}
            </button>
          </motion.div>
        </div>

        <motion.div
          className="hero-animation"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
        >
          <DotLottieReact
            src="https://lottie.host/3cfa005a-2714-4841-b477-df6a35039a3c/bNy739FZOs.lottie"
            loop
            autoplay
            style={{ width: "100%", maxWidth: "600px" }}
          />
        </motion.div>
      </div>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2>{t('home.solutionsTitle')}</h2>
            <p>{t('home.solutionsDesc')}</p>
          </motion.div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="feature-card"
              >
                <Link to={feature.link} className="feature-link">
                  <div className="feature-icon">
                    {feature.icon}
                  </div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                  <span className="card-arrow"><FaArrowRight /></span>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2>{t('home.whyChoose')}</h2>
            <p>{t('home.whyChooseDesc')}</p>
          </motion.div>

          <div className="benefits-grid">
            {benefits.map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="benefit-card"
              >
                <div className="benefit-icon">
                  {benefit.icon}
                </div>
                <h3>{benefit.title}</h3>
                <p>{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="cta-content"
          >
            <h2>{t('home.transformTitle')}</h2>
            <p>{t('home.transformDesc')}</p>
            <div className="cta-buttons">
              <Link to="/register" className="cta-button primary large">
                {t('home.createAccount')}
              </Link>
              <Link to="/login" className="cta-button secondary large">
                {t('common.login')}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;