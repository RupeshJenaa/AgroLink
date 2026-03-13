import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";

// Your Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyCz1Q1ixUKQAbl5Bem8g5uiiUP4ZO_Qp04",
  authDomain: "agrolink-8bca7.firebaseapp.com",
  projectId: "agrolink-8bca7",
  storageBucket: "agrolink-8bca7.firebasestorage.app",
  messagingSenderId: "327261048606",
  appId: "1:327261048606:web:65e1e8b2837ff2c48d430f",
  databaseURL: "https://agrolink-8bca7-default-rtdb.asia-southeast1.firebasedatabase.app"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const rtdb = getDatabase(app);

export { db, auth, rtdb };
