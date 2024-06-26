from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, abort
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import pandas as pd
import pickle
from mcq import questions_list
from mcq import run_mcq_quiz
from grammar_assessment import *
import json
from urllib.parse import urlencode
from urllib.parse import parse_qs
from model import average_values
from recommendation import recommend_for_student
from pyq import get_paper_list
import os

app = Flask(__name__)


API_KEY = "AIzaSyBF-gktODbomUIyPOT_MWuGqxFwDP-Mx8I"

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

model = pickle.load(open('model.pkl', 'rb'))
stream_dummies = pd.read_csv('stream_dummies.csv', index_col=0)
def get_type(value):
    return type(value)

app.jinja_env.filters['type'] = get_type

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
        return redirect(url_for('home_page', user_id=user_id))
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
        db.collection('users').document(user_id).set({'email': email})
        return redirect(url_for('form', user_id=user_id))
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

@app.route('/ad_home')
def ad_home():
    return render_template('admin_home.html')

@app.route('/placement_form')
def placement():
    return render_template('placement_form.html')

@app.route('/submit_success')
def submit_success():
    msg="Successfully Added New Placement Drive"
    return render_template('placement_form.html',msg=msg)

@app.route('/postnewplacement', methods=['POST'])
def submit_placement():
    try:
        formData = request.form.to_dict()
        departments = request.form.getlist('dept')
        formData['dept'] = ', '.join(departments)
        new_placement = db.collection('newplacements').document()
        new_placement.set(formData)
        return redirect(url_for('submit_success'))
    except Exception as e:
        error_message = 'Error adding new placement: {}'.format(e)
        return render_template('placement_form.html', error=error_message)

@app.route('/form/<user_id>')
def form(user_id):
    return render_template('form.html', user_id=user_id)

@app.route('/submit_form/<user_id>', methods=['POST'])
def submit_form(user_id):
    try:
        formData = request.form.to_dict()
        formData['aptitude'] = 0
        formData['communication'] = 0
        db.collection('users').document(user_id).set(formData, merge=True)
        return redirect(url_for('home_page', user_id=user_id))
    except Exception as e:
        error_message = str(e)
        return render_template('form.html', error=error_message)

@app.route('/home/<user_id>')
def home_page(user_id):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            userData = user_doc.to_dict()
            return render_template('home.html', user_id=user_id, userData=userData)
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
        # Make a prediction using the model
        prediction = model.predict([new_student_features])
        prob = model.predict_proba([new_student_features])
        pro = round(prob[0][1] * 100,2)
        if pro<0.01:
            pro=0.01
        pre=int(prediction[0])
        user_ref.update({'placement_chance': pro})
        user_ref.update({'placement_pre': pre})
        recommendations = recommend_for_student(prob[0][1],new_student_features, average_values)
        return redirect(url_for('result', user_id=user_id, prediction=pre, pro=pro,rec=json.dumps(recommendations), userData=urlencode({'userData': json.dumps(userData)})))

    else:
        return "User data not found"

@app.route('/result/<user_id><prediction>/<pro>/<userData>/<rec>')
def result(user_id,prediction, pro, userData,rec):
    if rec:
        try:
            rec = json.loads(rec) # Convert the string back to a list
        except json.JSONDecodeError:
            rec = []  # Set rec to an empty list if decoding fails
    userData = json.loads(parse_qs(userData)['userData'][0])  # convert the stringified dictionary back to a dictionary
    return render_template('result.html', rec=rec, prediction=prediction, pro=float(pro), userData=userData,user_id=user_id)
    

@app.route('/instructions/<user_id>')
def index(user_id):
    return render_template('aptitude/apt_instructions.html',user_id=user_id)
@app.route('/aptitude/<user_id>', methods=['GET', 'POST'])
def aptitude(user_id):
    if request.method == 'POST':
        score = run_mcq_quiz(questions_list)
        total=len(questions_list)
        apt_score=round(score/total*10,2)
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

@app.route('/com_instructions/<user_id>')
def com_instructions(user_id):
    return render_template('communication/com_instructions.html',user_id=user_id)

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
            audio = recognizer.listen(source, timeout=30)
        print("Stopped")
        print("Transcribing...")
        transcribed_text = transcribe_audio(audio)
        print(transcribed_text)
        grammar_marks,tot_words = calculate_grammar_marks(transcribed_text)
        print(grammar_marks)
        print(tot_words)
        grammar_marks=grammar_marks*0.9
        semantic_mark=calculate_semantic_score(transcribed_text)
        print(semantic_mark)
        semantic_mark=semantic_mark*0.1

        total=semantic_mark+grammar_marks
        score=round(total*0.1,2)

        print("Grammer score:",grammar_marks)
        print("Semantic mark:",semantic_mark)
        print("score:",score)
        with open("transcribed_text.txt", "w") as file:
            file.write(transcribed_text)

        if tot_words>25:
            if user_id:
                # Update the user document in Firestore with the new aptitude score
                user_ref = db.collection('users').document(user_id)
                user_ref.set({
                    'communication': score
                }, merge=True)

                return render_template('communication/grammar_mark.html', score=score, total=total,user_id=user_id)
        else:
            error="Audio is not clear,You have to speak atleast 25 words"
            return render_template('communication/grammar_test.html', error=error,user_id=user_id)

        # Store transcribed text in a text file

    except Exception as e:
        error="Could not understand audio,Try again"
    return render_template('communication/grammar_test.html', error=error,user_id=user_id)


@app.route('/drives/<user_id>')
def drives(user_id):
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        userData = user_doc.to_dict()
    dept=userData['dept']
    newplacements = db.collection('newplacements').stream()
    return render_template('drive.html', dept=dept,newplacements=newplacements,user_id=user_id)

@app.route('/pqpapers/<user_id>')
def pqpapers(user_id):
    papers = get_paper_list()
    return render_template('previousqp/index.html', papers=papers,user_id=user_id)

# Route to download a paper
@app.route('/downloadqp/<filename>')
def download_paper(filename):
    papers_dir = 'papers/'
    if os.path.isfile(os.path.join(papers_dir, filename)):
        return send_file(os.path.join(papers_dir, filename), as_attachment=True)
    else:
        abort(404)

@app.route('/viewqp/<filename>')
def view_paper(filename):
    papers_dir = 'papers/'
    if os.path.isfile(os.path.join(papers_dir, filename)):
        return send_file(os.path.join(papers_dir, filename), mimetype='application/pdf', as_attachment=False)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
