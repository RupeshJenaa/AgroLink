import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";

// Your Firebase config
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY || "AIzaSyCz1Q1ixUKQAbl5Bem8g5uiiUP4ZO_Qp04",
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || "agrolink-8bca7.firebaseapp.com",
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID || "agrolink-8bca7",
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || "agrolink-8bca7.firebasestorage.app",
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID || "327261048606",
  appId: process.env.REACT_APP_FIREBASE_APP_ID || "1:327261048606:web:65e1e8b2837ff2c48d430f",
  databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL || "https://agrolink-8bca7-default-rtdb.asia-southeast1.firebasedatabase.app"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const rtdb = getDatabase(app);

export { db, auth, rtdb };
