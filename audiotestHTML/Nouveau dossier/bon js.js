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
        document.getElementById('result').innerHTML = currentResult.text || currentResult.error;
        console.log(`<p>Verset trouvé - Sura: ${currentResult.sura}, Verse: ${currentResult.aya}</p><p>Texte: ${currentResult.text}</p>`);
    }
}

function startRecording() {
    appendToConsole('Enregistrement démarré...', 'info');
    fetch('/transcribe', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.result) {
                const sura = data.result[0] !== undefined ? data.result[0] : 'Non défini';
                const verse = data.result[1] !== undefined ? data.result[1] : 'Non défini';
                const texte = data.result[2] !== undefined ? data.result[2] : 'Non défini';

                var resultMessage = `
                    Verset trouvé :
                    - Sura: ${sura}
                    - Verse: ${verse}
                    - Texte: ${texte}
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


function startRecording() {
    appendToConsole('Enregistrement démarré...', 'info');
    fetch('/transcribe', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log('Réponse du serveur :', data);

            if (data.text) {
                document.getElementById('recorded-text').innerText = data.text;
                appendToConsole('Texte enregistré avec succès !', 'success');
            } else {
                appendToConsole('Aucun texte enregistré.', 'info');
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'enregistrement :', error);
            appendToConsole('Erreur lors de l\'enregistrement : ' + error.message, 'error');
        });
}


function appendToConsole(message, className) {
    var consoleDiv = document.getElementById('console');

    // Supprimer le dernier affichage
    while (consoleDiv.firstChild) {
        consoleDiv.removeChild(consoleDiv.firstChild);
    }

    // Ajouter le nouvel affichage
    var messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.textContent = message;
    consoleDiv.appendChild(messageDiv);
}
