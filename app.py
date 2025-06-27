# app.py

import streamlit as st
import pickle
import pandas as pd
import requests

# --- Page Config ---
st.set_page_config(page_title="Cineplex", page_icon="🎥", layout="wide")

# --- Load Data ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# --- Fetch Poster Function ---
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9ae52b8e46198833207ecb2aeac44e63&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path'] if data.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Poster"
        rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', 'No description available.')

        return poster_url, rating, overview

    except Exception as e:
        print(f"[ERROR] Movie detail fetch failed for movie_id={movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Error", "N/A", "No description available."


# --- Recommend Function ---
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

# --- UI Starts ---
st.markdown("<h1 style='text-align: center; color: #e50914;'>🍿 Cineplex: Movie Recommender 🎬</h1>", unsafe_allow_html=True)
st.markdown("### <span style='color:lightgray'>Search for a movie to get similar recommendations:</span>", unsafe_allow_html=True)

selected_movie_name = st.selectbox(" ", movies['title'].values)

if st.button("🚀 Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters, ratings, overviews = recommend(selected_movie_name)
        st.markdown("---")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"<h5 style='text-align: center; color: #fff;'>{names[i]}</h5>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gold;'>⭐ {ratings[i]}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 12px; color: #ccc;'>{overviews[i][:150]}...</p>", unsafe_allow_html=True)
