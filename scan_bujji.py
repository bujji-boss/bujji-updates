import sys
import wave, numpy as np, onnxruntime as ort

wav = sys.argv[1] if len(sys.argv) > 1 else "live_loop.wav"
mel_sess = ort.InferenceSession("features/melspectrogram.onnx")
emb_sess = ort.InferenceSession("features/embedding_model.onnx")
wake_sess = ort.InferenceSession("bujji_final_wakeword_model_single.onnx")

with wave.open(wav, "rb") as f:
    audio = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

mel_name = mel_sess.get_inputs()[0].name
emb_name = emb_sess.get_inputs()[0].name
wake_name = wake_sess.get_inputs()[0].name

for start in range(0, len(audio) - 16000 * 3 + 1, 16000):
    chunk = audio[start:start + 16000 * 3]
    mel = mel_sess.run(None, {mel_name: chunk.reshape(1, -1)})[0]
    mel = np.transpose(mel, (0, 2, 3, 1))

    embeddings = []
    for i in range(0, mel.shape[1] - 76 + 1, 8):
        window = mel[:, i:i+76, :, :]
        emb = emb_sess.run(None, {emb_name: window.astype(np.float32)})[0]
        embeddings.append(emb.reshape(96))

    embeddings = np.array(embeddings, dtype=np.float32)
    if len(embeddings) >= 16:
        features = embeddings[-16:].reshape(1, 16, 96)
        score = float(wake_sess.run(None, {wake_name: features})[0][0])
        print(f"{start/16000:.1f}s - {(start+48000)/16000:.1f}s : {score:.4f} " +
              ("<-- BUJJI TRIGGER" if score > -0.6 else ""))

print("SCAN COMPLETE")

