// src/pages/AdminPanel.jsx
import React, { useEffect, useState, useCallback } from "react";
import { db } from "../firebaseConfig"; // ✅ consistent import
import { collection, getDocs, deleteDoc, doc, updateDoc } from "firebase/firestore";
import { motion } from "framer-motion";
import "./AdminPanel.css";

const AdminPanel = () => {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editFormData, setEditFormData] = useState({
    crop: "",
    quantity: "",
    price: "",
    location: "",
    contact: ""
  });
  const [error, setError] = useState("");

  const fetchListings = useCallback(async () => {
    try {
      console.log("Fetching listings from Firebase...");
      setLoading(true);
      setError("");
      
      const querySnapshot = await getDocs(collection(db, "marketplace"));
      console.log("Query snapshot size:", querySnapshot.size);
      
      const data = querySnapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      
      console.log("Fetched data:", data);
      setListings(data);
    } catch (error) {
      console.error("Error fetching listings:", error);
      setError(`Failed to fetch listings: ${error.message}`);
      if (error.code === 'permission-denied') {
        setError("Permission denied. Please contact the administrator to update Firebase security rules.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  const handleDelete = async (id) => {
    try {
      await deleteDoc(doc(db, "marketplace", id));
      setListings((prev) => prev.filter((listing) => listing.id !== id));
    } catch (error) {
      console.error("Error deleting listing:", error);
      if (error.code === 'permission-denied') {
        setError("Permission denied. You don't have permission to delete listings.");
      } else {
        setError("Failed to delete listing. Please try again.");
      }
    }
  };

  const handleEditClick = (listing) => {
    setEditingId(listing.id);
    setEditFormData({
      crop: listing.crop || "",
      quantity: listing.quantity || "",
      price: listing.price || "",
      location: listing.location || "",
      contact: listing.contact || ""
    });
  };

  const handleEditChange = (e) => {
    setEditFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleUpdate = async (e, id) => {
    e.preventDefault();

    try {
      const listingRef = doc(db, "marketplace", id);
      await updateDoc(listingRef, { ...editFormData });

      setListings((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, ...editFormData } : item
        )
      );
      setEditingId(null);
    } catch (error) {
      console.error("Error updating listing:", error);
      if (error.code === 'permission-denied') {
        setError("Permission denied. You don't have permission to update listings.");
      } else {
        setError("Failed to update listing. Please try again.");
      }
    }
  };

  const filteredListings = listings.filter((listing) =>
    listing.crop?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    listing.location?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <motion.div
      className="admin-panel-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2>📋 Admin Panel – Crop Listings</h2>
      <div className="admin-header">
        <p>Total listings: {listings.length}</p>
        <button className="refresh-btn" onClick={fetchListings} disabled={loading}>
          {loading ? "🔄 Refreshing..." : "🔄 Refresh"}
        </button>
      </div>
      <p>Filtered listings: {filteredListings.length}</p>

      {/* Error message */}
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          {error.includes("Permission denied") && (
            <div>
              <p><strong>🔧 How to fix permission issues:</strong></p>
              <ol>
                <li>Go to Firebase Console → Firestore Database → Rules</li>
                <li>Update rules to allow read/write access</li>
                <li>Example rule: <code>allow read, write: if true;</code></li>
                <li>Click "Publish" to save changes</li>
              </ol>
            </div>
          )}
        </div>
      )}

      {/* 🔍 Search Bar */}
      <input
        type="text"
        placeholder="Search by crop or location..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-bar"
      />

      {loading ? (
        <p>Loading...</p>
      ) : filteredListings.length === 0 ? (
        <div>
          <p>No matching listings found.</p>
          {listings.length === 0 && !error && (
            <p>There are no listings in the database. Try adding some listings first.</p>
          )}
        </div>
      ) : (
        <div className="admin-listings">
          {filteredListings.map((listing) => (
            <div className="admin-card" key={listing.id}>
              <h3>{listing.crop}</h3>
              <p><strong>Quantity:</strong> {listing.quantity} kg</p>
              <p><strong>Price:</strong> ₹{listing.price}/kg</p>
              <p><strong>Location:</strong> {listing.location}</p>
              <p><strong>Contact:</strong> {listing.contact}</p>

              <button className="delete-btn" onClick={() => handleDelete(listing.id)}>
                ❌ Delete
              </button>
              <button className="edit-btn" onClick={() => handleEditClick(listing)}>
                ✏️ Edit
              </button>

              {editingId === listing.id && (
                <form
                  onSubmit={(e) => handleUpdate(e, listing.id)}
                  className="edit-form"
                >
                  <input
                    name="crop"
                    value={editFormData.crop}
                    onChange={handleEditChange}
                    placeholder="Crop Name"
                  />
                  <input
                    name="quantity"
                    value={editFormData.quantity}
                    onChange={handleEditChange}
                    placeholder="Quantity (kg)"
                  />
                  <input
                    name="price"
                    value={editFormData.price}
                    onChange={handleEditChange}
                    placeholder="Price"
                  />
                  <input
                    name="location"
                    value={editFormData.location}
                    onChange={handleEditChange}
                    placeholder="Location"
                  />
                  <input
                    name="contact"
                    value={editFormData.contact}
                    onChange={handleEditChange}
                    placeholder="Contact"
                  />
                  <button type="submit" className="save-btn">
                    💾 Save
                  </button>
                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={() => setEditingId(null)}
                  >
                    🗙 Cancel
                  </button>
                </form>
              )}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default AdminPanel;