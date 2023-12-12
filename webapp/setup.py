from flask import Flask, render_template, redirect, request, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
import tensorflow
import numpy as np
import pickle
import subprocess

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'bucket')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}

MODEL = tensorflow.keras.models.load_model(os.path.join(MODEL_DIR, 'model.h5'))
REC_MODEL = pickle.load(open(os.path.join(MODEL_DIR, 'modell.pkl'), 'rb'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLASSES =[
    'Яблучна чорнявка', 
    'Яблучна чорна гниль', 
    'Яблучна іржа', 
    'Здорове яблуко', 
    'Здорова чорниця', 
    'Вишня (включаючи кислу) Порошкоподібна біла пляма', 
    'Здорова вишня (включаючи кислу)', 
    'Кукурудза Листкова пляма Cercospora Сіра пляма', 
    'Кукурудза Звичайна ржавчина', 
    'Кукурудза Північна пляма на листі', 
    'Кукурудза Здорова', 
    'Виноградна чорна гниль', 
    'Виноградна Еска (Чорний кір)', 
    'Виноградна пляма листя (Пляма на листі Isariopsis)', 
    'Здоровий виноград', 
    'Апельсинове хвороба Гаунглонгбінг (цитрусове уживання)', 
    'Персиковий бактеріальний плямистий', 
    'Здоровий персик', 
    'Болгарський перець Бактеріальний плямистий', 
    'Здоровий болгарський перець', 
    'Картопля Ранній в\'ялотний', 
    'Картопля Пізній в\'ялотний', 
    'Здорова картопля', 
    'Малина Здорова', 
    'Соя Здорова', 
    'Гарбузова Порошкоподібна біла пляма', 
    'Клубіння Пляма листя', 
    'Здорова клубіння', 
    'Помідор Бактеріальний плямистий', 
    'Помідор Ранній в\'ялотний', 
    'Помідор Пізній в\'ялотний', 
    'Помідор Плісня листя', 
    'Помідор Пляма Септорії листя', 
    'Помідор Павукові кліщі (двоплямистий павуковий кліщ)', 
    'Помідор Цільова пляма', 
    'Помідор Вірус жовтої листкової кручі', 
    'Помідор Мозаїчний вірус помідора', 
    'Здорові помідори'
]


@app.route('/')
def home():
        return render_template("index.html")

@app.route("/streamlit")
def streamlit():
    # Call the Streamlit app using subprocess
    subprocess.run(["streamlit", "run", "system.py"])
    return "Streamlit app is running!"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/plantdisease/<res>')
def plantresult(res):
    print(res)
    corrected_result = ""
    for i in res:
        if i!='_':
            corrected_result = corrected_result+i
    return render_template('plantdiseaseresult.html', corrected_result=corrected_result)

@app.route('/plantdisease', methods=['GET', 'POST'])
def plantdisease():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Завантаження попередньо навченої моделі глибокого навчання з TensorFlow
            model = MODEL
            # Завантаження зображення та підготовка його для подальшого аналізу
            imagefile = tensorflow.keras.utils.load_img(os.path.join(app.config['UPLOAD_FOLDER'], filename), target_size=(224, 224, 3))
            input_arr = tensorflow.keras.preprocessing.image.img_to_array(imagefile)
            input_arr = np.array([input_arr])
            # Передбачення застосованої моделі на зображенні
            result = model.predict(input_arr)
            probability_model = tensorflow.keras.Sequential([model, 
                                         tensorflow.keras.layers.Softmax()])
            predict = probability_model.predict(input_arr)
            p = np.argmax(predict[0])
            res = CLASSES[p]
            print(res)
            return redirect(url_for('plantresult', res=res))
    return render_template("plantdisease.html")

@app.route('/croprecommendation/<res>')
def cropresult(res):
    print(res)
    corrected_result = res
    return render_template('croprecresult.html', corrected_result=corrected_result)

@app.route('/croprecommendation', methods=['GET', 'POST'])
def cr():
    if request.method == 'POST':
        X = []
        if request.form.get('nitrogen'):
            X.append(float(request.form.get('nitrogen')))
        if request.form.get('phosphorous'):
            X.append(float(request.form.get('phosphorous')))
        if request.form.get('potassium'):
            X.append(float(request.form.get('potassium')))
        if request.form.get('temperature'):
            X.append(float(request.form.get('temperature')))
        if request.form.get('humidity'):
            X.append(float(request.form.get('humidity')))
        if request.form.get('ph'):
            X.append(float(request.form.get('ph')))
        if request.form.get('rainfall'):
            X.append(float(request.form.get('rainfall')))
        X = np.array(X)
        X = X.reshape(1, -1)
        res = REC_MODEL.predict(X)[0]
        # print(res)
        return redirect(url_for('cropresult', res=res))
    return render_template('croprec.html')



if __name__== "__main__":
    app.run(debug=True)