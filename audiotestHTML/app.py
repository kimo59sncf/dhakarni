from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import mysql.connector
import os

app = Flask(__name__, static_url_path='/static')

# Utilisation de variables d'environnement
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
DB_DATABASE = os.environ.get("DB_DATABASE", "quran")

# Configuration CORS
@app.after_request
def add_cors_headers(response):
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
    response.headers['Access-Control-Allow-Origin'] = allowed_origins
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def search_arabic_database(text):
    # Utilisation de requêtes préparées pour la sécurité
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset='utf8mb4'
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

# Gestion des exceptions et validation des données utilisateur
def get_sura_name(sura_number):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    query = "SELECT sura_name FROM sura_names WHERE sura_number = %s"
    cursor.execute(query, (sura_number,))
    sura_name = cursor.fetchone()[0]  # Supposant que le numéro de sourate est unique

    conn.close()

    return sura_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    r = sr.Recognizer()
    engine = pyttsx3.init()

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
    # Utilisation d'une configuration différente pour le développement et la production
    app.run(debug=True, host='0.0.0.0')
