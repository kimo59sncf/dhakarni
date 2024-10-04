import requests
import json
import os

# Chemin vers le fichier local de la liste des sourates
surah_list_file = 'ayat.json'

def download_quran_data():
    # Vérifier si le fichier de la liste des sourates existe
    if not os.path.exists(surah_list_file):
        print(f"Le fichier {surah_list_file} n'existe pas.")
        return

    # Charger la liste des sourates depuis le fichier local
    with open(surah_list_file, 'r', encoding='utf-8') as f:
        surah_list = json.load(f)

    quran_data = {}

    # Parcourir chaque sourate dans la liste
    for surah in surah_list:
        surah_id = surah['id']
        surah_name = surah['name']
        surah_link = surah['link']

        print(f"Téléchargement de la sourate {surah_id}: {surah_name}")

        # Télécharger le fichier JSON de la sourate
        surah_response = requests.get(surah_link)
        if surah_response.status_code != 200:
            print(f"Échec du téléchargement de la sourate {surah_id}")
            continue

        surah_data = surah_response.json()

        # Afficher les clés de surah_data pour vérifier la structure
        print(f"Clés de surah_data : {surah_data.keys()}")

        # Accéder aux versets en fonction de la structure réelle
        if 'verses' in surah_data:
            verses = surah_data['verses']
        elif 'chapter' in surah_data and 'verses' in surah_data['chapter']:
            verses = surah_data['chapter']['verses']
        else:
            print(f"Structure inattendue pour la sourate {surah_id}")
            continue

        # Construire le dictionnaire des ayats
        ayat = {}
        for verse in verses:
            ayah_number = str(verse['id'])
            ayah_text = verse['text']
            ayat[ayah_number] = ayah_text

        # Ajouter la sourate au dictionnaire quran_data
        quran_data[str(surah_id)] = {
            'name': surah_name,
            'ayat': ayat
        }

    # Enregistrer quran_data dans le fichier quran.json
    with open('quran.json', 'w', encoding='utf-8') as f:
        json.dump(quran_data, f, ensure_ascii=False, indent=4)

    print("Toutes les sourates ont été téléchargées et enregistrées dans quran.json.")

if __name__ == '__main__':
    download_quran_data()
