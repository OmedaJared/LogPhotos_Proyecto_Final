from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email.message import EmailMessage
import smtplib
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
)

app.secret_key = "secret_key_provisoria"
# ...existing code...
 
# Configuración de MongoDB: usa tu URI real o local
app.config["MONGO_URI"] = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/photo_db"
)
mongo_client = MongoClient(app.config["MONGO_URI"])
mongo_db = mongo_client["photo_db"]

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    files = list(mongo_db.files.find({"owner": session['user']}))
    categories = mongo_db.files.distinct('category', {"owner": session['user']})
    return render_template('dashboard.html', files=files, categories=categories)

# ...existing code...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        mongo_db.users.insert_one({
            "email": request.form['email'],
            "password": hashed_pw
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message')
    if request.method == 'POST':
        user = mongo_db.users.find_one({"email": request.form['email']})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user'] = user['email']
            return redirect(url_for('index'))
    return render_template('login.html', message=message)

# --- RECUPERACIÓN DE CUENTA ---

from datetime import datetime, timedelta
import secrets

RESET_TOKEN_TTL_MINUTES = 30

def _create_reset_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
    mongo_db.reset_tokens.insert_one({
        "email": email,
        "token": token,
        "expires_at": expires_at
    })
    return token


def _send_email(to_address: str, subject: str, body: str) -> bool:
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("yamjarfer530")
    smtp_use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    if not smtp_host or not smtp_user or not smtp_pass:
        print("SMTP no configurado; no se envía correo.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_user
    message["To"] = to_address
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            if smtp_use_tls:
                smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(message)
        return True
    except Exception as exc:
        print("Error enviando correo:", exc)
        return False

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            return render_template('recover.html', error="Ingresa un correo válido.")

        user = mongo_db.users.find_one({"email": email})
        # No revelamos si existe el usuario
        if user:
            token = _create_reset_token(email)
            reset_url = url_for('reset_password', token=token, _external=True)
            email_sent = _send_email(
                email,
                "Recuperación de contraseña",
                f"Hola,\n\nHaz solicitado restablecer tu contraseña. Usa este enlace para crear una nueva contraseña:\n\n{reset_url}\n\nSi no solicitaste este correo, ignora este mensaje.\n"
            )
            if email_sent:
                return render_template('recover.html', message="Se envió un enlace de recuperación a tu correo.", email=email)
            return render_template('recover.html', error="No se pudo enviar el correo. Intenta de nuevo más tarde.", email=email)
        return render_template('recover.html', message="Si el correo existe, te enviaremos un enlace de recuperación.", email=email)

    return render_template('recover.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token: str):
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        if len(new_password) < 6:
            return render_template('reset.html', token=token, error="La contraseña debe tener al menos 6 caracteres.")

        token_doc = mongo_db.reset_tokens.find_one({"token": token})
        if not token_doc:
            return render_template('reset.html', token=token, error="Token inválido.")

        expires_at = token_doc.get("expires_at")
        if not expires_at or expires_at < datetime.utcnow():
            return render_template('reset.html', token=token, error="El token expiró. Solicita uno nuevo.")

        mongo_db.users.update_one(
            {"email": token_doc["email"]},
            {"$set": {"password": generate_password_hash(new_password)}}
        )
        mongo_db.reset_tokens.delete_many({"token": token})

        _send_email(
            token_doc["email"],
            "Contraseña restablecida",
            f"Tu nueva contraseña es: {new_password}\n\nSi no solicitaste este cambio, ignora este mensaje."
        )

        return redirect(url_for('login', message='Se envió la nueva contraseña a tu correo.'))

    return render_template('reset.html', token=token)

@app.route('/upload', methods=['POST'])
def upload_file():
    category = request.form.get('category', 'General')
    url = request.form.get('url', '').strip()
    
    if url:
        # Guardar link
        mongo_db.files.insert_one({
            "url": url,
            "owner": session['user'],
            "type": 'link',
            "category": category
        })
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return "Sin nombre"
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Guardar referencia en MongoDB
        mongo_db.files.insert_one({
            "filename": filename,
            "owner": session['user'],
            "type": file.content_type,
            "category": category
        })
    else:
        return "No hay archivo ni URL"
    
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_doc = mongo_db.files.find_one({"filename": filename, "owner": session['user']})
    if file_doc:
        mongo_db.files.delete_one({"_id": file_doc['_id']})
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/delete_link/<link_id>', methods=['POST'])
def delete_link(link_id):
    from bson import ObjectId
    mongo_db.files.delete_one({"_id": ObjectId(link_id), "owner": session['user']})
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
