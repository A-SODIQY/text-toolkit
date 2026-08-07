from flask import Flask, render_template, request
import random
import requests

app = Flask(__name__)

# ----------------------------------------------------
# TMDB API CONFIGURATION
# ----------------------------------------------------
TMDB_API_KEY = '72b1184f6368626d871c371e0571a430'

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

# 1. HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')

# 2. WHATSAPP GENERATOR ROUTE
@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp():
    link = None
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        if phone:
            # Clean phone number formatting
            clean_phone = ''.join(filter(str.isdigit, phone))
            link = f"https://wa.me/{clean_phone}"
            if message:
                import urllib.parse
                encoded_msg = urllib.parse.quote(message)
                link += f"?text={encoded_msg}"
    return render_template('whatsapp.html', link=link)

# 3. CASE CONVERTER ROUTE
@app.route('/case-converter', methods=['GET', 'POST'])
def case_converter():
    converted_text = None
    original_text = ""
    conversion_type = None

    if request.method == 'POST':
        original_text = request.form.get('text', '')
        conversion_type = request.form.get('type')

        if conversion_type == 'uppercase':
            converted_text = original_text.upper()
        elif conversion_type == 'lowercase':
            converted_text = original_text.lower()
        elif conversion_type == 'titlecase':
            converted_text = original_text.title()

    return render_template('case_converter.html', converted_text=converted_text, original_text=original_text)

# 4. WHAT TO WATCH ROUTE
@app.route('/what-to-watch', methods=['GET', 'POST'])
def what_to_watch():
    selected_genre = None
    movie = None

    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        page = random.randint(1, 5)
        
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
