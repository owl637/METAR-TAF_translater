function speakResult() {
  const textElement = document.getElementById("result-text");
  if (!textElement) {
      alert("読み上げ対象が見つかりません。");
      return;
  }

  const text = textElement.innerText;
  if (!window.speechSynthesis) {
      alert("このブラウザでは音声読み上げがサポートされていません。");
      return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "ja-JP";
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  speechSynthesis.speak(utterance);
}
