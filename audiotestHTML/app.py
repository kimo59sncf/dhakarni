from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import mysql.connector
import os

app = Flask(__name__, static_url_path='/static')

# Configuration des variables pour la base de données
DB_USER = "root"
DB_PASSWORD = "root"
DB_DATABASE = "quran"
UNIX_SOCKET = "/Applications/MAMP/tmp/mysql/mysql.sock"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            unix_socket=UNIX_SOCKET,
            database=DB_DATABASE,
            raise_on_warnings=True
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de base de données : {err}")
        return None

def search_arabic_database(text):
    try:
        with get_db_connection() as conn:
            if conn is None:
                return None

            cursor = conn.cursor()

            # Diviser le texte en mots individuels
            words = text.split()

            # Construire dynamiquement la requête SQL avec INSTR
            query = "SELECT sura, aya, text FROM quran_text WHERE " + " OR ".join(
                ["INSTR(text, %s) > 0" for _ in words]
            )
            cursor.execute(query, tuple(words))

            results = cursor.fetchall()

            major_result = None
            max_word_count = 0

            # Trouver le résultat qui correspond le mieux
            for result in results:
                text_result = result[2]
                word_count = sum(1 for word in words if word in text_result)
                if word_count > max_word_count:
                    max_word_count = word_count
                    major_result = result

            return major_result

    except mysql.connector.Error as err:
        print(f"Erreur de base de données : {err}")
        return None

def get_sura_name(sura_number):
    try:
        with get_db_connection() as conn:
            if conn is None:
                return None

            cursor = conn.cursor()

            query = "SELECT sura_name FROM sura_names WHERE sura_number = %s"
            cursor.execute(query, (sura_number,))
            sura_name = cursor.fetchone()[0]  # Supposant que le numéro de sourate est unique

            return sura_name

    except mysql.connector.Error as err:
        print(f"Erreur de base de données lors de la récupération du nom de la sourate : {err}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Initialisation des outils de reconnaissance vocale
        print("Initialisation de la reconnaissance vocale...")
        recognizer = sr.Recognizer()

        # Capture de l'audio
        with sr.Microphone() as source:
            print("Écoute...")
            audio = recognizer.listen(source)

        # Transcription de l'audio en texte
        print("Transcription en cours...")
        text = recognizer.recognize_google(audio, language='ar')
        print("Texte transcrit : " + text)

        # Recherche dans la base de données
        result = search_arabic_database(text)
        print("Résultat de la recherche dans la base de données : ", result)

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
        print("Je n'ai pas compris l'audio")
        return jsonify({'error': 'Je n\'ai pas compris'}), 400

    except sr.RequestError as e:
        print(f"Erreur de service Google : {e}")
        return jsonify({'error': 'Erreur de service'}), 500

    except Exception as e:
        print(f"Erreur inconnue : {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Lancement de l'application Flask
    app.run(debug=True)
