from flask import Flask, render_template, request
import random
import requests

app = Flask(__name__)

# ----------------------------------------------------
# TMDB API CONFIGURATION
# ----------------------------------------------------
# Replace the text inside quotes with your TMDB API key
TMDB_API_KEY = 'YOUR_TMDB_API_KEY_HERE'

# Genre and Drama categories linked to TMDB IDs
GENRE_MAP = {
    'action': {'type': 'movie', 'params': '&with_genres=28'},
    'comedy': {'type': 'movie', 'params': '&with_genres=35'},
    'drama': {'type': 'movie', 'params': '&with_genres=18'},
    'horror': {'type': 'movie', 'params': '&with_genres=27'},
    'romance': {'type': 'movie', 'params': '&with_genres=10749'},
    'sci-fi': {'type': 'movie', 'params': '&with_genres=878'},
    'kdrama': {'type': 'tv', 'params': '&with_original_language=ko&with_genres=18'},
    'cdrama': {'type': 'tv', 'params': '&with_original_language=zh&with_genres=18'}
}

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/what-to-watch', methods=['GET', 'POST'])
def what_to_watch():
    selected_genre = None
    movie = None

    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        page = random.randint(1, 5)  # Pick a random page to keep recommendations fresh
        
        # Surprise Me! selects randomly across all genres including K-Drama & C-Drama
        if selected_genre == 'random' or not selected_genre:
            chosen_key = random.choice(list(GENRE_MAP.keys()))
            config = GENRE_MAP[chosen_key]
        elif selected_genre in GENRE_MAP:
            config = GENRE_MAP[selected_genre]
        else:
            config = {'type': 'movie', 'params': ''}

        media_type = config['type']
        extra_params = config['params']
        url = f"https://api.themoviedb.org/3/discover/{media_type}?api_key={TMDB_API_KEY}&page={page}&sort_by=popularity.desc{extra_params}"
            
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    selected_item = random.choice(results)
                    
                    poster_path = selected_item.get('poster_path')
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    
                    title = selected_item.get('title') or selected_item.get('name')
                    release_date = selected_item.get('release_date') or selected_item.get('first_air_date', '')
                    year = release_date.split('-')[0] if release_date else 'N/A'
                    
                    movie = {
                        'title': title,
                        'year': year,
                        'rating': f"{selected_item.get('vote_average', 0):.1f}/10",
                        'desc': selected_item.get('overview', 'No summary available.'),
                        'poster': poster_url
                    }
        except Exception as e:
            print("API Error:", e)

    return render_template('what_to_watch.html', movie=movie, selected_genre=selected_genre)

if __name__ == '__main__':
    app.run(debug=True)
