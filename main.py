import pyttsx3
import requests
import time
import re

def recognizespeech():
    import speech_recognition as sr
    recognizer=sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio=recognizer.listen(source, timeout=5)
            text=recognizer.recognize_google(audio)
            print("You said: "+ text)
            return text
        except sr.WaitTimeoutError:
            print("Listening timed out, no speech detected.")
            return None
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print("Error with speech recognition service; {0}".format(e))
            return None

def geminiresponse(text, code_only=False):
    try:
        prompt = text
        if code_only:
            prompt = f"Only print the code for this request, no explanation or extra text: {text}"
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyBwepEkfaQqeTrKKhJuERytq-S2SLLl2Uk",
            json={"contents": [{"parts":[{"text": prompt}]}],
                  "generationConfig":{"maxOutputTokens":2048,"temperature":0.7}},
            headers={"Content-Type":"application/json"}
        )
        r.raise_for_status()
        response_text = r.json().get("candidates", [{}])[0].get("content",{}).get("parts",[{}])[0].get("text","No response")
        
        # Check if the input contains "write a program"
        if "write a program" in text.lower():
            # Extract code between triple backticks
            code_blocks = re.findall(r'```(?:\w*\n)?(.*?)```', response_text, re.DOTALL)
            if code_blocks:
                code = code_blocks[0].strip()
                print(f"Code:\n{code}")
                return code
            else:
                print("No code found in response")
                return "No code found"
        
        print(f"Gemini: {response_text}")
        return response_text
    except requests.exceptions.HTTPError as e:
        status=r.status_code
        errors={400:"Bad request",429:"Overloaded, retrying...",404:"Model not found",403: "Forbidden"}
        print(errors.get(status, f"Error: {e}"))
        if status==429:
            time.sleep(5)
            return geminiresponse(text)
        return "API error"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "API error"

def speak_text(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    print("Say 'python' to activate at any time...")
    while True:
        wakeword=recognizespeech()
        if wakeword and wakeword.lower().strip()=="python":
            speak_text("Python activated. Please speak your query.")
            inputtext=recognizespeech()
            if inputtext:
                gemini_response=geminiresponse(inputtext)
                if gemini_response:
                    speak_text(gemini_response)
        print("Listening for 'python' or say 'exit' to stop...")
        continue_response=recognizespeech()
        if continue_response and "exit" in continue_response.lower():
            speak_text("Goodbye")
            break
if __name__=="__main__":
    main()