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

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            let options = null;

            if (MediaRecorder.isTypeSupported('audio/webm; codecs=opus')) {
                options = { mimeType: 'audio/webm; codecs=opus' };
            } else if (MediaRecorder.isTypeSupported('audio/ogg; codecs=opus')) {
                options = { mimeType: 'audio/ogg; codecs=opus' };
            } else {
                console.error('Aucun type MIME supporté trouvé pour MediaRecorder.');
                return;
            }

            const mediaRecorder = new MediaRecorder(stream, options);
            let chunks = [];

            mediaRecorder.ondataavailable = function (event) {
                chunks.push(event.data);
            };

            mediaRecorder.onstop = function () {
                const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
                const formData = new FormData();
                let filename = 'audio.webm';

                if (mediaRecorder.mimeType.includes('ogg')) {
                    filename = 'audio.ogg';
                }

                formData.append('audio', blob, filename);

                fetch('/transcribe', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.result) {
                        displayResult(data.result);
                    } else {
                        console.error('Erreur:', data.error);
                        appendToConsole(data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de l\'envoi de l\'audio:', error);
                });
            };

            mediaRecorder.start();

            setTimeout(() => {
                mediaRecorder.stop();
            }, 5000); // Enregistre pendant 5 secondes
        })
        .catch(error => {
            console.error('Erreur lors de l\'accès au micro:', error);
        });
}

function displayResult(result) {
    const resultMessage = `
        <p>Texte transcrit : ${result.transcribed_text}</p>
        <p>Résultat trouvé :</p>
        <ul>
            <li>Sourate : ${result.sura_name} (${result.sura_number})</li>
            <li>Verset : ${result.aya_number}</li>
            <li>Texte : ${result.aya_text}</li>
        </ul>
    `;
    appendToConsole(resultMessage, 'success');
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
