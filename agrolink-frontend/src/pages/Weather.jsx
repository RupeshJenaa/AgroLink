import React, { useState } from 'react';
import './Weather.css';

const Weather = () => {
  const [city, setCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_KEY = 'be2858ba0d7ed98919cb67658c1a5da6'; // Replace with your OpenWeatherMap API key

  const fetchWeather = async () => {
    if (!city) return;
    setLoading(true);
    try {
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${API_KEY}`
      );
      const data = await response.json();
      if (data.cod === 200) {
        setWeatherData(data);
      } else {
        setWeatherData(null);
        alert('City not found');
      }
    } catch (error) {
      alert('Error fetching weather');
    }
    setLoading(false);
  };

  return (
    <div className="weather-container">
      <h2>🌤️ Weather Monitoring</h2>
      <div className="input-group">
        <input
          type="text"
          placeholder="Enter city name..."
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />
        <button onClick={fetchWeather}>Check Weather</button>
      </div>

      {loading && <p>Loading...</p>}

      {weatherData && (
        <div className="weather-info">
          <h3>{weatherData.name}</h3>
          <p><strong>Temperature:</strong> {weatherData.main.temp}°C</p>
          <p><strong>Humidity:</strong> {weatherData.main.humidity}%</p>
          <p><strong>Condition:</strong> {weatherData.weather[0].description}</p>
        </div>
      )}
    </div>
  );
};

export default Weather;
