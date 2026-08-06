import random
import io
import base64
import urllib.parse
from flask import Flask, render_template, request
import qrcode

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    processed_text = ""
    word_count = 0
    char_count = 0

    if request.method == 'POST':
        user_text = request.form.get('text', '')
        action = request.form.get('action')

        if action == 'uppercase':
            processed_text = user_text.upper()
        elif action == 'lowercase':
            processed_text = user_text.lower()
        elif action == 'titlecase':
            processed_text = user_text.title()
        elif action == 'remove_spaces':
            processed_text = " ".join(user_text.split())

        word_count = len(processed_text.split()) if processed_text else 0
        char_count = len(processed_text)

    return render_template('index.html', 
                           processed_text=processed_text, 
                           word_count=word_count, 
                           char_count=char_count)

@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp():
    wa_link = ""
    qr_code_url = ""
    phone = ""
    message = ""

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip().replace('+', '').replace(' ', '')
        message = request.form.get('message', '').strip()

        if phone:
            encoded_msg = urllib.parse.quote(message, safe='!')
            wa_link = f"https://wa.me/{phone}?text={encoded_msg}" if encoded_msg else f"https://wa.me/{phone}"

            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(wa_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buf = io.BytesIO()
            img.save(buf, format='PNG')
            qr_code_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('ascii')

    return render_template('whatsapp.html', wa_link=wa_link, qr_code_url=qr_code_url, phone=phone, message=message)
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
@app.route('/about')
def about():
    return render_template('about.html')
MOVIES_DB = {
    'action': [
        {"title": "Mad Max: Fury Road", "year": "2015", "rating": "8.1/10", "desc": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler."},
        {"title": "The Dark Knight", "year": "2008", "rating": "9.0/10", "desc": "Batman faces the Joker, a criminal mastermind bent on causing chaos in Gotham City."},
        {"title": "John Wick", "year": "2014", "rating": "7.4/10", "desc": "An ex-hitman comes out of retirement to track down the gangsters that took everything from him."}
    ],
    'comedy': [
        {"title": "The Hangover", "year": "2009", "rating": "7.7/10", "desc": "Three buddies wake up from a bachelor party in Las Vegas with no memory of the previous night."},
        {"title": "Superbad", "year": "2007", "rating": "7.6/10", "desc": "Two co-dependent high school seniors deal with separation anxiety after their plan to stage a party goes awry."},
        {"title": "Free Guy", "year": "2021", "rating": "7.1/10", "desc": "A bank teller discovers he is actually a background player in an open-world video game."}
    ],
    'drama': [
        {"title": "Interstellar", "year": "2014", "rating": "8.7/10", "desc": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."},
        {"title": "Parasite", "year": "2019", "rating": "8.5/10", "desc": "Greed and class discrimination threaten the newly formed symbiotic relationship between a wealthy family and the destitute family."},
        {"title": "Whiplash", "year": "2014", "rating": "8.5/10", "desc": "A promising young drummer enlists at a cut-throat music conservatory where his instructor will stop at nothing to realize his potential."}
    ],
    'horror': [
        {"title": "A Quiet Place", "year": "2018", "rating": "7.5/10", "desc": "A family must navigate their lives in silence to avoid mysterious creatures that hunt by sound."},
        {"title": "Get Out", "year": "2017", "rating": "7.8/10", "desc": "A young African-American visits his white girlfriend's parents for the weekend, where his uneasiness leads to a discovery."},
        {"title": "The Conjuring", "year": "2013", "rating": "7.5/10", "desc": "Paranormal investigators work to help a family terrorized by a dark presence in their farmhouse."}
    ]
}

@app.route('/what-to-watch', methods=['GET', 'POST'])
def what_to_watch():
    selected_genre = None
    movie = None
    if request.method == 'POST':
        selected_genre = request.form.get('genre')
        if selected_genre == 'random' or not selected_genre:
            all_movies = [m for genre in MOVIES_DB.values() for m in genre]
            movie = random.choice(all_movies)
        elif selected_genre in MOVIES_DB:
            movie = random.choice(MOVIES_DB[selected_genre])
            
    return render_template('what_to_watch.html', movie=movie, selected_genre=selected_genre)

if __name__ == '__main__':
    app.run(debug=True)
# Route for the Case Converter utility
@app.route('/case-converter')
def case_converter():
    return render_template('converter.html')
