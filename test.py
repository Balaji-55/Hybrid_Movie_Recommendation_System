import requests
from PIL import Image
from io import BytesIO

api_key = '20c67d9e5a125f9516102db2eb6bf8dc'
movie_name = 'The Avengers'

# Step 1: Search for the movie
url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
response = requests.get(url)
data = response.json()

# Step 2: Get the movie ID and poster path
movie_id = data['results'][0]['id']
movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
movie_response = requests.get(movie_url)
movie_data = movie_response.json()

poster_path = movie_data['poster_path']

poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
print(poster_url)   

# Step 3: Download and display the poster
poster_response = requests.get(poster_url)
img = Image.open(BytesIO(poster_response.content))
img.show()



import requests

# Your TMDb API key
api_key = '20c67d9e5a125f9516102db2eb6bf8dc'

# Function to get poster URL using TMDb API based on movie title
def get_poster(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        if results:
            poster_path = results[0].get('poster_path', None)
            if poster_path:
                full_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return full_url
    return None

# Updated recommend_for function
def recommend_for(userId, title):
    index = index_of_movies[title]
    tmdbId = movie_id.loc[title]['id']
    
    # Content-based filtering
    sim_scores = list(enumerate(cosin_sim2[int(index)]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:30]
    movie_indices = [i[0] for i in sim_scores]
    
    mv = movies.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'id']]
    mv = mv[mv['id'].isin(movie_id['id'])]

    # Collaborative filtering with SVD
    mv['est'] = mv['id'].apply(lambda x: svd.predict(userId, index_map.loc[x]['movieId']).est)

    mv = mv.sort_values('est', ascending=False)

    # Fetch posters from TMDb API for the top 10 recommended movies
    mv['poster_url'] = mv['title'].apply(get_poster)

    return mv[['title', 'vote_average', 'poster_url']].head(10)


import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Your TMDb API key
api_key = '20c67d9e5a125f9516102db2eb6bf8dc'

# Create a session with retry capability
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# Function to get poster URL using TMDb API
def get_poster(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}"
    
    # Delay to avoid hitting rate limit
    time.sleep(1)
    
    response = session.get(url)
    
    # Check if request was successful
    if response.status_code == 200:
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        rate_limit_reset = response.headers.get('X-RateLimit-Reset')
        print(f"Remaining: {rate_limit_remaining}, Reset in: {rate_limit_reset} seconds")
        
        data = response.json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

# Updated recommend_for function with TMDb poster integration
def recommend_for(userId, title):
    index = index_of_movies[title]
    tmdbId = movie_id.loc[title]['id']
    
    # Content-based filtering
    sim_scores = list(enumerate(cosin_sim2[int(index)]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:30]
    movie_indices = [i[0] for i in sim_scores]
    
    mv = movies.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'id']]
    mv = mv[mv['id'].isin(movie_id['id'])]

    # Collaborative filtering with SVD
    mv['est'] = mv['id'].apply(lambda x: svd.predict(userId, index_map.loc[x]['movieId']).est)

    mv = mv.sort_values('est', ascending=False)

    # Fetch posters from TMDb API for the top 10 recommended movies
    mv['poster_url'] = mv['id'].apply(get_poster)

    return mv[['title', 'vote_average', 'poster_url']].head(10)
