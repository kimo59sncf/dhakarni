let mediaRecorder;
let audioChunks = [];

function startRecording() {
    // Vérification de la compatibilité avec l'API MediaRecorder
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('API MediaRecorder non supportée par votre navigateur.');
        return;
    }

    navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.ondataavailable = function (event) {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = function () {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio_data', audioBlob);

            // Envoi du fichier audio au serveur Flask
            fetch('/transcribe', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
              .then(data => {
                  if (data.error) {
                      console.error('Erreur lors de la reconnaissance vocale :', data.error);
                  } else {
                      console.log('Texte reconnu :', data.text);
                  }
              })
              .catch(error => console.error('Erreur lors de l\'envoi de l\'audio :', error));
        };

        mediaRecorder.start();

        // Arrêt de l'enregistrement après 5 secondes
        setTimeout(() => mediaRecorder.stop(), 5000);
    }).catch(function (error) {
        console.error('Erreur lors de l\'accès au micro:', error);
    });
}
