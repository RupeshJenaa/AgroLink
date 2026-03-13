"""
Authentication Dependencies

Provides dependency injection for FastAPI routes to:
- Verify Firebase ID tokens
- Extract user information
- Enforce role-based access control
"""

from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from firebase_config import verify_firebase_token, get_user_role

class CurrentUser:
    """User information extracted from Firebase token"""
    def __init__(self, uid: str, email: str, role: str):
        self.uid = uid
        self.email = email
        self.role = role

async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    """
    Dependency to get current authenticated user from Firebase ID token.
    
    Expects Authorization header in format: "Bearer <firebase_id_token>"
    
    Args:
        authorization: Authorization header from request
        
    Returns:
        CurrentUser: Object containing user information
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Expected 'Bearer'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the Firebase ID token
    try:
        decoded_token = verify_firebase_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Fetch user role from Firestore
        role = await get_user_role(uid)
        
        return CurrentUser(uid=uid, email=email, role=role)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_farmer(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency to ensure user has 'farmer' role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CurrentUser: User object if role is farmer
        
    Raises:
        HTTPException: If user is not a farmer
    """
    if current_user.role != 'farmer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This feature is only available to farmers."
        )
    return current_user

async def require_authenticated(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency to ensure user is authenticated (any role).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        CurrentUser: User object
    """
    return current_user
