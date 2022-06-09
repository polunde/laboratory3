from flask import Flask, request, render_template, redirect, url_for, flash
from config import Config
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from skimage import io
from PIL import Image
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from pathlib import Path


class SignupForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField(label="Submit")


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
my_site_key = app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdSXSMgAAAAAHQgMIIoeoXxbEYRuip_zpRnLK0a'
my_private_key = app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdSXSMgAAAAAP8GPoEby3vYKmEbbHInhv2eG0y3'
height, width = 400, 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_histogram(image, flag: int):
    filepath = str(Path('uploads').absolute())
    _ = plt.hist(image.ravel(), bins=256, color='orange', )
    _ = plt.hist(image[:, :, 0].ravel(), bins=256, color='red', alpha=0.5)
    _ = plt.hist(image[:, :, 1].ravel(), bins=256, color='Green', alpha=0.5)
    _ = plt.hist(image[:, :, 2].ravel(), bins=256, color='Blue', alpha=0.5)
    _ = plt.xlabel('Intensity Value')
    _ = plt.ylabel('Count')
    _ = plt.legend(['Total', 'Red_Channel', 'Green_Channel', 'Blue_Channel'])
    if flag == 0:
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'temporary.png'))
    if flag == 1:
        plt.savefig(os.path.join(app.config['UPLOAD_FOLDER'], 'temporary_resized.png'))


@app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload_form():
    global form
    form = SignupForm()
    return render_template('download image.html', form=form)


@app.route('/wh', methods=['POST'])
def get_values():
    global height, width
    if request.method == 'POST':
        height = int(request.form.get('height'))
        width = int(request.form.get('width'))
    print(height, width)
    return render_template('download image.html', height=height, width=width)


@app.route('/', methods=['POST'])
def upload_image():
    if form.is_submitted():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Картинка не загружена')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(width, height)
            image = image.resize((width, height))
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], 'resized' + filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_path_resize = os.path.join(app.config['UPLOAD_FOLDER'], 'resized' + filename)
            image_histogram(io.imread(file_path), 0)
            image_histogram(io.imread(file_path_resize), 1)
            mat_filename = 'temporary.png'
            mat_filename_resized = 'temporary_resized.png'
            # print('upload_image filename: ' + filename)
            flash('Картинка загружена и отображена ниже')
            print(height, width)
            return render_template('download image.html', filename='resized' + filename, mat_filename=mat_filename,
                                   mat_filename_resized=mat_filename_resized, height=height,
                                   width=width, my_site_key=my_site_key, form=form)
        else:
            flash('Доступны форматы jpg, jpeg, png')
            return redirect(request.url)
    else:
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/display/<mat_filename>')
def display_imagemap():
    return redirect(url_for('static', mat_filename='uploads/temporary.png'), code=301)


@app.route('/display/<mat_filename_resized>')
def display_imagemap_resized():
    return redirect(url_for('static', mat_filename='uploads/temporary_resized.png'), code=301)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
