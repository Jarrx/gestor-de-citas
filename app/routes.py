from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Cita, Usuario
from datetime import datetime
import re
import io
from openpyxl import Workbook

main = Blueprint('main', __name__)

# Página principal con buscador
@main.route('/')
@login_required
def index():
    busqueda = request.args.get('busqueda', '').strip().lower()
    if busqueda:
        citas = Cita.query.filter(
            db.or_(
                db.func.lower(Cita.nombre).like(f'%{busqueda}%'),
                db.func.lower(Cita.apellido).like(f'%{busqueda}%')
            )
        ).order_by(Cita.fecha.asc()).all()
    else:
        citas = Cita.query.order_by(Cita.fecha.asc()).all()
    return render_template('index.html', citas=citas)

# Agregar una cita
@main.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip().title()
        apellido = request.form.get('apellido', '').strip().title()
        fecha_str = request.form.get('fecha', '').strip()
        telefono = request.form.get('telefono', '').strip()
        especialidad = request.form.get('especialidad', '').strip()

        if not nombre or not apellido or not fecha_str or not especialidad or not telefono:
            flash('Todos los campos, incluyendo el teléfono, son obligatorios.', 'error')
            return redirect(url_for('main.agregar'))

        if especialidad.lower() == 'selecciona una especialidad':
            flash('Por favor, selecciona una especialidad válida.', 'danger')
            return redirect(url_for('main.agregar'))

        try:
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
        except ValueError:
            flash('Formato de fecha inválido. Usa DD/MM/YYYY.', 'error')
            return redirect(url_for('main.agregar'))

        if not re.fullmatch(r'^\+?\d{8,15}$', telefono):
            flash('Número de teléfono inválido. Debe tener entre 8 y 15 dígitos y solo contener números (opcionalmente comienza con +).', 'danger')
            return redirect(url_for('main.agregar'))

        nueva_cita = Cita(
            nombre=nombre,
            apellido=apellido,
            fecha=fecha,
            telefono=telefono,
            especialidad=especialidad
        )

        db.session.add(nueva_cita)
        db.session.commit()
        flash('Cita agregada exitosamente.', 'success')
        return redirect(url_for('main.index'))

    return render_template('agregar.html')

# Editar una cita
@main.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cita = Cita.query.get_or_404(id)

    if request.method == 'POST':
        cita.nombre = request.form['nombre'].strip().title()
        cita.apellido = request.form['apellido'].strip().title()
        cita.fecha = datetime.strptime(request.form['fecha'], '%d/%m/%Y')
        cita.telefono = request.form.get('telefono', '').strip()
        cita.especialidad = request.form['especialidad'].strip()
        cita.estado = request.form.get('estado', 'Pendiente').strip()

        if not cita.telefono:
            flash('El teléfono es obligatorio.', 'danger')
            return redirect(url_for('main.editar', id=cita.id))

        if not re.fullmatch(r'^\+?\d{8,15}$', cita.telefono):
            flash('Número de teléfono inválido. Debe tener entre 8 y 15 dígitos y solo contener números (opcionalmente comienza con +).', 'danger')
            return redirect(url_for('main.editar', id=cita.id))

        db.session.commit()
        flash('Cita actualizada correctamente.', 'success')
        return redirect(url_for('main.index'))

    return render_template('editar.html', cita=cita)

# Eliminar una cita
@main.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    cita = Cita.query.get_or_404(id)
    db.session.delete(cita)
    db.session.commit()
    flash('Cita eliminada correctamente.', 'success')
    return redirect(url_for('main.index'))

# API pública para consultar citas
@main.route('/api/citas', methods=['GET'])
@login_required
def api_citas():
    citas = Cita.query.order_by(Cita.fecha.asc()).all()
    citas_json = [{
        'id': c.id,
        'nombre': c.nombre,
        'apellido': c.apellido,
        'telefono': c.telefono,
        'fecha': c.fecha.strftime('%d/%m/%Y'),
        'especialidad': c.especialidad,
        'estado': c.estado
    } for c in citas]
    return jsonify(citas_json)

# Exportar citas a Excel
@main.route('/exportar/excel')
@login_required
def exportar_excel():
    citas = Cita.query.order_by(Cita.fecha.asc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Citas"

    ws.append(["ID", "Nombre", "Apellido", "Teléfono", "Fecha", "Especialidad", "Estado"])

    for c in citas:
        ws.append([
            c.id,
            c.nombre,
            c.apellido,
            c.telefono or '',
            c.fecha.strftime('%d/%m/%Y'),
            c.especialidad,
            c.estado
        ])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="citas.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Registro de usuario
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_usuario = request.form["nombre_usuario"].strip()
        contraseña = request.form["contraseña"]

        if Usuario.query.filter_by(username=nombre_usuario).first():
            flash("El nombre de usuario ya existe.", "danger")
            return redirect(url_for("main.registro"))

        if (len(contraseña) < 8 or
            not re.search(r"[A-Z]", contraseña) or
            not re.search(r"[a-z]", contraseña) or
            not re.search(r"[0-9]", contraseña) or
            not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contraseña)):
            flash("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo especial.", "danger")
            return redirect(url_for("main.registro"))

        nuevo_usuario = Usuario(username=nombre_usuario)
        nuevo_usuario.set_password(contraseña)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario registrado exitosamente. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("main.login"))

    return render_template("registro.html")

# Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form["nombre_usuario"]
        contraseña = request.form["contraseña"]
        usuario = Usuario.query.filter_by(username=nombre_usuario).first()
        if usuario and usuario.check_password(contraseña):
            login_user(usuario)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("main.index"))
        flash("Credenciales inválidas", "danger")
    return render_template("login.html")

# Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("main.login"))
