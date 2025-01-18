from flask import jsonify, render_template, request, redirect, url_for, session
from sqlalchemy import desc
from . import db
from .models import *
from app.utils.debugging import printn
import json
import pprint

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
        '''
        devuelve un diccionario con clave 'dia de la semana' y valor de una lista de diccionarios.

        la lista de diccionarios tiene como primera clave: 'dato' y valor boolean. Y como segunda
        clave: 'id' y valor 'el id del dato'.

        Ejemplo:

        {
            'dom': [
                {'dato': False, 'id': 1},
                {'dato': True, 'id': 2},
                {'dato': False, 'id': 3},
                {'dato': False, 'id': 4},
                {'dato': False, 'id': 5},
                {'dato': False, 'id': 6},
                {'dato': False, 'id': 7}
                ],
                ...
        }

        '''
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

        # printn(datos)
        # printn(json.dumps(datos, indent=4, ensure_ascii=False))
        pprint.pprint(datos)

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
