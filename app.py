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

if __name__ == '__main__':
    app.run(debug=True)
