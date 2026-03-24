// src/pages/Marketplace.jsx
import React, { useState, useEffect, useRef } from "react";
import { db } from "../firebaseConfig";
import { collection, addDoc, getDocs, query, orderBy } from "firebase/firestore";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";
import { price as priceApi } from "../services/api";
import { useTranslation } from "react-i18next";
import "./Marketplace.css";



const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const Marketplace = () => {
  const { t } = useTranslation();
  const { isAuthenticated, user, role, isFarmer, userState } = useAuth();
  const [formData, setFormData] = useState({
    crop: "",
    quantity: "",
    price: "",
    state: userState || "",
    contact: ""
  });
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [suggestedPrice, setSuggestedPrice] = useState(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState("");
  const priceFetchRef = useRef(null);

  // Only authenticated farmers can create listings
  const canCreateListing = isAuthenticated && isFarmer;

  // ── Default state to user's registered state ────────────────────────────
  useEffect(() => {
    if (userState) {
      setFormData((prev) => ({ ...prev, state: prev.state || userState }));
    }
  }, [userState]);

  // ── Fetch listings ────────────────────────────────────────────────────────
  useEffect(() => {
    const fetchListings = async () => {
      setLoading(true);
      try {
        const q = query(collection(db, "marketplace"), orderBy("createdAt", "desc"));
        const snapshot = await getDocs(q);
        const data = [];
        snapshot.forEach((doc) => data.push({ id: doc.id, ...doc.data() }));
        setListings(data);
      } catch (error) {
        console.error("Error fetching listings:", error);
        setStatus(t('marketplace.failedToLoad'));
      } finally {
        setLoading(false);
      }
    };
    fetchListings();
  }, [t]);

  // ── Auto-predict price when crop, state, quantity are all filled ──────────
  useEffect(() => {
    if (!canCreateListing) return;
    const { crop, state, quantity } = formData;
    if (!crop || !state || !quantity || isNaN(parseFloat(quantity)) || parseFloat(quantity) <= 0) {
      setSuggestedPrice(null);
      setPriceError("");
      return;
    }

    // Debounce: wait 600 ms after typing stops
    if (priceFetchRef.current) clearTimeout(priceFetchRef.current);
    priceFetchRef.current = setTimeout(async () => {
      setPriceLoading(true);
      setPriceError("");
      setSuggestedPrice(null);
      try {
        const data = await priceApi.predict({
          crop_type: crop,
          quantity: parseFloat(quantity),
          state: state
        });
        setSuggestedPrice(data.predicted_price_per_kg);
      } catch (err) {
        const msg = err.response?.data?.detail || err.message || "Price prediction failed";
        setPriceError(msg);
      } finally {
        setPriceLoading(false);
      }
    }, 600);

    return () => clearTimeout(priceFetchRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.crop, formData.state, formData.quantity, canCreateListing]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear suggestion if price is manually edited
    if (name === "price") setSuggestedPrice(null);
  };

  const applyPrice = () => {
    if (suggestedPrice !== null) {
      setFormData((prev) => ({ ...prev, price: suggestedPrice.toString() }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.crop || !formData.quantity || !formData.price || !formData.state || !formData.contact) {
      setStatus(t('marketplace.pleaseFillAllFields'));
      return;
    }
    setLoading(true);
    setStatus("");
    try {
      const listingData = {
        ...formData,
        location: formData.state,
        createdAt: new Date(),
        ...(isAuthenticated && {
          userId: user?.uid,
          userEmail: user?.email,
          userRole: role
        })
      };
      await addDoc(collection(db, "marketplace"), listingData);
      setStatus("✅ " + t('marketplace.listedSuccessfully'));
      setFormData({ crop: "", quantity: "", price: "", state: userState || "", contact: "" });
      setSuggestedPrice(null);

      // Refresh listings
      const q = query(collection(db, "marketplace"), orderBy("createdAt", "desc"));
      const snapshot = await getDocs(q);
      const data = [];
      snapshot.forEach((doc) => data.push({ id: doc.id, ...doc.data() }));
      setListings(data);
    } catch (error) {
      console.error("Error adding listing:", error);
      setStatus(error.code === "permission-denied"
        ? t('marketplace.permissionDenied')
        : t('marketplace.failedToList'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="marketplace-container">
      <h2>🛒 {t('marketplace.buyCrops')}</h2>

      {/* ── Listings ── */}
      <div className="listings-container">
        {loading ? (
          <p>{t('marketplace.loadingListings')}</p>
        ) : (
          <div className="listings-grid">
            {listings.length === 0 ? (
              <p>{t('marketplace.noListings')}</p>
            ) : (
              listings.map((listing) => (
                <div key={listing.id} className="listing-card">
                  <h3>🌾 {listing.crop}</h3>
                  <p><strong>{t('marketplace.quantity')}:</strong> {listing.quantity} kg</p>
                  <p><strong>{t('marketplace.price')}:</strong> ₹{listing.price} / kg</p>
                  <p><strong>{t('marketplace.location')}:</strong> {listing.location || listing.state}</p>
                  <p><strong>{t('marketplace.contact')}:</strong> {listing.contact}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* ── Add Listing (farmers only) ── */}
      {canCreateListing ? (
        <>
          <h2>🌱 {t('marketplace.sellYourCrop')}</h2>
          <form onSubmit={handleSubmit} className="crop-form">
            <input
              name="crop"
              value={formData.crop}
              onChange={handleChange}
              placeholder={t('marketplace.cropName')}
              required
            />
            <select
              name="state"
              value={formData.state}
              onChange={handleChange}
              required
              className="crop-form-select"
            >
              <option value="">{t('marketplace.locationPlaceholder')}</option>
              {INDIAN_STATES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <input
              name="quantity"
              type="number"
              min="1"
              value={formData.quantity}
              onChange={handleChange}
              placeholder={t('marketplace.quantityPlaceholder')}
              required
            />

            <div className="price-field-group">
              <input
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={formData.price}
                onChange={handleChange}
                placeholder={t('marketplace.pricePlaceholder')}
                required
              />
              {priceLoading && (
                <div className="price-hint price-hint--loading">
                  ⏳ Fetching suggested price…
                </div>
              )}
              {!priceLoading && priceError && (
                <div className="price-hint price-hint--error">
                  ⚠️ {priceError}
                </div>
              )}
              {!priceLoading && suggestedPrice !== null && (
                <div className="price-hint price-hint--suggestion">
                  💡 AI Suggested Price: <strong>₹{suggestedPrice.toFixed(2)}/kg</strong>
                  <button type="button" className="use-price-btn" onClick={applyPrice}>
                    Use this price
                  </button>
                </div>
              )}
            </div>

            <input
              name="contact"
              value={formData.contact}
              onChange={handleChange}
              placeholder={t('marketplace.contactPlaceholder')}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? t('marketplace.listing') : t('marketplace.listCrop')}
            </button>
          </form>
        </>
      ) : isAuthenticated ? (
        <div className="role-notice">
          <h3>🚫 Farmers Only</h3>
          <p>Only farmers can create crop listings. You are logged in as a <strong>customer</strong>.</p>
          <p>Browse the listings above to find crops and contact sellers.</p>
        </div>
      ) : (
        <div className="role-notice">
          <h3>Want to sell crops?</h3>
          <p>Please <Link to="/register">register as a farmer</Link> or <Link to="/login">log in</Link> to list your crops.</p>
        </div>
      )}

      {status && <p className="status-message">{status}</p>}
    </div>
  );
};

export default Marketplace;