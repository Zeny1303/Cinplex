import streamlit as st
import pandas as pd
import pickle
import requests
import os

# --- UI Title ---
st.title('🎬 Cineplex: Movie Recommender System')

# --- File Upload ---
movie_dict_file = st.file_uploader("📁 Upload `movie_dict.pkl`", type="pkl")
similarity_file = st.file_uploader("📁 Upload `similarity.pkl`", type="pkl")

if movie_dict_file is not None and similarity_file is not None:
    # Load uploaded files
    movies_dict = pickle.load(movie_dict_file)
    similarity = pickle.load(similarity_file)
    movies = pd.DataFrame(movies_dict)

    # --- Fetch Poster ---
    def fetch_movie_details(movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9ae52b8e46198833207ecb2aeac44e63&language=en-US"
        response = requests.get(url)
        if response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Poster", "N/A", "No overview available"
        data = response.json()
        poster_url = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '') if data.get('poster_path') else "https://via.placeholder.com/300x450?text=No+Poster"
        return poster_url, data.get('vote_average', 'N/A'), data.get('overview', 'No overview available')

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

    # --- UI Input + Display ---
    selected_movie_name = st.selectbox("Search for a movie:", movies['title'].values)

    if st.button("🚀 Recommend"):
        with st.spinner("Finding top recommendations..."):
            names, posters, ratings, overviews = recommend(selected_movie_name)
            st.markdown("---")
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    st.image(posters[i], use_container_width=True)
                    st.markdown(f"**{names[i]}**")
                    st.markdown(f"⭐ {ratings[i]}")
                    st.markdown(f"📝 {overviews[i][:100]}...")

else:
    st.warning("⬆️ Please upload both `movie_dict.pkl` and `similarity.pkl` to continue.")
