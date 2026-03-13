import { getDatabase, ref, set, onValue, push } from 'firebase/database';
import { auth } from '../firebaseConfig';

export const marketplaceService = {
  // Add a new crop listing
  addCropListing: async (cropData) => {
    if (!auth.currentUser) throw new Error('User not authenticated');

    const db = getDatabase();
    const listingsRef = ref(db, 'marketplace/listings');
    const newListingRef = push(listingsRef);

    await set(newListingRef, {
      ...cropData,
      userId: auth.currentUser.uid,
      createdAt: Date.now()
    });

    return newListingRef.key;
  },

  // Subscribe to marketplace updates
  subscribeToListings: (callback) => {
    const db = getDatabase();
    const listingsRef = ref(db, 'marketplace/listings');

    const unsubscribe = onValue(listingsRef, (snapshot) => {
      const listings = [];
      snapshot.forEach((child) => {
        listings.push({
          id: child.key,
          ...child.val()
        });
      });
      callback(listings);
    });

    return unsubscribe;
  },

  // Get listings by user type
  getListingsByUserType: (userType, callback) => {
    const db = getDatabase();
    const listingsRef = ref(db, 'marketplace/listings');

    const unsubscribe = onValue(listingsRef, (snapshot) => {
      const listings = [];
      snapshot.forEach((child) => {
        const listing = {
          id: child.key,
          ...child.val()
        };
        
        // If user is a farmer, show all listings
        // If user is a customer, only show active listings
        if (userType === 'farmer' || listing.status === 'active') {
          listings.push(listing);
        }
      });
      callback(listings);
    });

    return unsubscribe;
  },

  // Update a crop listing
  updateListing: async (listingId, updates) => {
    if (!auth.currentUser) throw new Error('User not authenticated');

    const db = getDatabase();
    const listingRef = ref(db, `marketplace/listings/${listingId}`);
    await set(listingRef, updates);
  },

  // Delete a crop listing
  deleteListing: async (listingId) => {
    if (!auth.currentUser) throw new Error('User not authenticated');

    const db = getDatabase();
    const listingRef = ref(db, `marketplace/listings/${listingId}`);
    await set(listingRef, null);
  }
};