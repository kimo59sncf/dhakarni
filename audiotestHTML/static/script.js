let currentResultIndex = 0;
let resultsArray = [];

function showNextVerse() {
    if (resultsArray.length > 0) {
        currentResultIndex = (currentResultIndex + 1) % resultsArray.length;
        displayCurrentResult();
    }
}

function displayCurrentResult() {
    const currentResult = resultsArray[currentResultIndex];

    if (currentResult) {
        const suraName = currentResult.sura_name; // Utilisation du nom de la sourate au lieu du numéro
        const resultMessage = `
            <p>Verset trouvé :</p>
            <ul>
                <li>Sura: ${suraName}</li> <!-- Utiliser le nom de la sourate au lieu du numéro -->
                <li>Texte: ${currentResult.text}<span data-type="eoa" class="eoAaya">Verse: ${currentResult.aya}</span></li>
            </ul>
        `;
        appendToConsole(resultMessage, 'success');
    }
}

function startRecording() {
    appendToConsole('Enregistrement démarré...', 'info');
    fetch('/transcribe', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                const sura_number = data.result[0];
                const verse = data.result[1];
                const texte = data.result[2];
                const sura_name = data.sura_name;

                const resultMessage = `
                    <p class="verse-info">السورة: ${sura_name}</p>
                    <p class="verse-info">  آية رقم: ${verse}</p>
                    <p class="verse-text verse-text-special"> ${texte}</p>
                `;
                appendToConsole(resultMessage, 'success');
            } else {
                appendToConsole('Aucun verset trouvé dans la base de données.', 'info');
            }
        })
        .catch(error => {
            appendToConsole('Erreur lors de l\'enregistrement : ' + error.message, 'error');
        });
}

function stopRecording() {
    // Vous pouvez ajouter du code ici si nécessaire
}

function appendToConsole(message, className) {
    var consoleDiv = document.getElementById('console');

    // Supprimer le dernier affichage
    while (consoleDiv.firstChild) {
        consoleDiv.removeChild(consoleDiv.firstChild);
    }

    var messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.innerHTML = message;
    consoleDiv.appendChild(messageDiv);
}
