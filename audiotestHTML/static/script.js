document.addEventListener('DOMContentLoaded', () => {
  const startButton = document.getElementById('startButton');
  const microphoneIcon = document.getElementById('microphoneIcon');
  const textDisplay = document.getElementById('text-display');
  const recordedText = document.getElementById('recorded-text');
  const recordingStatus = document.getElementById('recording-status');
  const resultElement = document.getElementById('result');
  const navigationButtons = document.getElementById('navigation-buttons');
  const prevAyahButton = document.getElementById('prevAyah');
  const nextAyahButton = document.getElementById('nextAyah');
  const quranIcon = '<i class="fa-solid fa-book" style="color: #63E6BE;"></i>';


  let currentSuraNumber = null;
  let currentAyaNumber = null;

  if (startButton) {
      startButton.addEventListener('click', checkAndRequestPermissions);
  }

  if (microphoneIcon) {
      microphoneIcon.addEventListener('click', checkAndRequestPermissions);
  }

  if (prevAyahButton) {
      prevAyahButton.addEventListener('click', () => {
          if (currentSuraNumber && currentAyaNumber > 1) {
              fetchAyah(currentSuraNumber, currentAyaNumber - 1);
          }
      });
  }

  if (nextAyahButton) {
      nextAyahButton.addEventListener('click', () => {
          if (currentSuraNumber && currentAyaNumber) {
              fetchAyah(currentSuraNumber, currentAyaNumber + 1);
          }
      });
  }

  function checkAndRequestPermissions() {
      // Effacer le résultat précédent et afficher le statut d'enregistrement
      clearResult();
      showRecordingStatus();

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          navigator.mediaDevices.getUserMedia({ audio: true })
              .then(stream => {
                  startRecording(stream);
              })
              .catch(error => {
                  hideRecordingStatus();
                  if (error.name === 'PermissionDeniedError' || error.name === 'NotAllowedError') {
                      alert("Veuillez autoriser l'accès à votre microphone pour utiliser cette fonctionnalité.");
                  } else {
                      console.error('Erreur lors de l\'accès au microphone:', error);
                  }
              });
      } else {
          hideRecordingStatus();
          alert("Votre navigateur ne supporte pas l'enregistrement audio.");
      }
  }

  function startRecording(stream) {
      let options = { mimeType: 'audio/webm; codecs=opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          options = { mimeType: 'audio/ogg; codecs=opus' };
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
              options = { mimeType: '' };
          }
      }

      const mediaRecorder = new MediaRecorder(stream, options);
      let audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
              audioChunks.push(event.data);
          }
      };

      mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });

          // Envoyer le fichier audio au serveur pour transcription
          const formData = new FormData();
          formData.append('audio', audioBlob, 'audio.webm');

          fetch('/transcribe', {
              method: 'POST',
              body: formData
          })
          .then(response => response.json())
          .then(data => {
              hideRecordingStatus();

              if (data.result) {
                  displayResult(data.result);
                  showRecordedText(data.result.transcribed_text);
              } else if (data.error) {
                  alert(`Erreur : ${data.error}`);
              } else {
                  alert('Une erreur est survenue lors de la transcription. Veuillez réessayer.');
              }
          })
          .catch(error => {
              hideRecordingStatus();
              console.error('Erreur lors de la transcription:', error);
              alert('Une erreur est survenue lors de la transcription. Veuillez réessayer.');
          });
      };

      mediaRecorder.start();

      // Arrêt automatique après 5 secondes
      setTimeout(() => {
          mediaRecorder.stop();
      }, 5000);
  }

  function displayResult(result) {
    if (result && result.sura_number && result.aya_number) {
        currentSuraNumber = result.sura_number;
        currentAyaNumber = result.aya_number;

        const quranIcon = '<i class="fa-solid fa-quran" style="color: #63E6BE;"></i>';

        resultElement.innerHTML = `
            <p><strong>سورة ${result.sura_name} (${result.sura_number})</strong></p>
            <p><strong>الآية ${result.aya_number}:</strong></p>
            <p class="quran-text">${quranIcon} ${result.aya_text} ${quranIcon}</p>
            <p>نسبة التشابه: ${Math.round(result.similarity)}%</p>
        `;

        navigationButtons.style.display = 'block';
    } else {
        alert('Aucun résultat valide reçu du serveur.');
    }
}

  function clearResult() {
      resultElement.innerHTML = '';
      recordedText.textContent = '';
      textDisplay.classList.remove('visible');
      navigationButtons.style.display = 'none';
  }

  function showRecordedText(text) {
      if (text) {
          recordedText.textContent = text;
          textDisplay.classList.add('visible');
      }
  }

  function showRecordingStatus() {
      recordingStatus.innerHTML = '<p>جاري التسجيل...</p>';
      recordingStatus.classList.add('recording');
  }

  function hideRecordingStatus() {
      recordingStatus.innerHTML = '';
      recordingStatus.classList.remove('recording');
  }

  function fetchAyah(suraNumber, ayaNumber) {
      fetch(`/get_ayah?sura=${suraNumber}&aya=${ayaNumber}`)
          .then(response => response.json())
          .then(data => {
              if (data.success && data.result) {
                  currentSuraNumber = data.result.sura_number;
                  currentAyaNumber = data.result.aya_number;
                  displayResult(data.result);
              } else if (data.error) {
                  alert(`Erreur : ${data.error}`);
              } else {
                  alert('هذه الآية غير موجودة.');
              }
          })
          .catch(error => {
              console.error('Erreur lors de la récupération de l\'ayah:', error);
              alert('Une erreur est survenue. Veuillez réessayer.');
          });
  }
});
