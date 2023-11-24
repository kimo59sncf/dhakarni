from flask import Flask, render_template, request
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

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
        engine.say(text)
        engine.runAndWait()
        return {'text': text}
    except sr.UnknownValueError:
        print("Je n'ai pas compris")
        return {'error': 'Je n\'ai pas compris'}
    except sr.RequestError as e:
        print("Erreur de service : {0}".format(e))
        return {'error': 'Erreur de service'}
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import mysql.connector

app = Flask(__name__)

def search_arabic_database(text):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="quran",
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # Diviser la chaîne de texte en mots
    words = text.split()

    # Construire une requête avec une condition OR pour chaque mot
    query = "SELECT sura, aya, text FROM quran_text WHERE "
    query += " OR ".join(["INSTR(text, %s)" for _ in words])

    # Exécuter la requête en passant chaque mot comme paramètre
    cursor.execute(query, tuple(word for word in words))

    results = cursor.fetchall()
    conn.close()

    # Initialiser le résultat majoritaire
    major_result = None
    max_word_count = 0

    # Parcourir les résultats et compter les mots correspondants
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
    r = sr.Recognizer()
    engine = pyttsx3.init()

    with sr.Microphone() as source:
        print("Ecoute...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language='ar')
        print("Texte transcrit : " + text)

        # Effectuer la recherche dans la base de données
        result = search_arabic_database(text)

        if result:
            print(f"Verset trouvé - Sura: {result[0]}, Verse: {result[1]}, Texte: {result[2]}")
            return jsonify({'text': text, 'result': result})
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
    app.run(debug=True)
