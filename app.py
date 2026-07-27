from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ""
    processed_text = ""
    action = ""
    word_count = 0
    char_count = 0

    if request.method == 'POST':
        original_text = request.form.get('text_input', '')
        action = request.form.get('action', '')

        # Text calculations
        word_count = len(original_text.split())
        char_count = len(original_text)

        # Actions
        if action == 'uppercase':
            processed_text = original_text.upper()
        elif action == 'lowercase':
            processed_text = original_text.lower()
        elif action == 'clean_spaces':
            processed_text = ' '.join(original_text.split())
        elif action == 'titlecase':
            processed_text = original_text.title()
        else:
            processed_text = original_text

    return render_template(
        'index.html',
        original_text=original_text,
        processed_text=processed_text,
        word_count=word_count,
        char_count=char_count
    )

if __name__ == '__main__':
    app.run(debug=True)
