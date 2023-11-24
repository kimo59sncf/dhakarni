import mysql.connector

def remove_arabic_vowels_from_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="votre_utilisateur",
        password="votre_mot_de_passe",
        database="votre_base_de_donnees",
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # Utilisez la fonction REGEXP_REPLACE pour supprimer les voyelles arabes
    cursor.execute("UPDATE arabic SET text = REGEXP_REPLACE(text, '[ًٌٍَُِّْ]', '')")

    # Valider les changements
    conn.commit()

    # Fermer la connexion
    conn.close()

# Appeler la fonction pour supprimer les voyelles arabes de la base de données
remove_arabic_vowels_from_database()
