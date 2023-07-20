"""
Purpose:
    API for the application.
"""


from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from cryptography.fernet import Fernet
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
path = str(os.path.dirname(os.path.abspath(__file__)))
path = path.replace('\\', '/')
app.config['UPLOAD_FOLDER'] = path + '/static/files'
# Azure Storage Account Configuration
connection_string = 'DefaultEndpointsProtocol=https;AccountName=trialdr;AccountKey=x93qAnyxLLduyIAaNonrSCWYolHKXptDOwla8j1w00PgYufv2JIZdoGSponIT7PAEJJfErcVmLeV+AStuzKM1g==;EndpointSuffix=core.windows.net'
container_name = 'diya'


# Generating the Encryption key
key_file = 'encryption_key.key'
encryption_key = None


def generate_key():
    global encryption_key
    encryption_key = Fernet.generate_key()
    with open(key_file, 'wb') as file:
        file.write(encryption_key)


def load_key():
    global encryption_key
    with open(key_file, 'rb') as file:
        encryption_key = file.read()


if not os.path.isfile(key_file):
    generate_key()
else:
    load_key()

logging.basicConfig(level=logging.DEBUG)


# Funtion to encrypt the file


def encrypt_file(file_data):
    fernet = Fernet(encryption_key)
    encrypted_data = fernet.encrypt(file_data)
    return encrypted_data


@app.route('/', methods=('GET', 'POST'))
@app.route('/index', methods=('GET', 'POST'))
def index():
    header_1 = 'Red Flags'
    header_2 = 'For Back Pain'
    explanation = """
    Some cases of back pain can be serious, and require immediate medical attention.
    We are going to ask a few questions to understand the nature of your pain.
    """
    return render_template('index.html', header_1=header_1, header_2=header_2, explanation=explanation)


@app.route('/red_flags', methods=('GET', 'POST'))
@app.route('/red_flags/<int:question_number>', methods=('GET', 'POST'))
def red_flags_questionnaire(question_number: int = 0):
    num_question = 3
    header_1 = 'Is your back pain associated with any of the following?'
    if question_number and request.args.get('answer') == 'Yes':
        header_1 = 'You need immediate care'
        explanation = """
            You answered 'Yes' to a question indicating you could be in need of emergency care. 
            Use the map below to see some providers.
            """
        map_link = 'https://goo.gl/maps/zKXs4iFKqaqDwfJy6'
        return render_template('immediate_care.html', header_1=header_1, explanation=explanation, map_link=map_link)
    elif not question_number:
        question_number = 1
    elif question_number > num_question:
        return redirect(url_for('mobile_msk_questionnaire'))
    question, answers, more_information = model.get_red_flag_question(
        question_number)
    return render_template('Red_Flags.html', header_1=header_1, question=question, answers=answers,
                           more_information=more_information, next_question_number=question_number + 1)


@app.route('/Questionnaire', methods=('GET', 'POST'))
def mobile_msk_questionnaire():
    questions, answers = model.Get_Questions_And_Answers()
    if request.method == 'POST':
        for q in questions:
            answers[q] = request.form.get(q)
        diagnosis_URL = model.diagnose(questions, answers)
        return render_template('Diagnosis.html', questions=questions, answers=answers, diagnosis=diagnosis_URL)
    terms_conditions_url = url_for('temp_placeholder')
    return render_template('questionnaire.html', questions=questions, answers=answers,
                           terms_conditions_url=terms_conditions_url)


@app.route('/OSWENTRY_Back_Pain')
def OSWENTRY_Low_Back_Pain_questionnaire():
    questions = model.get_OSWENTRY_questionnaire()
    post_URL = url_for('OSWENTRY_Low_Back_Pain_questionnaire_evaluation')
    return render_template('OSWENTRY_questionnaire.html', questions=questions, post_URL=post_URL)


@app.route('/OSWENTRY_Back_Pain', methods=['POST'])
def OSWENTRY_Low_Back_Pain_questionnaire_evaluation():
    score = model.score_OSWENTRY(request.form)
    disability = model.get_OSWENTRY_disability_level(score)
    return render_template('OSWENTRY_results.html', score=score, disability=disability)


@app.route('/upload', methods=['GET'])
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file found"

    file = request.files['file']

    if file.filename == '':
        return "No file selected"

    # Encrypting the file data
    encrypted_data = encrypt_file(file.read())

    # Saving the file
    try:
     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
     container_client = blob_service_client.get_container_client(container_name)
     encrypted_filename = secure_filename(file.filename) + '.encrypted'
     blob_client = container_client.get_blob_client(encrypted_filename)
     blob_client.upload_blob(encrypted_data)
     return "File Encrypted and uploaded successfully"

    except Exception as e:
        error_message = f"File upload failed. Error: {str(e)}"
        logging.exception(error_message)
        return error_message


if __name__ == '__main__':
    app.run(debug=True)
