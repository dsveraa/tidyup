from flask import jsonify, render_template, request, redirect, url_for, session
from sqlalchemy import desc
from . import db
from .models import *
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from colorama import Fore, Style
from pytz import timezone, UTC
import inspect
import random
import pytz

colors = [Fore.CYAN, Fore.GREEN]
last_color = None

def printn(message):
    global last_color
    frame = inspect.currentframe()
    info = inspect.getframeinfo(frame.f_back)
    new_color = random.choice([color for color in colors if color != last_color])
    last_color = new_color
    print(f"{new_color}[{info.lineno - 1}] {message}{Style.RESET_ALL}")

def process_datetime(client_timezone, datetime_obj):
    client_tz = pytz.timezone(client_timezone)
    client_datetime_tz = client_tz.localize(datetime_obj)
    client_datetime_utc = client_datetime_tz.astimezone(pytz.utc)   
    client_datetime_local = client_datetime_utc.astimezone(client_tz)
    date_local=client_datetime_local.isoformat()
    utc_iso_format = client_datetime_utc.isoformat()
    return date_local, utc_iso_format

def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            input_user = request.form["name"]
            input_password = request.form["password"]
            db_user_obj = User.query.filter_by(name=input_user).first()
            user = db_user_obj.name
            password = db_user_obj.password
            if input_user == user and input_password == password:
                session["user_id"] = db_user_obj.id
                session["user_name"] = db_user_obj.name
                session.permanent = True
                return redirect(url_for("index"))
            else:
                return "Error en el usuario o contraseña"
        return render_template("login.html")
    
    @app.route('/cambiar_estado/<item_id>', methods=["POST"])
    def cambiar_estado(item_id):
        # printn("hola")
        item_obj = Agenda.query.filter_by(id=item_id).first()
        
        if item_obj:
            item_obj.completado = not item_obj.completado
            db.session.commit()
            return jsonify({"success": True, "new_state": item_obj.completado})
        return jsonify({"success": False, "error": "Item no encontrado"}), 404
    
    @app.route('/agenda/<responsable_id>')
    def agenda(responsable_id):
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        responsable = Agenda.query.filter_by(responsable_id=responsable_id).first()
        responsable_nombre = responsable.responsable.nombre

        agenda_obj = Agenda.query.filter_by(responsable_id=responsable_id).order_by(Agenda.id).all()

        actividades = []

        for item in agenda_obj:
            if item.actividad.nombre not in actividades:
                actividades.append(item.actividad.nombre)

        ids = [] # <--- id de cada agenda ( responsable - actividad - dia - completado )
        dias = {}
        datos = {}

        for item in agenda_obj:
            if item.id not in ids:
                ids.append(item.id)

            dia_nombre = item.dia_id
            if dia_nombre not in dias:
                dias[dia_nombre] = []
            dias[dia_nombre].append({'id': item.id, 'dato': item.completado})

        dias_nombre = {1: 'dom', 2: 'lun', 3: 'mar', 4: 'mie', 5: 'jue', 6: 'vie', 7: 'sab'}

        
        for dia_id, tareas in dias.items():
            dia_nombre = dias_nombre[dia_id]
            datos[dia_nombre] = tareas

        # printn(data)

        return render_template("agenda.html", data=datos, responsable=responsable_nombre, actividades=actividades)

    @app.route('/detalle/<actividad_id>')
    def detalle_actividad(actividad_id):
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        actividad = DetalleActividad.query.filter_by(actividad_id=actividad_id).first()
        actividad_titulo = actividad.actividad.nombre
        
        detalle_actividad_obj = DetalleActividad.query.filter_by(actividad_id=actividad_id).order_by(desc(DetalleActividad.id)).all()
        detalle_actividad = []
        
        for actividad in detalle_actividad_obj:
            detalle_actividad.append(actividad.tarea.nombre)

        return render_template("detalle_actividad.html", actividad=actividad_titulo, detalle_actividad=detalle_actividad)
    
    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        session.pop("user_name", None)
        return redirect(url_for("index"))

    @app.route('/')
    def index():
        if "user_id" not in session:
            return redirect(url_for("login"))
        return render_template("index.html")
