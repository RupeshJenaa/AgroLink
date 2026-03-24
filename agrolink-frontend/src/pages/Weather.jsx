import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Weather.css';

const Weather = () => {
  const { userState } = useAuth();
  const [city, setCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_KEY = 'be2858ba0d7ed98919cb67658c1a5da6';

  const fetchWeatherForCity = async (cityName) => {
    if (!cityName) return;
    setLoading(true);
    try {
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?q=${cityName},IN&units=metric&appid=${API_KEY}`
      );
      const data = await response.json();
      if (data.cod === 200) {
        setWeatherData(data);
      } else {
        setWeatherData(null);
        alert('City / state not found. Try a major city name.');
      }
    } catch (error) {
      alert('Error fetching weather');
    }
    setLoading(false);
  };

  // Auto-fetch when user's state is available
  useEffect(() => {
    if (userState) {
      setCity(userState);
      fetchWeatherForCity(userState);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userState]);

  return (
    <div className="weather-container">
      <h2>🌤️ Weather Monitoring</h2>
      {userState && (
        <p style={{ fontSize: '0.9rem', color: '#7ecb6f', marginBottom: '0.5rem' }}>
          📍 Showing weather for your region: <strong>{userState}</strong>
        </p>
      )}
      <div className="input-group">
        <input
          type="text"
          placeholder="Enter city or state name..."
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && fetchWeatherForCity(city)}
        />
        <button onClick={() => fetchWeatherForCity(city)}>Check Weather</button>
      </div>

      {loading && <p>Loading...</p>}

      {weatherData && (
        <div className="weather-info">
          <h3>{weatherData.name}</h3>
          <p><strong>Temperature:</strong> {weatherData.main.temp}°C</p>
          <p><strong>Feels Like:</strong> {weatherData.main.feels_like}°C</p>
          <p><strong>Humidity:</strong> {weatherData.main.humidity}%</p>
          <p><strong>Pressure:</strong> {weatherData.main.pressure} hPa</p>
          <p><strong>Wind Speed:</strong> {weatherData.wind.speed} m/s</p>
          <p><strong>Condition:</strong> {weatherData.weather[0].description}</p>
          {weatherData.rain && (
            <p><strong>Rainfall (1h):</strong> {weatherData.rain['1h'] || weatherData.rain['3h'] || 0} mm</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Weather;
