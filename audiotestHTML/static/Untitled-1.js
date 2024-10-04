// Fonction pour vérifier la compatibilité du navigateur et demander les permissions
function checkAndRequestPermissions() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        startRecording(stream);
      })
      .catch(error => {
        if (error.name === 'PermissionDeniedError') {
          alert("Veuillez autoriser l'accès à votre microphone pour utiliser cette fonctionnalité.");
        } else {
          console.error('Erreur lors de l\'accès au microphone:', error);
        }
      });
  } else {
    alert("Votre navigateur ne supporte pas l'enregistrement audio.");
  }
}

// Fonction pour démarrer l'enregistrement
function startRecording(stream) {
  const mediaRecorder = new MediaRecorder(stream);
  let audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

    // Envoyer le fichier audio à votre serveur pour transcription
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');

    fetch('/transcribe', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      displayResult(data.result);
    })
    .catch(error => {
      console.error('Erreur lors de la transcription:', error);
      alert('Une erreur est survenue lors de la transcription. Veuillez réessayer.');
    });
  };

  // Démarrage de l'enregistrement
  mediaRecorder.start();

  // Arrêt automatique après 5 secondes (ajustez si nécessaire)
  setTimeout(() => {
    mediaRecorder.stop();
  }, 5000);
}

// Fonction pour afficher les résultats de la transcription
function displayResult(result) {
  const resultElement = document.getElementById('result');
  resultElement.textContent = result.transcribed_text;
}

// Bouton pour démarrer l'enregistrement
const startButton = document.getElementById('startButton');
startButton.addEventListener('click', checkAndRequestPermissions);