import os
import io
from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr
import mysql.connector
import json

app = Flask(__name__)

# Configurer pydub pour trouver ffmpeg (en local)
AudioSegment.converter = which("ffmpeg")
# en prod( ffmpeg est version linux dans le dossier bin)
#ffmpeg_path = os.path.join(os.getcwd(), 'bin', 'ffmpeg')
#AudioSegment.converter = ffmpeg_path

# Connexion à la base de données
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_DATABASE = "quran"
DB_PORT = 3306

# Charger le texte du Coran au démarrage
with open('quran.json', 'r', encoding='utf-8') as f:
    quran_data = json.load(f)

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
def get_ayah_from_database(sura_number, aya_number):
    try:
        # Accéder à la sourate
        sura = quran_data[str(sura_number)]
        # Accéder à l'ayah
        aya_text = sura['ayat'][str(aya_number)]
        # Préparer le résultat
        result = {
            'sura_number': sura_number,
            'sura_name': sura['name'],
            'aya_number': aya_number,
            'aya_text': aya_text
        }
        return result
    except KeyError:
        # La sourate ou l'ayah n'existe pas
        return None

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
@app.route('/get_ayah')
def get_ayah():
    sura_number = int(request.args.get('sura'))
    aya_number = int(request.args.get('aya'))

    # Logique pour récupérer l'ayah en fonction de la sourate et du numéro d'ayah
    result = get_ayah_from_database(sura_number, aya_number)

    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'success': False, 'error': 'Ayah not found'})

if __name__ == '__main__':
    app.run(debug=True)