
def remove_arabic_vowels_from_sql_file(input_sql_file, output_sql_file):
    with open(input_sql_file, 'r', encoding='utf-8') as file:
        sql_script = file.read()
    # Supprimer les voyelles arabes
    arabic_vowels = "َ ً ُ ٌ ِ ٍ ْ ّ ٰ ٖ ٗ ٓ ٔ ٕ ٚ ٛ ٜ ٝ ٞ ٟ"
    sql_script_without_arabic_vowels = ''.join(char for char in sql_script if char not in arabic_vowels)

    with open(output_sql_file, 'w', encoding='utf-8') as file:
        file.write(sql_script_without_arabic_vowels)

# Exemple d'utilisation avec des chemins complets
remove_arabic_vowels_from_sql_file('arabic.sql', 'arabicZ.sql')

