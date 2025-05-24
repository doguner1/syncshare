from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import os
import qrcode
import webbrowser

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB sınır


shared_text = ""

def generate_qr_code(url):
    qr_path = os.path.join(STATIC_FOLDER, 'qr.png')
    qrcode.make(url).save(qr_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    global shared_text

    if request.method == 'POST':
        if 'text' in request.form:
            shared_text = request.form['text']
        elif 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = file.filename
                chunk_size = 4096
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                with open(save_path, 'wb') as f:
                    while True:
                        chunk = file.stream.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    url = request.host_url.rstrip('/')
    generate_qr_code(url)
    return render_template('index.html', text=shared_text, files=files, qr_url=url)



@app.route('/get_text')
def get_text():
    return jsonify({"text": shared_text})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/clear')
def clear():
    global shared_text
    shared_text = ""
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)