import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './Profile.css';

const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const Profile = () => {
  const { user, role, userState, updateProfile, loading } = useAuth();
  const [selectedState, setSelectedState] = useState('');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (userState) setSelectedState(userState);
  }, [userState]);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!selectedState) {
      setError('Please select your state.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateProfile({ state: selectedState });
      setSuccess('✅ Profile updated! Your state has been saved.');
    } catch (err) {
      setError('Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="profile-container"><p>Loading…</p></div>;

  return (
    <div className="profile-container">
      <div className="profile-card">
        <div className="profile-avatar">
          {role === 'farmer' ? '🧑‍🌾' : '🛒'}
        </div>
        <h2 className="profile-name">{user?.displayName || user?.email}</h2>
        <p className="profile-role-badge">{role}</p>
        <p className="profile-email">{user?.email}</p>

        <div className="profile-divider" />

        <form className="profile-form" onSubmit={handleSave}>
          <div className="profile-form-group">
            <label htmlFor="profile-state">
              📍 Your State / Region
            </label>
            <p className="profile-field-hint">
              This is used to auto-fill weather, crop &amp; fertilizer recommendations, and marketplace location.
            </p>
            <select
              id="profile-state"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              required
            >
              <option value="">-- Select your state --</option>
              {INDIAN_STATES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {success && <div className="profile-success">{success}</div>}
          {error && <div className="profile-error">{error}</div>}

          <button type="submit" className="profile-save-btn" disabled={saving}>
            {saving ? 'Saving…' : 'Save Profile'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Profile;
