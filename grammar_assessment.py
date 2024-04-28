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
    print(f"Total:{total_words} Gramemr errors:{grammar_errors}")
    grammar_marks = max(0, total_words - grammar_errors) / total_words * 100
    return grammar_marks



if __name__ == "__main__":
    app.run(debug=True)
