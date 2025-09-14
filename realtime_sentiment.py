import pyaudio 
import wave
import os
import threading
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
OUTPUT_FILE = "chunk.wav"

SENTIMENT_PROMPT = """
You are a sentiment detection engine.
Classify the following text as Positive, Negative, or Neutral.
Text: "{}"
"""

running = True  

def record_chunk(filename):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    print("Listening...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(filename):
    with open(filename, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f
        )
    return transcription.text

def detect_sentiment(text):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text)}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def main():
    global running
    last_sentiment = None
    while running:
        record_chunk(OUTPUT_FILE)
        try:
            text = transcribe_audio(OUTPUT_FILE)
            if not text.strip():
                continue
            sentiment = detect_sentiment(text)
            print(f" Text: {text}")
            print(f" Sentiment: {sentiment}")
            if last_sentiment and sentiment != last_sentiment:
                print(f"⚠ Sentiment shift detected: {last_sentiment} → {sentiment}")
            last_sentiment = sentiment
        except Exception as e:
            print("Error:", e)

def wait_for_stop():
    global running
    input("Press Enter to stop recording...\n")
    running = False

if __name__ == "__main__":
    t = threading.Thread(target=main)
    t.start()
    wait_for_stop()
    t.join()
    print("Recording stopped.")
