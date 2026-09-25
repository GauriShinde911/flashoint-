// Voice input using browser Web Speech API

let recognitionInstance = null;
let isListening = false;

function isSpeechSupported() {
  return "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
}

function initVoice(lang, onResultCallback, onEndCallback) {
  if (!isSpeechSupported()) {
    console.warn("Web Speech API not supported in this browser.");
    return null;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognitionInstance = new SpeechRecognition();
  recognitionInstance.continuous = false;
  recognitionInstance.interimResults = true;

  const langMap = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };
  recognitionInstance.lang = langMap[lang] || "en-IN";

  recognitionInstance.onresult = function (event) {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    if (onResultCallback) onResultCallback(transcript);
  };

  recognitionInstance.onend = function () {
    isListening = false;
    if (onEndCallback) onEndCallback();
  };

  recognitionInstance.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    isListening = false;
    if (onEndCallback) onEndCallback();
  };

  return recognitionInstance;
}

function startListening(lang, onResult, onEnd) {
  if (isListening) {
    stopListening();
    return;
  }
  initVoice(lang, onResult, onEnd);
  if (recognitionInstance) {
    recognitionInstance.start();
    isListening = true;
  }
}

function stopListening() {
  if (recognitionInstance && isListening) {
    recognitionInstance.stop();
    isListening = false;
  }
}
