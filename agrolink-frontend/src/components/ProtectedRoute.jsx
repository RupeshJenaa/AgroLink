import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Protected Route Component
 * 
 * Wraps routes that require authentication.
 * Optionally can require specific roles (e.g., farmer-only features)
 */
const ProtectedRoute = ({ children, requiredRole = null }) => {
    const { isAuthenticated, role, loading } = useAuth();

    // Show loading state while checking authentication
    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh'
            }}>
                <p>Loading...</p>
            </div>
        );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // Check role requirement if specified
    if (requiredRole && role !== requiredRole) {
        return (
            <div style={{
                padding: '40px',
                textAlign: 'center',
                maxWidth: '600px',
                margin: '100px auto'
            }}>
                <h2>Access Denied</h2>
                <p>This feature is only available to {requiredRole}s.</p>
                <p>Your current role: {role}</p>
                <a href="/" style={{ color: '#667eea', textDecoration: 'none' }}>
                    Go to Home
                </a>
            </div>
        );
    }

    // Render the protected component
    return children;
};

export default ProtectedRoute;
