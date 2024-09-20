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
        const suraName = currentResult.sura_name;
        const resultMessage = `
            <p>Verset trouvé :</p>
            <ul>
                <li>Sura: ${suraName}</li>
                <li>Texte: ${currentResult.text}<span data-type="eoa" class="eoAaya">Verse: ${currentResult.aya}</span></li>
            </ul>
        `;
        appendToConsole(resultMessage, 'success');
    }
}

async function startRecording() {
    appendToConsole('Enregistrement démarré...', 'info');
    
    var textDisplay = document.getElementById('text-display');
    textDisplay.classList.add('visible');
    
    try {
        const response = await fetch('/transcribe', { method: 'POST' });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const text = await response.text();

        try {
            const data = JSON.parse(text);
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
        } catch (error) {
            console.error('Erreur lors de la conversion en JSON :', error.message);
            console.log('Réponse brute :', text);
            appendToConsole('Erreur inattendue lors de l\'enregistrement : réponse non valide.', 'error');
        }
    } catch (error) {
        appendToConsole('Erreur lors de l\'enregistrement : ' + error.message, 'error');
    }
}

function stopRecording() {
    // Vous pouvez ajouter du code ici si nécessaire
}

function appendToConsole(message, className) {
    var consoleDiv = document.getElementById('console');

    while (consoleDiv.firstChild) {
        consoleDiv.removeChild(consoleDiv.firstChild);
    }

    var messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.innerHTML = message;
    consoleDiv.appendChild(messageDiv);

    consoleDiv.classList.add('visible');
}
