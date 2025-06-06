import speech_recognition as sr
import pyttsx3
import requests
import time

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition; {e}")
            return None

def process_with_gemini(text):
    try:
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyBwepEkfaQqeTrKKhJuERytq-S2SLLl2Uk",
            json={"contents": [{"parts": [{"text": f"Answer as if searching the internet: {text}"}]}],
                  "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.7}},
            headers={"Content-Type": "application/json"}
        )
        r.raise_for_status()
        text = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
        print(f"Gemini: {text}")
        return text
    except requests.exceptions.HTTPError as e:
        status = r.status_code
        errors = {400: "Bad request", 429: "Overloaded, retrying...", 404: "Model not found", 403: "Forbidden"}
        print(errors.get(status, f"Error: {e}"))
        if status == 429:
            time.sleep(5)
            return process_with_gemini(text)
        return "API error"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "API error"

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    print("Say 'python' to activate at any time...")
    while True:
        wake_word = recognize_speech()
        if wake_word and wake_word.lower().strip() == "python":
            speak_text("Python activated. Please speak your query.")
            # Process main query
            input_text = recognize_speech()
            if input_text:
                gemini_response = process_with_gemini(input_text)
                if gemini_response:
                    speak_text(gemini_response)
        # Continuous listening without asking to continue unless a query is processed
        print("Listening for 'python' or say 'exit' to stop...")
        continue_response = recognize_speech()
        if continue_response and "exit" in continue_response.lower():
            speak_text("Goodbye")
            break

if __name__ == "__main__":
    main()