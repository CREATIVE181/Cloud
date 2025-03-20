from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.getenv("PASSWORD")

app = Flask(__name__)
app.secret_key = b'\x8f%)\x08H\\*x\x96\r\x9e\x17\xb7<\xa9\xae\n\xca\x02\x90\xa3)\x937E.\xc7\x13\xa0\xd0\x83\xb1\x94\x14\x0b>\x1a\xa8\xeaA \xb2C\x17\xfb\xc0\x8f@\x1cO'  # Замените на свой ключ

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Простая авторизаци

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('cloud'))  # Исправлено: редирект на 'cloud'
        else:
            flash('Неверный пароль')
    return render_template('login.html')

@app.route('/home')
def cloud():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folders = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('cloud.html', folders=folders)

@app.route('/create_folder', methods=['POST'])
def create_folder():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folder_name = request.form.get('folder_name')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return redirect(url_for('cloud'))  # Исправлено: редирект на 'cloud'

@app.route('/folder/<folder_name>')
def open_folder(folder_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    files = os.listdir(folder_path)
    return render_template('folder.html', folder_name=folder_name, files=files)

@app.route('/upload/<folder_name>', methods=['POST'])
def upload_file(folder_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    file.save(os.path.join(folder_path, file.filename))
    return redirect(url_for('open_folder', folder_name=folder_name))

@app.route('/download/<folder_name>/<filename>')
def download_file(folder_name, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    return send_from_directory(folder_path, filename)

@app.route('/delete/<folder_name>/<filename>', methods=['POST'])
def delete_file(folder_name, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('open_folder', folder_name=folder_name))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/delete_folder/<folder_name>', methods=['POST'])
def delete_folder(folder_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if os.path.exists(folder_path):
        # Удаляем все файлы и папки внутри
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(folder_path)
    return redirect(url_for('cloud'))  # Исправлено: редирект на 'cloud'

# Удаляем запуск приложения через app.run()
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

