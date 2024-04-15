from flask import Flask, render_template, request
import speech_recognition as sr
import language_tool_python

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')

def transcribe_audio(audio):
    recognizer = sr.Recognizer()
    text = ""
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results: {}".format(e))
    return text

def calculate_grammar_marks(text):
    matches = tool.check(text)
    grammar_errors = len(matches)
    total_words = len(text.split())
    grammar_marks = max(0, total_words - grammar_errors) / total_words * 100
    return grammar_marks

@app.route('/')
def index():
    return render_template('grammar_test.html')

@app.route('/record', methods=['POST'])
def record():
    try:
        with sr.Microphone() as source:
            print("Say something...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=120)

        transcribed_text = transcribe_audio(audio)
        grammar_marks = calculate_grammar_marks(transcribed_text)

        # Store transcribed text in a text file
        with open("transcribed_text.txt", "w") as file:
            file.write(transcribed_text)

        return render_template('grammar_mark.html', grammar_marks=grammar_marks)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
