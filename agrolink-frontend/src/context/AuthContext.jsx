import React, { createContext, useState, useEffect, useContext } from 'react';
import { auth, db } from '../firebaseConfig';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged
} from 'firebase/auth';
import { doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [userState, setUserState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Listen to authentication state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);

        // Fetch user role from Firestore
        try {
          const userDocRef = doc(db, 'users', firebaseUser.uid);
          const userDoc = await getDoc(userDocRef);

          if (userDoc.exists()) {
            const userData = userDoc.data();
            setRole(userData.role || 'customer');
            setUserState(userData.state || null);
          } else {
            setRole('customer'); // Default role
            setUserState(null);
          }
        } catch (err) {
          console.error('Error fetching user role:', err);
          setRole('customer');
          setUserState(null);
        }
      } else {
        setUser(null);
        setRole(null);
        setUserState(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const register = async (email, password, name, selectedRole, selectedState) => {
    try {
      setError(null);
      setLoading(true);

      console.log('🔵 Starting registration...', { email, name, selectedRole });

      // Create user in Firebase Auth
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const firebaseUser = userCredential.user;

      console.log('✅ Firebase Auth user created:', firebaseUser.uid);

      // Create user profile in Firestore
      const userDocRef = doc(db, 'users', firebaseUser.uid);

      console.log('🔵 Attempting to create Firestore document...', {
        uid: firebaseUser.uid,
        email,
        name,
        role: selectedRole
      });

      await setDoc(userDocRef, {
        uid: firebaseUser.uid,
        email: email,
        name: name,
        role: selectedRole,
        state: selectedState || null,
        createdAt: new Date(),
        updatedAt: new Date()
      });

      setUserState(selectedState || null);

      console.log('✅ Firestore document created successfully!');

      setRole(selectedRole);
      setLoading(false);

      return { success: true, user: firebaseUser };
    } catch (err) {
      console.error('❌ Registration error:', err);
      console.error('Error code:', err.code);
      console.error('Error message:', err.message);
      setLoading(false);
      setError(err.message);
      throw err;
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);

      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const firebaseUser = userCredential.user;

      // Fetch user role
      const userDocRef = doc(db, 'users', firebaseUser.uid);
      const userDoc = await getDoc(userDocRef);

      if (userDoc.exists()) {
        const userData = userDoc.data();
        setRole(userData.role || 'customer');
        setUserState(userData.state || null);
      } else {
        setRole('customer');
        setUserState(null);
      }

      setLoading(false);
      return { success: true, user: firebaseUser };
    } catch (err) {
      setLoading(false);
      setError(err.message);
      throw err;
    }
  };

  const updateProfile = async (updates) => {
    if (!user) throw new Error('Not authenticated');
    const userDocRef = doc(db, 'users', user.uid);
    await updateDoc(userDocRef, { ...updates, updatedAt: new Date() });
    if (updates.state !== undefined) setUserState(updates.state);
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setRole(null);
      setUserState(null);
      setError(null);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const value = {
    user,
    role,
    userState,
    loading,
    error,
    register,
    login,
    logout,
    updateProfile,
    isAuthenticated: !!user,
    isFarmer: role === 'farmer',
    isCustomer: role === 'customer'
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
