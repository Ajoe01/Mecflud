# app.py
import os, time, json, re
from datetime import datetime
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from utils.auth import User, db, bcrypt, login_manager
from utils.models import Attempt
from utils.exercises_data import exercises# app.py (encima de las rutas o donde tengas otros @app.route)
from flask import send_from_directory
from utils.models import Attempt, ForumPost



# ---------- DB PATH ABSOLUTO ----------
BASEDIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASEDIR, "database.db")

# ---------- APP / CONFIG ----------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.png',
        mimetype='image/png'
    )

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

# ---------- Cache-buster para CSS/JS ----------
def _asset_ver(path):
    try: return int(os.path.getmtime(path))
    except: return int(time.time())

@app.context_processor
def inject_asset_versions():
    return {
        "css_v": _asset_ver(os.path.join(BASEDIR, "static", "style.css")),
        "js_v":  _asset_ver(os.path.join(BASEDIR, "static", "scripts.js")),
    }

# ---------- Flags de navegación ----------
@app.context_processor
def inject_nav_flags():
    # lock_Q: 1 = ocultar opción "preguntas"; 0 = mostrar
    try:
        # Preferir el flag en la sesión (se setea en /submit)
        lock_Q = int(session.get('lock_Q', 0) or 0)
    except Exception:
        lock_Q = 0

    # Si no hay flag en sesión, intentar leer atributo del usuario autenticado
    if lock_Q == 0 and current_user.is_authenticated:
        try:
            lock_Q = int(getattr(current_user, "lock_Q", 0) or 0)
        except Exception:
            lock_Q = 0

    # Determinar si el usuario ya tiene un intento guardado
    has_attempt = False
    try:
        if current_user.is_authenticated:
            has_attempt = Attempt.query.filter_by(user_id=current_user.id).first() is not None
    except Exception:
        has_attempt = False

    return dict(lock_Q=lock_Q, has_attempt=has_attempt)


    

# ---------- Helpers ----------
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
def sanitize_username(s: str) -> str:
    return (s or "").strip()

def build_leaderboard(order="score"):
    """Tabla global ordenada por correctas DESC, luego total DESC y fecha ASC."""
    q = db.session.query(Attempt, User).join(User, User.id == Attempt.user_id)
    if order == "score":
        q = q.order_by(Attempt.score.desc(), Attempt.total.desc(), Attempt.created_at.asc())
    else:
        q = q.order_by(Attempt.created_at.desc())
    tabla = []
    for a, u in q.all():
        tabla.append({
            "username": (u.username if u else f"User {a.user_id}"),
            "score": int(a.score or 0),
            "total": int(a.total or 0),
            "fecha": a.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return tabla


@app.after_request
def ensure_utf8(response):
    # Asegura que las respuestas HTML incluyan charset=utf-8
    try:
        ctype = response.headers.get('Content-Type', '')
        if 'text/html' in ctype and 'charset' not in ctype:
            response.headers['Content-Type'] = ctype + '; charset=utf-8'
    except Exception:
        pass
    return response

# ------------------- RUTAS -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/foro", methods=["GET", "POST"])
@login_required
def foro():
    if request.method == "POST":
        contenido = (request.form.get("mensaje") or "").strip()
        if contenido:
            db.session.add(ForumPost(user_id=current_user.id, contenido=contenido))
            db.session.commit()
            flash("Comentario publicado correctamente.")
        return redirect(url_for("foro"))

    # Gracias a lazy="joined" en la relación, ya viene el usuario asociado
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
    return render_template("foro.html", posts=posts)


@app.route('/recursos')
def recursos():
    return render_template('resources.html')



@app.route('/nosotros')
def nosotros():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = sanitize_username(request.form.get('username', ''))
            password_raw = request.form.get('password', '')
            if not USERNAME_RE.match(username):
                flash('Usuario inválido (3–30: letras/números/._-).', 'warning')
                return redirect(url_for('register'))
            if len(password_raw) < 4:
                flash('Contraseña muy corta (mín. 4).', 'warning')
                return redirect(url_for('register'))
            if User.query.filter_by(username=username).first():
                flash('Ese usuario ya está registrado.', 'warning')
                return redirect(url_for('register'))
            password = bcrypt.generate_password_hash(password_raw).decode('utf-8')
            nuevo = User(username=username, password=password)
            db.session.add(nuevo)
            db.session.commit()
            flash('Registro exitoso. Inicia sesión.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback(); flash('Usuario ya existe.', 'warning')
        except (OperationalError, SQLAlchemyError):
            db.session.rollback(); flash('Error de base de datos.', 'danger')
        except Exception:
            db.session.rollback(); flash('Error inesperado.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = sanitize_username(request.form.get('username', ''))
            password = request.form.get('password', '')
            try:
                usuario = User.query.filter_by(username=username).first()
            except OperationalError:
                # Migración opcional si existía esquema viejo
                try:
                    from utils.db_utils import ensure_schema
                    ensure_schema(db)
                except Exception:
                    pass
                usuario = User.query.filter_by(username=username).first()
            if usuario and bcrypt.check_password_hash(usuario.password, password):
                login_user(usuario)
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('exercises_page'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        except Exception:
            flash('Error al iniciar sesión.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Sesión cerrada.', 'info')
    except Exception:
        flash('Se cerró la sesión con advertencias.', 'warning')
    # Limpiar flag de preguntas en la sesión al cerrar sesión
    try:
        session.pop('lock_Q', None)
    except Exception:
        pass
    return redirect(url_for('login'))

@app.route('/exercises')
@login_required
def exercises_page():
    # Si la sesión indica que ya envió respuestas, redirige inmediatamente
    if session.get('lock_Q', 0) == 1:
        return redirect(url_for('results'))

    ya = Attempt.query.filter_by(user_id=current_user.id).first()
    if ya:
        return redirect(url_for('results'))
    return render_template('exercises.html', exercises=exercises)


@app.route('/submit', methods=['POST'])
@login_required
def submit_all():
    try:
        # Evitar doble envío si ya existe intento (o si luego activas lock_Q)
        if Attempt.query.filter_by(user_id=current_user.id).first():
            return redirect(url_for('results'))

        respuestas_usuario, detalle = {}, []
        correctas = 0
        faltantes = []

        for ex in exercises:
            name = f"q-{ex['id']}"  # <- CON GUION
            sel = request.form.get(name)
            if not sel:
                faltantes.append(ex['id'])
                continue
            ok = (sel == ex['correcta'])
            if ok: correctas += 1
            respuestas_usuario[str(ex['id'])] = sel
            detalle.append({
                "id": ex['id'],
                "titulo": ex['titulo'],
                "seleccion": sel,
                "correcta": ex['correcta'],
                "ok": ok,
                "exp": ex.get("exp", "")
            })

        if faltantes:
            nums = ", ".join(map(str, faltantes))
            flash("Pregunta(s) sin responder.", "danger")
            flash(f"Tienes {len(faltantes)} pregunta(s) sin responder: {nums}.", 'danger')
            return redirect(url_for('exercises_page'))

        intento = Attempt(
            user_id=current_user.id,
            answers_json=json.dumps(respuestas_usuario, ensure_ascii=False),
            score=correctas,
            total=len(exercises)
        )
        db.session.add(intento)
        db.session.commit()

        tabla = build_leaderboard(order="score")
        flash("Cuestionario enviado correctamente.", "success")

        # Marcar en la sesión que el usuario ya envió las respuestas para ocultar el enlace
        session['lock_Q'] = 1

        # Redirigir a /results (la vista `results` mostrará el intento guardado)
        return redirect(url_for('results'))
    except Exception:
        db.session.rollback()
        flash('No se pudo guardar el envío. Intenta de nuevo.', 'danger')
        return redirect(url_for('exercises_page'))


@app.route("/resultsb")
def resultsb():
    try:
        tabla = build_leaderboard(order="score")
        return render_template("resultsb.html", tabla=tabla)
    except Exception as e:
        flash("No se pudieron cargar los resultados globales.", "danger")
        print("Error en /resultsb:", e)
        return redirect(url_for("index"))



@app.route('/results')
@login_required
def results():
    try:
        intento = Attempt.query.filter_by(user_id=current_user.id)\
                               .order_by(Attempt.created_at.desc()).first()
        tabla = build_leaderboard(order="score")

        if intento:
            respuestas = json.loads(intento.answers_json or "{}")
            detalle = []
            for ex in exercises:
                sel = respuestas.get(str(ex['id']))
                detalle.append({
                    "id": ex['id'],
                    "titulo": ex['titulo'],
                    "seleccion": sel,
                    "correcta": ex['correcta'],
                    "ok": (sel == ex['correcta']),
                    "exp": ex.get("exp","")
                })
            return render_template('results.html',
                                   detalle=detalle,
                                   puntaje=intento.score,
                                   total=intento.total,
                                   tabla=tabla,
                                   local=True)

        # Sin intento propio: solo global
        return render_template('results.html',
                               detalle=[],
                               puntaje=0,
                               total=len(exercises),
                               tabla=tabla,
                               local=False)
    except Exception:
        flash('No se pudieron cargar los resultados.', 'danger')
        return redirect(url_for('results'))


@app.route('/api/nav_flags')
@login_required
def api_nav_flags():
    """Endpoint pequeño que devuelve flags de navegación usados por JS.
    Devuelve lock_Q (0/1) y has_attempt (bool) para que el cliente oculte enlaces.
    """
    try:
        lock_Q = int(session.get('lock_Q', 0) or 0)
    except Exception:
        lock_Q = 0

    has_attempt = False
    try:
        if current_user.is_authenticated:
            has_attempt = Attempt.query.filter_by(user_id=current_user.id).first() is not None
    except Exception:
        has_attempt = False

    return jsonify({'lock_Q': lock_Q, 'has_attempt': bool(has_attempt)})

# ------------------- ARRANQUE -------------------
if __name__ == '__main__':
    with app.app_context():
        try:
            # Migración opcional si tenías esquema anterior
            from utils.db_utils import ensure_schema
            ensure_schema(db)
        except Exception:
            pass
        db.create_all()
    app.run(debug=True,  port=5100)
