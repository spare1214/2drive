import sqlite3
import hashlib
from datetime import date, datetime
import secrets
import smtplib
from email.mime.text import MIMEText
import os
from werkzeug.utils import secure_filename
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit, join_room
import json
import psycopg2
from psycopg2.extras import RealDictCursor


app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

socketio = SocketIO(app, cors_allowed_origins="*")

EMAIL_MITTENTE = "mohamedighir56@gmail.com"
EMAIL_PASSWORD = "sybc sxpy nmkx ujqz"

def connect_to_db():
    import sqlite3
    return sqlite3.connect('database.db', check_same_thread=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def invia_mail_verifica(email_destinatario, username, token):
    link = f"http://127.0.0.1:5000/verifica/{token}"
    corpo = f"""
Ciao {username}

Grazie per esserti registrato.

Clicca il link per attivare il tuo account

{link}
"""
    msg = MIMEText(corpo)
    msg["Subject"] = "Verifica account"
    msg["From"] = EMAIL_MITTENTE
    msg["To"] = email_destinatario

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_MITTENTE, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def valida_annuncio(data):
    try:
        prezzo = float(data['prezzo_annuncio'])
        if prezzo <= 0:
            return False, "Il prezzo deve essere positivo"
        if prezzo > 1000000:
            return False, "Il prezzo non può superare 1.000.000€"
        
        anno = int(data['anno'])
        if anno < 1900 or anno > 2026:
            return False, "L'anno deve essere compreso tra 1900 e 2026"
        
        chilometraggio = int(data['chilometraggio'])
        if chilometraggio < 0:
            return False, "Il chilometraggio non può essere negativo"
        if chilometraggio > 500000:
            return False, "Il chilometraggio non può superare 500.000 km"
        
        telefono = data['telefono'].strip()
        if len(telefono) < 9 or len(telefono) > 15:
            return False, "Il numero di telefono deve avere tra 9 e 15 cifre"
        
        modello = data['modello'].strip()
        if len(modello) < 2:
            return False, "Il modello deve avere almeno 2 caratteri"
        
        titolo = data['titolo'].strip()
        if len(titolo) < 5:
            return False, "Il titolo deve avere almeno 5 caratteri"
        
        return True, "OK"
    except ValueError:
        return False, "Dati non validi"
    except KeyError as e:
        return False, f"Campo mancante: {e}"

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page

    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT annuncio.id_annuncio) as total
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.stato = 'attivo'
    """)
    total_result = cursor.fetchone()
    total = total_result['total'] if total_result else 0

    cursor.execute("""
        SELECT DISTINCT annuncio.*, veicolo.modello, veicolo.anno, veicolo.chilometraggio, 
               veicolo.carburante, veicolo.cambio, veicolo.id_marca, marca.nome_marca, 
               utente.username as nome_utente
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        JOIN utente ON annuncio.id_utente = utente.id_utente
        WHERE annuncio.stato = 'attivo'
        ORDER BY annuncio.data_pubblicazione DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))

    annunci = []
    for row in cursor.fetchall():
        annuncio = dict(row)
        cursor.execute("SELECT url FROM immagine WHERE id_annuncio = ? LIMIT 1", (annuncio['id_annuncio'],))
        immagini = [dict(img) for img in cursor.fetchall()]
        annuncio['immagini'] = immagini
        annunci.append(annuncio)
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    cursor.close()
    conn.close()

    return render_template("index.html", 
                         annunci=annunci, 
                         page=page, 
                         total_pages=total_pages,
                         total=total)

@app.route("/register", methods=["GET","POST"])
def register():
    error = None

    if request.method == "POST":
        nome = request.form["nome"]
        cognome = request.form["cognome"]
        username = request.form["username"]
        email = request.form["email"]
        password = hash_password(request.form["password"])
        token = secrets.token_urlsafe(32)

        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM utente WHERE username=? OR email=?",
            (username, email)
        )

        if cursor.fetchone():
            error = "Username o email già esistente"
            cursor.close()
            conn.close()
            return render_template("login_register.html", panel="register", error=error)

        cursor.execute("""
            INSERT INTO utente
            (username,password,email,nome,cognome,data_registrazione,verificato,token_verifica)
            VALUES(?,?,?,?,?,?,?,?)
        """, (username, password, email, nome, cognome, date.today(), False, token))

        conn.commit()
        cursor.close()
        conn.close()

        invia_mail_verifica(email, username, token)

        error = "Registrazione completata! Controlla la tua email"
        return render_template("login_register.html", panel="login", error=error)

    return render_template("login_register.html", panel="register")

@app.route("/login", methods=["GET","POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_utente, password, verificato FROM utente WHERE username=?",
            (username,)
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            error = "Utente non trovato"
            return render_template("login_register.html", panel="login", error=error)

        if not result['verificato']:
            error = "Account non verificato"
            return render_template("login_register.html", panel="login", error=error)

        if result['password'] == password:
            session["user_id"] = result['id_utente']
            session["username"] = username
            return redirect(url_for("home"))
        else:
            error = "Password errata"
            return render_template("login_register.html", panel="login", error=error)

    return render_template("login_register.html", panel="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/verifica/<token>")
def verifica(token):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_utente FROM utente WHERE token_verifica=?",
        (token,)
    )

    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE utente SET verificato=1, token_verifica=NULL WHERE id_utente=?",
            (result[0],)
        )
        conn.commit()
        message = "Account verificato! Ora puoi fare login"
    else:
        message = "Token non valido"

    cursor.close()
    conn.close()
    return message

@app.route("/inserisci", methods=["GET","POST"])
def inserisci():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        valido, msg = valida_annuncio(request.form)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("inserisci"))
        
        titolo = request.form["titolo"]
        descrizione = request.form["descrizione"]
        prezzo_annuncio = request.form["prezzo_annuncio"]
        modello = request.form["modello"]
        anno = request.form["anno"]
        mese_immatricolazione = request.form.get("mese_immatricolazione", "")
        targa = request.form.get("targa", "")
        carburante = request.form["carburante"]
        cambio = request.form["cambio"]
        chilometraggio = request.form["chilometraggio"]
        colore = request.form["colore"]
        numero_posti = request.form.get("numero_posti", None)
        luogo = request.form.get("luogo", "")
        id_marca = request.form["marca"]
        id_categoria = request.form["categoria"]
        telefono = request.form["telefono"]
        mostra_telefono = 'mostra_telefono' in request.form
        
        if numero_posti:
            numero_posti = int(numero_posti)

        data_immatricolazione = None
        if anno and mese_immatricolazione:
            data_immatricolazione = f"{anno}-{mese_immatricolazione}-01"
        
        immagini_urls = []
        files = request.files.getlist("immagini")
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{int(time.time())}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                immagini_urls.append(f"/static/uploads/{unique_filename}")
        
        conn = connect_to_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO veicolo
                (modello, anno, data_immatricolazione, targa, carburante, cambio, 
                 chilometraggio, colore, numero_posti, luogo, id_marca, id_categoria, prezzo, telefono)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (modello, anno, data_immatricolazione, targa, carburante, cambio,
                  chilometraggio, colore, numero_posti, luogo, id_marca, id_categoria, 
                  prezzo_annuncio, telefono))
            
            id_veicolo = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO annuncio
                (titolo, descrizione, data_pubblicazione, stato, id_utente, id_veicolo, prezzo, telefono_visibile)
                VALUES(?,?,?,?,?,?,?,?)
            """, (titolo, descrizione, date.today(), "attivo", session["user_id"], 
                  id_veicolo, prezzo_annuncio, mostra_telefono))
            
            id_annuncio = cursor.lastrowid
            
            for url in immagini_urls:
                cursor.execute("INSERT INTO immagine (url, id_annuncio) VALUES(?,?)", (url, id_annuncio))
            
            conn.commit()
            flash("Annuncio pubblicato con successo!", "success")
            
        except Exception as e:
            conn.rollback()
            print(f"Errore: {e}")
            flash(f"Errore: {str(e)}", "error")
            return redirect(url_for("inserisci"))
            
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for("home"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM marca ORDER BY nome_marca")
    marche = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM categoria")
    categorie = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template("inserisci.html", marche=marche, categorie=categorie)

@app.route("/annuncio/<id>")
def annuncio(id):
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("UPDATE annuncio SET visualizzazioni = visualizzazioni + 1 WHERE id_annuncio = ?", (id,))
    conn.commit()

    cursor.execute("""
        SELECT annuncio.*, veicolo.*, marca.nome_marca
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.id_annuncio = ?
    """, (id,))

    annuncio_row = cursor.fetchone()

    if annuncio_row:
        annuncio_dict = dict(annuncio_row)
        cursor.execute("SELECT url FROM immagine WHERE id_annuncio = ?", (id,))
        immagini = [dict(img) for img in cursor.fetchall()]
        annuncio_dict['immagini'] = immagini
    else:
        annuncio_dict = None

    cursor.close()
    conn.close()

    if not annuncio_dict:
        return "Annuncio non trovato", 404

    return render_template("annuncio.html", annuncio=annuncio_dict)

@app.route("/cerca")
def cerca():
    query = request.args.get('q', '')
    sort = request.args.get('sort', 'recent')
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = """
        SELECT annuncio.*, veicolo.*, marca.nome_marca
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.stato = 'attivo'
    """
    params = []
    
    if query:
        sql += " AND (annuncio.titolo LIKE ? OR veicolo.modello LIKE ? OR marca.nome_marca LIKE ?)"
        search_term = f"%{query}%"
        params.extend([search_term, search_term, search_term])

    if sort == 'price_asc':
        sql += " ORDER BY annuncio.prezzo ASC"
    elif sort == 'price_desc':
        sql += " ORDER BY annuncio.prezzo DESC"
    else:
        sql += " ORDER BY annuncio.data_pubblicazione DESC"
    
    cursor.execute(sql, params)
    annunci = []
    for row in cursor.fetchall():
        a_dict = dict(row)
        cursor.execute("SELECT url FROM immagine WHERE id_annuncio = ? LIMIT 1", (a_dict['id_annuncio'],))
        immagini = [dict(img) for img in cursor.fetchall()]
        a_dict['immagini'] = immagini
        annunci.append(a_dict)
    
    cursor.close()
    conn.close()
    
    return render_template("ricerca.html", annunci=annunci, query=query, sort=sort)

@app.route("/chat")
def chat_lista():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            c.id_conversazione,
            c.id_annuncio,
            c.ultimo_messaggio,
            c.ultimo_aggiornamento,
            a.titolo as annuncio_titolo,
            a.prezzo,
            CASE 
                WHEN c.id_acquirente = ? THEN vend.username
                ELSE acq.username
            END as altro_utente,
            CASE 
                WHEN c.id_acquirente = ? THEN c.id_venditore
                ELSE c.id_acquirente
            END as altro_utente_id,
            (SELECT COUNT(*) FROM messaggio WHERE id_conversazione = c.id_conversazione AND id_destinatario = ? AND letto = 0) as non_letti
        FROM conversazione c
        JOIN annuncio a ON c.id_annuncio = a.id_annuncio
        JOIN utente vend ON c.id_venditore = vend.id_utente
        JOIN utente acq ON c.id_acquirente = acq.id_utente
        WHERE c.id_acquirente = ? OR c.id_venditore = ?
        ORDER BY c.ultimo_aggiornamento DESC
    """, (session["user_id"], session["user_id"], session["user_id"], session["user_id"], session["user_id"]))
    
    conversazioni = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return render_template("chat_lista.html", conversazioni=conversazioni)

@app.route("/chat/<int:id_conversazione>")
def chat_dettaglio(id_conversazione):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM conversazione 
        WHERE id_conversazione = ? AND (id_acquirente = ? OR id_venditore = ?)
    """, (id_conversazione, session["user_id"], session["user_id"]))
    
    conversazione = cursor.fetchone()
    
    if not conversazione:
        cursor.close()
        conn.close()
        flash("Conversazione non trovata", "error")
        return redirect(url_for("chat_lista"))
    
    conversazione_dict = dict(conversazione)
    
    cursor.execute("""
        SELECT a.*, 
               CASE WHEN a.id_utente = ? THEN 'venditore' ELSE 'acquirente' END as mio_ruolo
        FROM annuncio a
        WHERE a.id_annuncio = ?
    """, (session["user_id"], conversazione_dict['id_annuncio']))
    annuncio = cursor.fetchone()
    
    if not annuncio:
        annuncio = {'id_annuncio': 0, 'titolo': 'Annuncio', 'prezzo': 0, 'mio_ruolo': ''}
    else:
        annuncio = dict(annuncio)
    
    altro_utente_id = conversazione_dict['id_venditore'] if conversazione_dict['id_acquirente'] == session["user_id"] else conversazione_dict['id_acquirente']
    cursor.execute("SELECT id_utente, username FROM utente WHERE id_utente = ?", (altro_utente_id,))
    altro_utente = cursor.fetchone()
    
    if not altro_utente:
        altro_utente = {'id_utente': 0, 'username': 'Utente'}
    else:
        altro_utente = dict(altro_utente)
    
    cursor.execute("""
        UPDATE messaggio SET letto = 1 
        WHERE id_conversazione = ? AND id_destinatario = ? AND letto = 0
    """, (id_conversazione, session["user_id"]))
    conn.commit()
    
    cursor.execute("""
        SELECT m.*, u.username as mittente_nome, u.foto_profilo
        FROM messaggio m
        JOIN utente u ON m.id_mittente = u.id_utente
        WHERE m.id_conversazione = ?
        ORDER BY m.data_invio ASC
    """, (id_conversazione,))
    messaggi = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template("chat_dettaglio.html", 
                         conversazione=conversazione_dict, 
                         annuncio=annuncio,
                         messaggi=messaggi,
                         altro_utente=altro_utente)

@app.route("/api/chat/invia", methods=["POST"])
def chat_invia_messaggio():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Non autenticato"})
    
    data = request.get_json()
    id_conversazione = data.get('id_conversazione')
    messaggio = data.get('messaggio', '').strip()
    
    if not messaggio:
        return jsonify({"success": False, "error": "Messaggio vuoto"})
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM conversazione 
        WHERE id_conversazione = ? AND (id_acquirente = ? OR id_venditore = ?)
    """, (id_conversazione, session["user_id"], session["user_id"]))
    
    conv = cursor.fetchone()
    if not conv:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Conversazione non trovata"})
    
    conv_dict = dict(conv)
    id_destinatario = conv_dict['id_venditore'] if conv_dict['id_acquirente'] == session["user_id"] else conv_dict['id_acquirente']
    
    cursor.execute("""
        INSERT INTO messaggio (id_conversazione, id_mittente, id_destinatario, id_annuncio, contenuto, data_invio, letto)
        VALUES (?, ?, ?, ?, ?, datetime('now'), 0)
    """, (id_conversazione, session["user_id"], id_destinatario, conv_dict['id_annuncio'], messaggio))
    
    cursor.execute("""
        UPDATE conversazione 
        SET ultimo_messaggio = ?, ultimo_aggiornamento = datetime('now')
        WHERE id_conversazione = ?
    """, (messaggio[:100], id_conversazione))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    socketio.emit('new_chat_message', {
        'conversazione_id': id_conversazione,
        'user_id': session["user_id"],
        'username': session["username"],
        'message': messaggio,
        'time': time_str
    }, room=f"chat_{id_conversazione}")
    
    return jsonify({"success": True, "messaggio": messaggio})

@app.route("/api/chat/nuova/<int:id_annuncio>")
def chat_nuova_conversazione(id_annuncio):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Non autenticato"})
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_utente, titolo FROM annuncio WHERE id_annuncio = ?", (id_annuncio,))
    annuncio = cursor.fetchone()
    
    if not annuncio:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Annuncio non trovato"})
    
    annuncio_dict = dict(annuncio)
    if annuncio_dict['id_utente'] == session["user_id"]:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Non puoi chattare con te stesso"})
    
    cursor.execute("""
        SELECT id_conversazione FROM conversazione 
        WHERE id_annuncio = ? AND ((id_acquirente = ? AND id_venditore = ?) OR (id_acquirente = ? AND id_venditore = ?))
    """, (id_annuncio, session["user_id"], annuncio_dict['id_utente'], annuncio_dict['id_utente'], session["user_id"]))
    
    conv = cursor.fetchone()
    
    if conv:
        id_conversazione = conv['id_conversazione']
    else:
        cursor.execute("""
            INSERT INTO conversazione (id_annuncio, id_acquirente, id_venditore, ultimo_aggiornamento)
            VALUES (?, ?, ?, datetime('now'))
        """, (id_annuncio, session["user_id"], annuncio_dict['id_utente']))
        id_conversazione = cursor.lastrowid
        conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({"success": True, "id_conversazione": id_conversazione})

@app.route("/api/chat/non-letti")
def api_chat_non_letti():
    if "user_id" not in session:
        return jsonify({"non_letti": 0})
    
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM messaggio m
        JOIN conversazione c ON m.id_conversazione = c.id_conversazione
        WHERE m.id_destinatario = ? AND m.letto = 0
    """, (session["user_id"],))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return jsonify({"non_letti": result[0] if result else 0})

# Altre route (preferiti, dashboard, miei-annunci, etc.)
@app.route("/preferiti/aggiungi/<int:id_annuncio>")
def aggiungi_preferito(id_annuncio):
    if "user_id" not in session:
        flash("Devi effettuare il login", "warning")
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_utente, titolo FROM annuncio WHERE id_annuncio = ? AND stato = 'attivo'", (id_annuncio,))
    annuncio = cursor.fetchone()
    
    if not annuncio:
        flash("Annuncio non trovato", "error")
        cursor.close()
        conn.close()
        return redirect(url_for("home"))
    
    if annuncio[0] == session["user_id"]:
        flash("❌ Non puoi aggiungere ai preferiti i tuoi annunci!", "warning")
        cursor.close()
        conn.close()
        return redirect(request.referrer or url_for("home"))
    
    try:
        cursor.execute("INSERT INTO preferiti (id_utente, id_annuncio, data_aggiunta) VALUES (?, ?, ?)", 
                      (session["user_id"], id_annuncio, date.today()))
        conn.commit()
        flash(f"✅ Annuncio aggiunto ai preferiti!", "success")
    except:
        flash("ℹ️ Annuncio già nei preferiti", "info")
    
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for("home"))

@app.route("/preferiti/rimuovi/<int:id_annuncio>")
def rimuovi_preferito(id_annuncio):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM preferiti WHERE id_utente = ? AND id_annuncio = ?", (session["user_id"], id_annuncio))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for("home"))

@app.route("/miei-preferiti")
def miei_preferiti():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT annuncio.*, veicolo.modello, veicolo.anno, marca.nome_marca, 
               preferiti.data_aggiunta, utente.username as venditore
        FROM preferiti
        JOIN annuncio ON preferiti.id_annuncio = annuncio.id_annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        JOIN utente ON annuncio.id_utente = utente.id_utente
        WHERE preferiti.id_utente = ? AND annuncio.stato = 'attivo' AND annuncio.id_utente != ?
        ORDER BY preferiti.data_aggiunta DESC
    """, (session["user_id"], session["user_id"]))
    
    preferiti = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("miei_preferiti.html", preferiti=preferiti)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT annuncio.*, veicolo.modello, veicolo.anno, marca.nome_marca
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.id_utente = ?
        ORDER BY annuncio.data_pubblicazione DESC
    """, (session["user_id"],))
    miei_annunci = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT annuncio.*, preferiti.data_aggiunta
        FROM preferiti
        JOIN annuncio ON preferiti.id_annuncio = annuncio.id_annuncio
        WHERE preferiti.id_utente = ? AND annuncio.stato = 'attivo'
        ORDER BY preferiti.data_aggiunta DESC
    """, (session["user_id"],))
    miei_preferiti = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) as count FROM messaggio WHERE id_destinatario = ? AND letto = 0", (session["user_id"],))
    result = cursor.fetchone()
    messaggi_non_letti = result[0] if result else 0
    
    cursor.execute("""
        SELECT m.*, u.username as mittente_username, a.titolo as titolo_annuncio
        FROM messaggio m
        JOIN utente u ON m.id_mittente = u.id_utente
        JOIN annuncio a ON m.id_annuncio = a.id_annuncio
        WHERE m.id_destinatario = ?
        ORDER BY m.data_invio DESC
        LIMIT 5
    """, (session["user_id"],))
    messaggi_recenti = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template("dashboard.html", 
                         miei_annunci=miei_annunci,
                         miei_preferiti=miei_preferiti,
                         messaggi_non_letti=messaggi_non_letti,
                         messaggi_recenti=messaggi_recenti)

@app.route("/miei-annunci")
def miei_annunci():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT annuncio.*, veicolo.modello, veicolo.anno, marca.nome_marca
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.id_utente = ?
        ORDER BY annuncio.data_pubblicazione DESC
    """, (session["user_id"],))
    
    annunci = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template("miei_annunci.html", annunci=annunci)

@app.route("/segna-venduto/<int:id_annuncio>")
def segna_venduto(id_annuncio):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE annuncio SET stato = 'venduto' WHERE id_annuncio = ? AND id_utente = ?", (id_annuncio, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/elimina-annuncio/<int:id_annuncio>")
def elimina_annuncio(id_annuncio):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE annuncio SET stato = 'eliminato' WHERE id_annuncio = ? AND id_utente = ?", (id_annuncio, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/modifica-annuncio/<int:id_annuncio>", methods=["GET", "POST"])
def modifica_annuncio(id_annuncio):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT annuncio.*, veicolo.*, marca.nome_marca
        FROM annuncio
        JOIN veicolo ON annuncio.id_veicolo = veicolo.id_veicolo
        JOIN marca ON veicolo.id_marca = marca.id_marca
        WHERE annuncio.id_annuncio = ? AND annuncio.id_utente = ?
    """, (id_annuncio, session["user_id"]))
    
    annuncio = cursor.fetchone()
    
    if not annuncio:
        cursor.close()
        conn.close()
        return "Annuncio non trovato", 404
    
    if request.method == "POST":
        titolo = request.form["titolo"]
        descrizione = request.form["descrizione"]
        prezzo = request.form["prezzo"]
        modello = request.form["modello"]
        anno = request.form["anno"]
        chilometraggio = request.form["chilometraggio"]
        colore = request.form["colore"]
        
        cursor.execute("UPDATE annuncio SET titolo = ?, descrizione = ?, prezzo = ? WHERE id_annuncio = ?", 
                      (titolo, descrizione, prezzo, id_annuncio))
        cursor.execute("UPDATE veicolo SET modello = ?, anno = ?, chilometraggio = ?, colore = ? WHERE id_veicolo = ?",
                      (modello, anno, chilometraggio, colore, annuncio['id_veicolo']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("dashboard"))
    
    cursor.execute("SELECT * FROM marca")
    marche = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM categoria")
    categorie = [dict(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template("modifica_annuncio.html", 
                         annuncio=dict(annuncio),
                         marche=marche,
                         categorie=categorie)

@app.route("/api/notifiche")
def api_notifiche():
    if "user_id" not in session:
        return jsonify({"messaggi_non_letti": 0})
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM messaggio WHERE id_destinatario = ? AND letto = 0", (session["user_id"],))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({"messaggi_non_letti": result[0] if result else 0})

@app.route("/segna-letto/<int:id_messaggio>")
def segna_letto(id_messaggio):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE messaggio SET letto = 1 WHERE id_messaggio = ? AND id_destinatario = ?", (id_messaggio, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("chat_lista"))

@socketio.on('join_chat')
def handle_join_chat(data):
    room = f"chat_{data['conversazione_id']}"
    join_room(room)
    print(f"Utente {data['user_id']} è entrato nella stanza {room}")
    emit('user_joined', {'user_id': data['user_id']}, room=room)

@socketio.on('typing')
def handle_typing(data):
    room = f"chat_{data['conversazione_id']}"
    emit('user_typing', {
        'user_id': data['user_id'],
        'username': session.get('username', 'Utente'),
        'is_typing': data['is_typing']
    }, room=room, include_self=False)

if __name__ == "__main__":
    socketio.run(app, debug=True)
