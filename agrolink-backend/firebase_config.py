"""
Firebase Configuration for Backend

Initialize Firebase Admin SDK for:
- Authentication verification (verify ID tokens from frontend)
- Firestore database access
- User role management
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    """
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("✅ Firebase Admin SDK already initialized")
    except ValueError:
        # Not initialized, so initialize now
        import os
        
        # Try to use service account key file
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        
        if os.path.exists(key_path):
            # Use service account key file
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized with service account key")
        else:
            # Fallback: Initialize without auth (limited functionality)
            print("⚠️  WARNING: serviceAccountKey.json not found!")
            print("⚠️  Token verification will NOT work.")
            print("⚠️  Download from: Firebase Console → Project Settings → Service Accounts")
            firebase_admin.initialize_app(options={
                'projectId': 'agrolink-8bca7',
            })
            print("⚠️  Firebase Admin SDK initialized WITHOUT credentials")
    
    return firestore.client()

# Get Firestore client
db = None

def get_db():
    """Get Firestore database client"""
    global db
    if db is None:
        db = initialize_firebase()
    return db

def verify_firebase_token(id_token: str):
    """
    Verify Firebase ID token and return decoded token with user info.
    
    Args:
        id_token: Firebase ID token from the client
        
    Returns:
        dict: Decoded token containing user information (uid, email, etc.)
        
    Raises:
        Exception: If token is invalid or expired
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Invalid authentication token: {str(e)}")

async def get_user_role(uid: str):
    """
    Get user role from Firestore users collection.
    
    Args:
        uid: Firebase user ID
        
    Returns:
        str: User role ('farmer' or 'customer' or 'admin')
    """
    try:
        db = get_db()
        user_doc = db.collection('users').document(uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get('role', 'customer')  # Default to customer if role not set
        else:
            # User document doesn't exist, return default role
            return 'customer'
    except Exception as e:
        print(f"Error fetching user role: {str(e)}")
        return 'customer'
