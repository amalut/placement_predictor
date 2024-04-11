from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, StringField, SubmitField
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import pandas as pd
import pickle
from mcq import app as mcq_app
from mcq import questions_list
from mcq import *

app = Flask(__name__)

API_KEY = "AIzaSyBF-gktODbomUIyPOT_MWuGqxFwDP-Mx8I"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

model = pickle.load(open('xgbmodel.pkl', 'rb'))
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

        return redirect(url_for('result', name=userData['name'], prediction=prediction[0], pro=pro))

    else:
        return "User data not found"

@app.route('/result/<name>/<prediction>/<pro>')
def result(name, prediction, pro):
    return render_template('result.html', name=name, prediction=prediction, pro=pro)
    
    
@app.route('/aptitude', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        score = run_mcq_quiz(questions_list)
        return render_template('aptitude/result.html', score=score, total=len(questions_list))

    return render_template('aptitude/quiz.html', questions=enumerate(questions_list, 1))

@app.route('/communication')
def communication():
    return render_template('communication.html')

if __name__ == '__main__':
    app.run(debug=True)
