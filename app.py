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
    'cdrama': {'type': 'tv', 'params': '&with_original_language=zh&with_genres=18'},
    'turkish': {'type': 'tv', 'params': '&with_original_language=tr'},  # Ertuğrul, Osman, Turkish Series
    'arabic': {'type': 'movie', 'params': '&with_original_language=ar'} # Arabic Movies & Content
}

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

# 1. HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')

# 2. WHATSAPP GENERATOR ROUTE
import urllib.parse

@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp():
    link = None
    qr_url = None
    phone = ""
    message = ""

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        # Clean phone number by removing +, spaces, and dashes
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if clean_phone:
            if message:
                encoded_msg = urllib.parse.quote(message)
                link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            else:
                link = f"https://wa.me/{clean_phone}"
            
            # Generate QR Code via standard API
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(link)}"

    return render_template('whatsapp.html', link=link, qr_url=qr_url, phone=phone, message=message)

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
    selected_genre = 'random'
    media = None

    if request.method == 'POST':
        selected_genre = request.form.get('genre', 'random')

    # Handle genre selection
    if selected_genre == 'random' or selected_genre not in GENRE_MAP:
        chosen_key = random.choice(list(GENRE_MAP.keys()))
        config = GENRE_MAP[chosen_key]
    else:
        config = GENRE_MAP[selected_genre]

    media_type = config['type']
    extra_params = config['params']
    random_page = random.randint(1, 5)

    url = f"https://api.themoviedb.org/3/discover/{media_type}?api_key={TMDB_API_KEY}&sort_by=popularity.desc&page={random_page}{extra_params}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                item = random.choice(results)
                
                title = item.get('title') or item.get('name') or "Unknown Title"
                overview = item.get('overview', 'No overview available.')
                poster_path = item.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                vote_average = round(item.get('vote_average', 0), 1)
                release_date = item.get('release_date') or item.get('first_air_date') or 'N/A'
                
                # Fetch Trailer Video Key
                item_id = item.get('id')
                trailer_url = None
                try:
                    video_res = requests.get(f"https://api.themoviedb.org/3/{media_type}/{item_id}/videos?api_key={TMDB_API_KEY}", timeout=5)
                    if video_res.status_code == 200:
                        videos = video_res.json().get('results', [])
                        for vid in videos:
                            if vid.get('type') == 'Trailer' and vid.get('site') == 'YouTube':
                                trailer_url = f"https://www.youtube.com/watch?v={vid.get('key')}"
                                break
                except Exception:
                    pass

                media = {
                    'title': title,
                    'overview': overview,
                    'poster_url': poster_url,
                    'rating': vote_average,
                    'release_date': release_date,
                    'trailer_url': trailer_url,
                    'media_type': 'TV Series' if media_type == 'tv' else 'Movie'
                }
    except Exception as e:
        print(f"TMDB Fetch Error: {e}")

    return render_template('what_to_watch.html', media=media, selected_genre=selected_genre)

if __name__ == '__main__':
    app.run(debug=True)
