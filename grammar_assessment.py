
import speech_recognition as sr
import language_tool_python
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from itertools import product

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
    return grammar_marks,total_words

def calculate_semantic_score(text):
    # Tokenize the text into words
    tokens = word_tokenize(text)

    # Calculate semantic similarity score
    similarity_scores = []
    for word1 in tokens:
        max_similarity = 0
        for word2 in tokens:
            if word1 != word2:
                synsets1 = wn.synsets(word1)
                synsets2 = wn.synsets(word2)
                if synsets1 and synsets2:
                    for synset1, synset2 in product(synsets1, synsets2):
                        similarity = synset1.path_similarity(synset2)
                        if similarity is not None and similarity > max_similarity:
                            max_similarity = similarity
        similarity_scores.append(max_similarity)

    # Calculate average similarity score
    if similarity_scores:
        semantic_score = sum(similarity_scores) / len(similarity_scores)*100
    else:
        semantic_score = 0

    return semantic_score



if __name__ == "__main__":
    app.run(debug=True)
