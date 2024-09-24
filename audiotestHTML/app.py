import os
import io
from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr
import mysql.connector

app = Flask(__name__)

# Configurer pydub pour trouver ffmpeg
AudioSegment.converter = which("ffmpeg")

# Connexion à la base de données
DB_HOST = "sql8.freesqldatabase.com"
DB_USER = "sql8732822"
DB_PASSWORD = "cbSjwGd9Xe"
DB_DATABASE = "sql8732822"
DB_PORT = 3306

# Fonction pour convertir l'audio en WAV si nécessaire
def convert_audio_to_wav(audio_file):
    audio_format = os.path.splitext(audio_file.filename)[-1].lower().strip('.')

    # Lire les données du fichier
    file_data = audio_file.read()

    # Conversion selon le format d'entrée
    try:
        if audio_format == 'mp3':
            sound = AudioSegment.from_mp3(io.BytesIO(file_data))
        elif audio_format == 'ogg':
            sound = AudioSegment.from_ogg(io.BytesIO(file_data))
        elif audio_format == 'webm':
            sound = AudioSegment.from_file(io.BytesIO(file_data), format='webm')
        elif audio_format == 'wav':
            sound = AudioSegment.from_wav(io.BytesIO(file_data))
        else:
            return None, f'Format de fichier non pris en charge: {audio_format}'

        # Exporter en WAV
        wav_io = io.BytesIO()
        sound.export(wav_io, format="wav")
        wav_io.seek(0)

        return wav_io, None
    except Exception as e:
        return None, f'Erreur lors de la conversion audio : {str(e)}'

# Fonction pour obtenir le nom de la sourate
def get_sura_name(sura_number):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset='utf8mb4',
       # unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock'  # Mettez à jour ce chemin si nécessaire
    )
    cursor = conn.cursor()

    query = "SELECT sura_name FROM sura_names WHERE sura_number = %s"
    cursor.execute(query, (sura_number,))
    sura_name = cursor.fetchone()[0]

    conn.close()

    return sura_name

# Fonction pour rechercher des données dans la base de données
def search_arabic_database(text):
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset='utf8mb4',
        #unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock'  # Mettez à jour ce chemin si nécessaire
    )
    cursor = conn.cursor()

    words = text.split()
    query = "SELECT sura, aya, text FROM quran_text WHERE " + " OR ".join(["INSTR(text, %s)" for _ in words])
    cursor.execute(query, tuple(words))

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'Aucun fichier audio fourni.'}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()

    # Conversion de l'audio en WAV
    wav_audio, error = convert_audio_to_wav(audio_file)
    if error:
        return jsonify({'error': error}), 400

    try:
        # Utilisation du fichier WAV avec speech_recognition
        with sr.AudioFile(wav_audio) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language='ar')

            # Recherche du texte transcrit dans la base de données
            major_result = search_arabic_database(text)

            if major_result:
                sura_number = major_result[0]
                aya_number = major_result[1]
                aya_text = major_result[2]
                sura_name = get_sura_name(sura_number)

                result = {
                    'sura_number': sura_number,
                    'sura_name': sura_name,
                    'aya_number': aya_number,
                    'aya_text': aya_text,
                    'transcribed_text': text
                }

                return jsonify({'result': result})
            else:
                return jsonify({'error': 'Aucun verset correspondant trouvé.'})

    except sr.UnknownValueError as e:
        return jsonify({'error': f'Erreur de compréhension vocale : {str(e)}'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Erreur du service de reconnaissance vocale : {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Erreur inconnue : {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
