import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { price } from '../services/api';
import './PricePrediction.css';

const PricePrediction = () => {
    const { t, i18n } = useTranslation();
    const [formData, setFormData] = useState({
        crop_type: '',
        quantity: '',
        state: ''
    });
    const [prediction, setPrediction] = useState(null);
    const [availableCrops, setAvailableCrops] = useState([]);
    const [availableStates, setAvailableStates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { isFarmer } = useAuth();

    // Fetch available crops and states on component mount
    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const [cropsData, statesData] = await Promise.all([
                    price.getCrops(),
                    price.getStates()
                ]);
                setAvailableCrops(cropsData.crops || []);
                setAvailableStates(statesData.states || []);
            } catch (err) {
                console.error('Error fetching options:', err);
            }
        };
        fetchOptions();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setPrediction(null);

        if (!formData.crop_type || !formData.quantity || !formData.state) {
            setError('Please fill in all fields');
            return;
        }

        setLoading(true);

        try {
            const result = await price.predict({
                crop_type: formData.crop_type,
                quantity: parseFloat(formData.quantity),
                state: formData.state
            }, i18n.language);
            setPrediction(result);
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Failed to get price prediction. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (!isFarmer) {
        return (
            <div className="price-prediction-container">
                <div className="access-denied">
                    <h2>Farmer-Only Feature</h2>
                    <p>Price prediction is only available to farmers.</p>
                    <p>Please register as a farmer to access this feature.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="price-prediction-container">
            <h2>🌾 Crop Price Prediction</h2>
            <p className="subtitle">Get estimated market price for your crops</p>

            <div className="price-content">
                <div className="prediction-form-section">
                    <form onSubmit={handleSubmit} className="prediction-form">
                        <div className="form-group">
                            <label htmlFor="crop_type">Crop Type</label>
                            <input
                                type="text"
                                id="crop_type"
                                name="crop_type"
                                value={formData.crop_type}
                                onChange={handleChange}
                                placeholder="e.g. Rice, Tomato, Wheat..."
                                list="crop-suggestions"
                                required
                                autoComplete="off"
                            />
                            <datalist id="crop-suggestions">
                                {availableCrops.map(crop => (
                                    <option key={crop} value={crop} />
                                ))}
                            </datalist>
                        </div>

                        <div className="form-group">
                            <label htmlFor="quantity">Quantity (kg)</label>
                            <input
                                type="number"
                                id="quantity"
                                name="quantity"
                                value={formData.quantity}
                                onChange={handleChange}
                                placeholder="Enter quantity in kg"
                                min="1"
                                step="1"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="state">State/Location</label>
                            <select
                                id="state"
                                name="state"
                                value={formData.state}
                                onChange={handleChange}
                                required
                            >
                                <option value="">Select state</option>
                                {availableStates.map(state => (
                                    <option key={state} value={state}>{state}</option>
                                ))}
                            </select>
                        </div>

                        {error && <div className="error-message">{error}</div>}

                        <button type="submit" className="predict-button" disabled={loading}>
                            {loading ? 'Predicting...' : '💰 Get Price Prediction'}
                        </button>
                    </form>
                </div>

                {prediction && (
                    <div className="prediction-results">
                        <h3>Price Prediction Results</h3>

                        <div className="result-card main-prediction">
                            <div className="result-label">Predicted Price per kg</div>
                            <div className="result-value price">₹{prediction.predicted_price_per_kg.toFixed(2)}</div>
                        </div>

                        <div className="result-card">
                            <div className="result-label">Total Estimated Value</div>
                            <div className="result-value">₹{prediction.predicted_total_value.toLocaleString('en-IN')}</div>
                        </div>

                        <div className="confidence-range">
                            <h4>Price Range (Confidence Interval)</h4>
                            <div className="range-display">
                                <span className="range-low">₹{prediction.confidence_interval_low.toFixed(2)}</span>
                                <span className="range-separator">—</span>
                                <span className="range-high">₹{prediction.confidence_interval_high.toFixed(2)}</span>
                            </div>
                            <p className="range-note">The actual market price is likely to fall within this range</p>
                        </div>

                        {prediction.historical_average && (
                            <div className="historical-info">
                                <p>📊 Historical Average: ₹{prediction.historical_average.toFixed(2)} per kg</p>
                            </div>
                        )}

                        <div className="prediction-details">
                            <p><strong>Crop:</strong> {prediction.crop_type}</p>
                            <p><strong>Quantity:</strong> {prediction.quantity} kg</p>
                            <p><strong>Location:</strong> {prediction.state}</p>
                            <p><strong>Current Month:</strong> {new Date(0, prediction.current_month - 1).toLocaleString('default', { month: 'long' })}</p>
                        </div>

                        <div className="info-note">
                            <strong>💡 Note:</strong> This prediction is based on historical data and current market trends.
                            Actual prices may vary based on quality, demand, and local market conditions.
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PricePrediction;
