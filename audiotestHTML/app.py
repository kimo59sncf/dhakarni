import os
import io
import subprocess
from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr
import json
import re
from rapidfuzz import fuzz, process
import tempfile

app = Flask(__name__)

# Configurer pydub pour trouver ffmpeg (en local)
if which("ffmpeg") is None:
    AudioSegment.converter = "/usr/bin/ffmpeg"  # Modifier ce chemin selon l'emplacement de ffmpeg sur votre système
else:
    AudioSegment.converter = which("ffmpeg")

# Charger le texte du Coran au démarrage
with open('quran.json', 'r', encoding='utf-8') as f:
    quran_data = json.load(f)

# Fonction pour supprimer les diacritiques du texte arabe
def remove_diacritics(text):
    arabic_diacritics = re.compile("""
                                     ّ    | # Shadda
                                     َ    | # Fatha
                                     ً    | # Tanwin Fath
                                     ُ    | # Damma
                                     ٌ    | # Tanwin Damm
                                     ِ    | # Kasra
                                     ٍ    | # Tanwin Kasr
                                     ْ    | # Sukun
                                     ـ     # Tatwil/Kashida
                                 """, re.VERBOSE)
    return re.sub(arabic_diacritics, '', text)

# Fonction pour convertir l'audio en WAV si nécessaire
def convert_audio_to_wav(audio_file):
    audio_format = os.path.splitext(audio_file.filename)[-1].lower().strip('.')
    try:
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.' + audio_format)
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')

        audio_file.save(temp_input.name)

        command = ['ffmpeg', '-y', '-i', temp_input.name, temp_output.name]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        wav_io = open(temp_output.name, 'rb')
        return wav_io, None
    except Exception as e:
        return None, f'Erreur lors de la conversion audio : {str(e)}'
    finally:
        temp_input.close()
        temp_output.close()
        os.unlink(temp_input.name)
        # Ne supprimez pas temp_output.name ici car nous en avons besoin plus tard
        # Il sera supprimé après utilisation


def search_ayah_by_transcription(transcribed_text, threshold=70):
    transcribed_text = remove_diacritics(transcribed_text)
    best_match = None
    highest_ratio = 0

    for sura_number, sura in quran_data.items():
        sura_name = sura['name']
        ayat = sura['ayat']
        for aya_number, aya_text in ayat.items():
            aya_text_no_diacritics = remove_diacritics(aya_text)
            ratio = fuzz.partial_ratio(transcribed_text, aya_text_no_diacritics)
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = {
                    'sura_number': int(sura_number),
                    'sura_name': sura_name,
                    'aya_number': int(aya_number),
                    'aya_text': aya_text,
                    'transcribed_text': transcribed_text,
                    'similarity': ratio
                }

    if best_match and highest_ratio >= threshold:
        return best_match
    else:
        return None

# Fonction pour obtenir une ayah spécifique depuis le fichier JSON
def get_ayah_from_json(sura_number, aya_number):
    try:
        sura = quran_data[str(sura_number)]
        aya_text = sura['ayat'][str(aya_number)]
        result = {
            'sura_number': sura_number,
            'sura_name': sura['name'],
            'aya_number': aya_number,
            'aya_text': aya_text
        }
        return result
    except KeyError:
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
        print(f"Erreur lors de la conversion audio : {error}")
        return jsonify({'error': error}), 400

    try:
        # Utilisation du fichier WAV avec speech_recognition
        with sr.AudioFile(wav_audio) as source:
            print("Enregistrement audio chargé pour la transcription.")
            audio = recognizer.record(source)
            print("Début de la transcription...")
            text = recognizer.recognize_google(audio, language='ar')
            print(f"Texte transcrit : {text}")

            # Recherche du texte transcrit dans le fichier JSON
            result = search_ayah_by_transcription(text)

            if result:
                print(f"Verset trouvé : {result}")
                return jsonify({'result': result})
            else:
                print("Aucun verset correspondant trouvé.")
                return jsonify({'result': None, 'error': 'Aucun verset correspondant trouvé.'})
    except sr.UnknownValueError as e:
        print(f"Erreur de compréhension vocale : {e}")
        return jsonify({'error': f'Erreur de compréhension vocale : {str(e)}'}), 400
    except sr.RequestError as e:
        print(f"Erreur du service de reconnaissance vocale : {e}")
        return jsonify({'error': f'Erreur du service de reconnaissance vocale : {str(e)}'}), 500
    except Exception as e:
        print(f"Erreur inconnue : {e}")
        return jsonify({'error': f'Erreur inconnue : {str(e)}'}), 500
    finally:
        wav_audio.close()
        os.unlink(wav_audio.name)

@app.route('/get_ayah')
def get_ayah():
    sura_number = request.args.get('sura')
    aya_number = request.args.get('aya')

    if not sura_number or not aya_number:
        return jsonify({'success': False, 'error': 'Paramètres manquants'}), 400

    result = get_ayah_from_json(sura_number, aya_number)

    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'success': False, 'error': 'Ayah non trouvée'}), 404

if __name__ == '__main__':
    app.run(debug=True)
