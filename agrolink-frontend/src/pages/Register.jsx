import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Register.css';

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const Register = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'farmer',
        state: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleRoleSelect = (role) => {
        setFormData({ ...formData, role });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
            setError('Please fill in all fields');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        try {
            setError('');
            setLoading(true);

            const result = await register(
                formData.email,
                formData.password,
                formData.name,
                formData.role,
                formData.state
            );

            if (result.success) {
                navigate('/');
            }
        } catch (err) {
            setError(getFriendlyErrorMessage(err.code || err.message));
        } finally {
            setLoading(false);
        }
    };

    const getFriendlyErrorMessage = (errorCode) => {
        switch (errorCode) {
            case 'auth/email-already-in-use':
                return 'An account with this email already exists';
            case 'auth/invalid-email':
                return 'Invalid email address format';
            case 'auth/weak-password':
                return 'Password is too weak. Use at least 6 characters';
            default:
                return 'Failed to create account. Please try again.';
        }
    };

    return (
        <div className="register-container">
            {/* Floating particles */}
            <div className="login-particles" aria-hidden="true">
                {[...Array(8)].map((_, i) => (
                    <div
                        key={i}
                        className="particle"
                        style={{
                            left: `${10 + i * 11}%`,
                            width: `${6 + (i % 3) * 4}px`,
                            height: `${6 + (i % 3) * 4}px`,
                            animationDuration: `${8 + i * 1.5}s`,
                            animationDelay: `${i * 1.2}s`,
                        }}
                    />
                ))}
            </div>

            <div className="register-box" role="main">
                {/* Brand
                <div className="register-brand">
                    <div className="register-brand-icon" aria-hidden="true">🌾</div>
                    <span className="register-brand-name">AgroLink</span>
                </div> */}

                <h1 className="sr-only">AgroLink Registration</h1>
                <h2>Join AgroLink</h2>
                <p className="register-subtitle">Create your farming account today</p>

                {error && <div className="error-message" role="alert">{error}</div>}

                <form onSubmit={handleSubmit} className="register-form" noValidate>
                    <div className="form-group">
                        <label htmlFor="name">Full Name</label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Enter your full name"
                            required
                            aria-required="true"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Enter your email"
                            required
                            autoComplete="email"
                            aria-required="true"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Create a password (min 6 characters)"
                            required
                            autoComplete="new-password"
                            aria-required="true"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            placeholder="Confirm your password"
                            required
                            autoComplete="new-password"
                            aria-required="true"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="state">Your State</label>
                        <select
                            id="state"
                            name="state"
                            value={formData.state}
                            onChange={handleChange}
                            required
                            aria-required="true"
                            style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '10px', border: '1.5px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.08)', color: 'inherit', fontSize: '1rem', marginTop: '0.25rem' }}
                        >
                            <option value="">-- Select your state --</option>
                            {INDIAN_STATES.map((s) => (
                                <option key={s} value={s} style={{ background: '#1a2a1a', color: '#fff' }}>{s}</option>
                            ))}
                        </select>
                    </div>

                    {/* Role Selector — visual card toggle */}
                    <div className="form-group">
                        <label>I am a:</label>
                        <div className="role-selector" role="group" aria-label="Select your role">
                            <button
                                type="button"
                                className={`role-option ${formData.role === 'farmer' ? 'active' : ''}`}
                                onClick={() => handleRoleSelect('farmer')}
                                aria-pressed={formData.role === 'farmer'}
                            >
                                <span className="role-icon">🧑‍🌾</span>
                                <span>Farmer</span>
                            </button>
                            <button
                                type="button"
                                className={`role-option ${formData.role === 'customer' ? 'active' : ''}`}
                                onClick={() => handleRoleSelect('customer')}
                                aria-pressed={formData.role === 'customer'}
                            >
                                <span className="role-icon">🛒</span>
                                <span>Customer</span>
                            </button>
                        </div>
                        {/* Hidden input to keep form data aligned */}
                        <input type="hidden" name="role" value={formData.role} />
                    </div>

                    <button
                        type="submit"
                        className="register-button"
                        disabled={loading}
                        aria-busy={loading}
                    >
                        {loading ? 'Creating Account…' : 'Create Account'}
                    </button>
                </form>

                <div className="register-footer">
                    <p>
                        Already have an account?{' '}
                        <Link to="/login" className="login-link">
                            Sign in here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register;
