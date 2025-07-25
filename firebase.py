import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- Initialize Firebase ---
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        })
        firebase_admin.initialize_app(cred)
    return firestore.client()

# --- Save favorite movie ---
def save_favorite(user_id: str, movie_title: str):
    db = init_firebase()
    db.collection("favorites").add({
        "user_id": user_id,
        "movie": movie_title
    })

# --- Load favorite movies ---
def get_favorites(user_id: str):
    db = init_firebase()
    docs = db.collection("favorites").where("user_id", "==", user_id).stream()
    return [doc.to_dict()["movie"] for doc in docs]
