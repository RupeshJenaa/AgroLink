import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from 'react-i18next';
import { chatbot } from '../services/api';
import "../components/Chatbot.css";
import botIcon from "../assets/icons8-chatbot.gif";

const Chatbot = ({ isOpen: externalIsOpen, onClose: externalOnClose }) => {
  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [chatbotLanguage, setChatbotLanguage] = useState("en");
  const { t } = useTranslation();
  const [chat, setChat] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const suggestions = [
    "What crops grow well in my soil?",
    "How to fertilize my field?",
    "When to plant rice?",
    "How to prevent plant diseases?"
  ];
  const chatBodyRef = useRef(null);

  // Use external state if provided, otherwise use internal state
  const isOpen = externalIsOpen !== undefined ? externalIsOpen : internalIsOpen;
  const setIsOpen = externalOnClose !== undefined ? externalOnClose : setInternalIsOpen;

  // Scroll to bottom of chat when new messages are added
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [chat, isTyping]);

  // Reset chat when chatbot language changes
  useEffect(() => {
    // Set initial message based on chatbot language
    const initialMessages = {
      en: "Hello! I'm your AI-powered farming assistant. Ask me anything about crops, fertilizers, weather, or plant diseases!",
      hi: "नमस्ते! मैं आपका एआई-संचालित कृषि सहायक हूँ। फसलों, उर्वरकों, मौसम या पौधों की बीमारियों के बारे में मुझसे कुछ भी पूछें!",
      or: "ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର ଏଆଇ-ସଞ୍ଚାଳିତ କୃଷି ସହାୟକ ଅଟେ। ଫସଲ, ଉର୍ବରକ, ପାଣିପାଗ, କିମ୍ବା ଗଛର ରୋଗ ବିଷୟରେ ମୋତେ ଯାହା ଖୁବ୍ ପଚାରନ୍ତୁ!",
      bn: "হ্যালো! আমি আপনার এআই-চালিত কৃষি সহকারী। ফসল, সার, আবহাওয়া বা গাছের রোগ সম্পর্কে আমাকে যেকোনো কিছু জিজ্ঞাসা করুন!",
      ta: "ஹலோ! நான் உங்கள் எஆஇ-இயக்கப்படும் விவசாய உதவியாளர். பயிர்கள், உரங்கள், வானிலை அல்லது தாவர நோய்கள் பற்றி என்னிடம் எதையும் கேளுங்கள்!",
      te: "హలో! నేను మీ ఎఆఐ-ఆధారిత వ్యవసాయ సహాయకుడిని. పంటలు, ఎరువులు, వాతావరణం లేదా మొక్కల రోగాల గురించి నాకు ఏదైనా అడగండి!",
      kn: "ಹಲೋ! ನಾನು ನಿಮ್ಮ ಎಐ-ಚಾಲಿತ ಕೃಷಿ ಸಹಾಯಕನಾಗಿದ್ದೇನೆ. ಬೆಳೆಗಳು, ಗೊಬ್ಬರಗಳು, ಹವಾಮಾನ ಅಥವಾ ಸಸ್ಯ ರೋಗಗಳ ಬಗ್ಗೆ ನನಗೆ ಏನು ಕೇಳಿ!",
      mr: "हॅलो! मी तुमचा एआय-आधारित कृषी सहाय्यक आहे. पीक, खत, हवामान किंवा वनस्पती रोगांविषयी मला काहीही विचारा!"
    };

    setChat([{ type: "bot", message: initialMessages[chatbotLanguage] || initialMessages.en }]);
  }, [chatbotLanguage]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setChat((prev) => [...prev, { type: "user", message: input }]);

    setInput("");
    setIsTyping(true);
    try {
      console.log("Sending question:", input, "in language:", chatbotLanguage);
      const data = await chatbot.ask(input, chatbotLanguage);

      console.log("Received response:", data);

      // Check if we got a valid response
      if (data && data.reply) {
        setChat((prev) => [...prev, { type: "bot", message: data.reply }]);
      } else {
        // Handle case where no response is returned
        setChat((prev) => [
          ...prev,
          { type: "bot", message: t('chatbot.connection_error') || "Sorry, I'm having trouble connecting. Please try again." },
        ]);
      }
    } catch (err) {
      console.error("Chatbot error:", err);
      // More specific error handling
      let errorMessage = t('chatbot.connection_error') || "Sorry, I'm having trouble connecting. Please try again.";
      if (err.message && err.message.includes('Unexpected token')) {
        errorMessage = "Sorry, there was a problem processing your request. Please try again or switch to English.";
      }
      setChat((prev) => [
        ...prev,
        { type: "bot", message: errorMessage },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    // Auto-send after a short delay to improve UX
    setTimeout(() => {
      handleSend();
    }, 300);
  };

  // Language options for chatbot
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

  return (
    <>
      {/* Chatbot Toggle Button - Show when chatbot is closed, regardless of external control */}
      {!isOpen && (
        <button className="chatbot-toggle enhanced" onClick={() => setIsOpen(true)}>
          <div className="chatbot-icon-container">
            <img src={botIcon} alt="Chatbot" />
            <span className="notification-dot"></span>
          </div>
        </button>
      )}

      {/* Chatbot UI */}
      {isOpen && (
        <div className="chatbot-container enhanced">
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <div className="chatbot-avatar">
                <img src={botIcon} alt="Chatbot" />
              </div>
              <div className="chatbot-header-text">
                <h3>AgroLink Assistant</h3>
                <p>Your AI-powered farming assistant</p>
              </div>
            </div>
            <div className="chatbot-header-actions">
              <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
            </div>
          </div>

          <div className="chatbot-body" ref={chatBodyRef}>
            {/* Language selection for chatbot */}
            <div className="chatbot-language-selector">
              <label htmlFor="chatbot-language">{t('common.selectLanguage')}:</label>
              <select
                id="chatbot-language"
                value={chatbotLanguage}
                onChange={(e) => setChatbotLanguage(e.target.value)}
                className="language-dropdown"
              >
                {languageOptions.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Suggestions */}
            {chat.length === 1 && (
              <div className="suggestions-container">
                <p className="suggestions-title">Try asking:</p>
                <div className="suggestions">
                  {suggestions.slice(0, 4).map((suggestion, index) => (
                    <button
                      key={index}
                      className="suggestion-button"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="chat-messages">
              {chat.map((msg, i) => (
                <div key={i} className={`chat-message ${msg.type}`}>
                  {msg.type === "bot" && (
                    <div className="message-avatar">
                      <img src={botIcon} alt="Bot" />
                    </div>
                  )}
                  <div className="message-content">
                    <div className="message-text">{msg.message}</div>
                  </div>
                  {msg.type === "user" && (
                    <div className="message-avatar user-avatar">
                      <span>👤</span>
                    </div>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="chat-message bot typing-indicator">
                  <div className="message-avatar">
                    <img src={botIcon} alt="Bot" />
                  </div>
                  <div className="message-content">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="chatbot-footer">
            <textarea
              placeholder="Ask me anything about farming..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              rows="1"
            />
            <button
              className="send-button"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;