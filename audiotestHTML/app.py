import sys
#sys.path.append('/Users/kimo/dev/www/dhakarni/venv/lib/python3.11/site-packages')
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import mysql.connector
import os
from gtts import gTTS
import io

app = Flask(__name__, static_url_path='/static')

# Mise à jour avec les nouvelles informations de la base de données
DB_HOST = "sql8.freesqldatabase.com"
DB_USER = "sql8732822"
DB_PASSWORD = "cbSjwGd9Xe"
DB_DATABASE = "sql8732822"
DB_PORT = 3306

# Configuration CORS
@app.after_request
def add_cors_headers(response):
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
    response.headers['Access-Control-Allow-Origin'] = allowed_origins
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def search_arabic_database(text):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        port=DB_PORT
    )
    cursor = conn.cursor()

    words = text.split()
    query = "SELECT sura, aya, text FROM quran_text WHERE " + " OR ".join(["INSTR(text, %s)" for _ in words])
    cursor.execute(query, tuple(word for word in words))

    results = cursor.fetchall()
    conn.close()

    major_result = None
    max_word_count = 0

    for result in results:
        text_result = result[2]
        word_count = sum(1 for word in words if word in text_result)
        if word_count > max_word_count:
            max_word_count = word_count
            major_result = result

    return major_result

def get_sura_name(sura_number):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        port=DB_PORT
    )
    cursor = conn.cursor()

    query = "SELECT sura_name FROM sura_names WHERE sura_number = %s"
    cursor.execute(query, (sura_number,))
    sura_name = cursor.fetchone()[0]

    conn.close()

    return sura_name


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ecoute...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language='ar')
        print("Texte transcrit : " + text)

        result = search_arabic_database(text)

        if result:
            sura_number = result[0]
            verse = result[1]
            sura_name = get_sura_name(sura_number)

            # Synthèse vocale avec gTTS
            tts = gTTS(text=result[2], lang='ar')
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)

            print(f"Verset trouvé - Sura: {sura_number}, Verse: {verse}, Texte: {result[2]}")
            return jsonify({'text': text, 'result': result, 'sura_name': sura_name})
        else:
            print("Aucun verset trouvé dans la base de données.")
            return jsonify({'text': text, 'result': 'Aucun verset trouvé'})

    except sr.UnknownValueError:
        print("Je n'ai pas compris")
        return jsonify({'error': 'Je n\'ai pas compris'})
    except sr.RequestError as e:
        print("Erreur de service : {0}".format(e))
        return jsonify({'error': 'Erreur de service'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
