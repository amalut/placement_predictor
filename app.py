from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import pandas as pd
import pickle
from mcq import app as mcq_app
from mcq import questions_list
from mcq import *
from grammar_assessment import *
import json
from urllib.parse import urlencode
from urllib.parse import parse_qs

app = Flask(__name__)

API_KEY = "AIzaSyBF-gktODbomUIyPOT_MWuGqxFwDP-Mx8I"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

model = pickle.load(open('model.pkl', 'rb'))
stream_dummies = pd.read_csv('stream_dummies.csv', index_col=0)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}", json=data)
    response_data = response.json()

    if response.ok:
        id_token = response_data.get('idToken')
        decoded_token = auth.verify_id_token(id_token)
        user_email = decoded_token['email']
        user_id = response_data.get('localId')
        return redirect(url_for('home_page', user_email=user_email, user_id=user_id))
    else:
        error_message = response_data.get('error', {}).get('message', 'Unknown error')
        return render_template('login.html', error=error_message)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup_page', methods=['POST'])
def signup_page():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    if password != confirm_password:
        error = 'Passwords do not match'
        return render_template('signup.html', error=error)
    
    try:
        user = auth.create_user(email=email, password=password)
        user_id = user.uid
        print(user.email)
        return redirect(url_for('form', user_id=user_id, user_email=email))
    except Exception as e:
        error_message = str(e)
        return render_template('signup.html', error=error_message)

@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_home', methods=['POST'])
def admin_home():
    email = request.form.get('email')
    password = request.form.get('password')
    if email=="admin@gmail.com" and password=="admin123":
        users_ref = db.collection(u'users')
        users = users_ref.stream()
        user_data = []
        for user in users:
            user_data.append(user.to_dict())
        return render_template('admin_home.html', users=user_data)
    else:
        error_message = "Invalid details!"
        return render_template('admin_login.html', error=error_message)

@app.route('/students')
def students():
    users_ref = db.collection(u'users')
    users = users_ref.stream()
    user_data = []
    for user in users:
        user_data.append(user.to_dict())
    return render_template('student_details.html', users=user_data)

@app.route('/form/<user_id>/<user_email>')
def form(user_id, user_email):
    return render_template('form.html', user_id=user_id, user_email=user_email)

@app.route('/submit_form/<user_id>/<user_email>', methods=['POST'])
def submit_form(user_id, user_email):
    try:
        formData = request.form.to_dict()
        formData['aptitude'] = 0
        formData['communication'] = 0
        db.collection('users').document(user_id).set(formData)
        return redirect(url_for('home_page', user_id=user_id, user_email=user_email))
    except Exception as e:
        error_message = str(e)
        return render_template('form.html', error=error_message)

@app.route('/home/<user_id>/<user_email>')
def home_page(user_id, user_email):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            userData = user_doc.to_dict()
            return render_template('home.html', user_id=user_id, userData=userData, userEmail=user_email)
        else:
            return "User data not found"
    except Exception as e:
        print("Error:", e)
        return "Error occurred: " + str(e)


@app.route('/predict/<user_id>')
def predict(user_id):
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        userData = user_doc.to_dict()

        # Preprocess the input
        cgpa = float(userData['cgpa'])
        internships = int(userData['num_internships'])
        communication = float(userData['communication'])
        aptitude = float(userData['aptitude'])
        stream = userData['dept']

        new_student_stream_dummy = stream_dummies.loc[stream_dummies[f'Stream_{stream}'] == 1].values.tolist()[0]

        new_student_features = [cgpa, communication, aptitude, internships]  + new_student_stream_dummy

        # Convert the input to a 2D array
        new_student_features = [new_student_features]

        # Make a prediction using the model
        prediction = model.predict(new_student_features)
        prob = model.predict_proba(new_student_features)
        pro = prob[0][1] * 100
        pre=int(prediction[0])
        user_ref.update({'placement_chance': pro})
        user_ref.update({'placement_pre': pre})

        return redirect(url_for('result', prediction=pre, pro=pro, userData=urlencode({'userData': json.dumps(userData)})))

    else:
        return "User data not found"

@app.route('/result/<prediction>/<pro>/<userData>')
def result(prediction, pro, userData):
    userData = json.loads(parse_qs(userData)['userData'][0])  # convert the stringified dictionary back to a dictionary
    return render_template('result.html', prediction=prediction, pro=float(pro), userData=userData)
    
    
@app.route('/aptitude/<user_id>', methods=['GET', 'POST'])
def index(user_id):
    if request.method == 'POST':
        score = run_mcq_quiz(questions_list)
        total=len(questions_list)
        apt_score=score/total*10
        if user_id:
            # Update the user document in Firestore with the new aptitude score
            user_ref = db.collection('users').document(user_id)
            user_ref.set({
                'aptitude': apt_score
            }, merge=True)

            return render_template('aptitude/result.html', score=score, apt_score=apt_score, total=total, user_id=user_id)
        else:
            # Redirect to the login page if the user is not logged in
            return redirect(url_for('login_page'))

    return render_template('aptitude/quiz.html', questions=enumerate(questions_list, 1))

@app.route('/communication/<user_id>')
def communication(user_id):
    return render_template('communication/grammar_test.html',user_id=user_id)


@app.route('/record/<user_id>', methods=['POST'])
def record(user_id):
    try:
        with sr.Microphone() as source:
            print("Say something...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=120)

        transcribed_text = transcribe_audio(audio)
        grammar_marks = calculate_grammar_marks(transcribed_text)
        score=grammar_marks/100*10

        if user_id:
            # Update the user document in Firestore with the new aptitude score
            user_ref = db.collection('users').document(user_id)
            user_ref.set({
                'communication': score
            }, merge=True)

            return render_template('communication/grammar_mark.html', score=score, grammar_marks=grammar_marks,user_id=user_id)

        # Store transcribed text in a text file
        with open("transcribed_text.txt", "w") as file:
            file.write(transcribed_text)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
