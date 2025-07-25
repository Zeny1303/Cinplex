# app.py

import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os

import firebase_admin
from firebase_admin import credentials, firestore

# --- Streamlit Config ---
st.set_page_config(page_title="Cineplex", page_icon="🎥", layout="wide")

# --- Firebase Initialization ---
@st.cache_resource
def init_firebase():
    firebase_secrets = st.secrets["FIREBASE"]
    private_key = firebase_secrets["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n")

    cred = credentials.Certificate({
        "type": firebase_secrets["FIREBASE_TYPE"],
        "project_id": firebase_secrets["FIREBASE_PROJECT_ID"],
        "private_key_id": firebase_secrets["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": private_key,
        "client_email": firebase_secrets["FIREBASE_CLIENT_EMAIL"],
        "client_id": firebase_secrets["FIREBASE_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": firebase_secrets["FIREBASE_CLIENT_CERT_URL"]
    })

    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# --- Download if missing from Google Drive ---
def download_if_missing(file_name, file_id):
    if not os.path.exists(file_name):
        st.info(f"📥 Downloading {file_name}...")
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, file_name, quiet=False)

download_if_missing("movie_dict.pkl", "18FMqH7M3sCxq-1R2SOLzZhxYOIGV9Hf6")
download_if_missing("similarity.pkl", "1q2TEo5-2XLxR4ThzSBa1rjmMwuRGfxNF")

# --- Load Data ---
try:
    with open("movie_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# --- TMDB Movie Detail Fetch ---
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9ae52b8e46198833207ecb2aeac44e63&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        poster_url = (
            "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            if data.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Poster"
        )
        rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', 'No description available.')

        return poster_url, rating, overview

    except Exception as e:
        print(f"[ERROR] Movie detail fetch failed for movie_id={movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Error", "N/A", "No description available."

# --- Recommender Logic ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_ratings = []
    recommended_overviews = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, rating, overview = fetch_movie_details(movie_id)

        recommended_movies.append(title)
        recommended_posters.append(poster)
        recommended_ratings.append(rating)
        recommended_overviews.append(overview)

    return recommended_movies, recommended_posters, recommended_ratings, recommended_overviews

# --- Streamlit UI ---
st.markdown("<h1 style='text-align: center; color: #e50914;'>🍿 Cineplex: Movie Recommender 🎬</h1>", unsafe_allow_html=True)
st.markdown("### <span style='color:lightgray'>Search for a movie to get similar recommendations:</span>", unsafe_allow_html=True)

selected_movie_name = st.selectbox(" ", movies['title'].values)

if st.button("🚀 Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters, ratings, overviews = recommend(selected_movie_name)

        # ✅ Log to Firebase
        db.collection("recommendations").add({
            "input_movie": selected_movie_name,
            "recommended": names,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        st.markdown("---")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"<h5 style='text-align: center; color: #fff;'>{names[i]}</h5>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gold;'>⭐ {ratings[i]}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 12px; color: #ccc;'>{overviews[i][:150]}...</p>", unsafe_allow_html=True)
