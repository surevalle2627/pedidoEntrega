from flask import Flask, render_template, request, redirect, url_for, session, flash

from functools import wraps

import json

import folium # <--- AÑADIDO DE LA VERSIÓN ANTERIOR



app = Flask(__name__)



app.secret_key = 'tu_clave_secreta_muy_segura'



# --- DICCIONARIO DE USUARIOS ACTUALIZADO ---

# Se ha quitado el rol 'usuario'. Solo quedan admin, editor y driver.

users = {

    'admin': {'password': '12345', 'role': 'admin'},

    'editor': {'password': '1234', 'role': 'editor'},

    'driver': {'password': 'driverpass', 'role': 'driver'}

}





# --- DECORADORES DE TU NUEVA VERSIÓN ---



def login_required(f):

    """

    Decorador para asegurarse de que el usuario haya iniciado sesión.

    """

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if 'username' not in session:

            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')

            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function



def role_required(role):

    """

    Decorador para restringir el acceso a una página según un rol específico.

    """

    def decorator(f):

        @wraps(f)

        def decorated_function(*args, **kwargs):



            if 'username' not in session:

                flash('Debes iniciar sesión para ver esta página.', 'warning')

                return redirect(url_for('login'))

            if session.get('role') != role:

                flash('No tienes los permisos necesarios para acceder a esta página.', 'danger')

                return redirect(url_for('dashboard')) # Lo redirigimos al dashboard principal

            return f(*args, **kwargs)

        return decorated_function

    return decorator





# --- RUTAS PRINCIPALES DE TU NUEVA VERSIÓN ---



@app.route('/')

def home():

    # Asumimos que tienes un 'home.html'. Si no, crea uno o redirige a 'login'

    return render_template('home.html')



@app.route('/login', methods=['GET', 'POST'])

def login():

    if 'username' in session:

        return redirect(url_for('dashboard'))



    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']



        user_data = users.get(username)



        if user_data and user_data['password'] == password:

            session['username'] = username

            session['role'] = user_data['role']

            flash(f'¡Bienvenido de nuevo, {username}!', 'success')

            return redirect(url_for('dashboard'))

        else:

            flash('Usuario o contraseña incorrectos.', 'danger')



    return render_template('login.html')



@app.route('/logout')

def logout():

    session.clear()

    flash('Has cerrado sesión exitosamente.', 'info')

    return redirect(url_for('login'))



@app.route('/dashboard')

@login_required

def dashboard():

    return render_template('dashboard.html')



# --- RUTAS DE ROL DE TU NUEVA VERSIÓN ---



@app.route('/admin')

@login_required

@role_required('admin')

def admin_panel():

    # return render_template('admin_panel.html') # Asegúrate de tener esta plantilla

    flash('Acceso al panel de Admin (requiere plantilla admin_panel.html)', 'info')

    return redirect(url_for('dashboard'))





@app.route('/editor')

@login_required

@role_required('editor')

def editor_page():

    # return render_template('editor_page.html') # Asegúrate de tener esta plantilla

    flash('Acceso a la página de Editor (requiere plantilla editor_page.html)', 'info')

    return redirect(url_for('dashboard'))





# --- RUTAS DE MAPA Y PEDIDO AÑADIDAS (FUSIONADAS) ---



@app.route('/ver_mapa')

@login_required

@role_required('driver') # <--- PROTEGIDO CON TU NUEVO DECORADOR

def ver_mapa():

    # Crear el mapa centrado en Cochabamba

    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)



    # Lista de tiendas con sus datos

    tiendas = [

        {

            'nombre': 'Doña Filomena',

            'contacto': 'Filomena Delgado',

            'direccion': 'Calle La Tablada #4533',

            'telefono': '7778899',

            'foto': 'tienda_barrio.jpg',

            'ubicacion': [-17.3935, -66.1570]

        },

        {

            'nombre': 'Abarrotes El Carmen',

            'contacto': 'Carmen Rojas',

            'direccion': 'Av. Blanco Galindo Km 2',

            'telefono': '76543210',

            'foto': 'tienda_carmen.jpg',

            'ubicacion': [-17.3850, -66.1700]

        },

        # ... (otras tiendas)

        {

            'nombre': 'Tienda Doña Rosa',

            'contacto': 'Rosa Mendez',

            'direccion': 'Calle Hamiroya #432',

            'telefono': '79876543',

            'foto': 'tienda_rosa.jpg',

            'ubicacion': [-17.4010, -66.1520]

        }

    ]



    pedido_url = url_for('pedido')



    # Agregar marcadores para cada tienda

    for tienda in tiendas:

        # Usar la foto de la tienda actual

        foto_url = url_for('static', filename='fotos/' + tienda['foto'])



        popup_content = f"""<table class='table table-success table-striped'>

            <tr><td colspan='2'><img src='{foto_url}' width='250' height='200'></td></tr>

            <tr><td><b>Nombre</b></td><td>{tienda['nombre']}</td></tr>

            <tr><td><b>Contacto</b></td><td>{tienda['contacto']}</td></tr>

            <tr><td><b>Direccion</b></td><td>{tienda['direccion']}</td></tr>

            <tr><td><b>Teléfono</b></td><td>{tienda['telefono']}</td></tr>

            <tr><td colspan='2'><center>

                <a class='btn btn-primary' href='{pedido_url}' style='color: white;'>Ver Pedido</a>

            </center></td></tr>

        </table>"""



        folium.Marker(

            location=tienda['ubicacion'],

            popup=folium.Popup(popup_content, max_width=300),

            tooltip=tienda['nombre'],

            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')

        ).add_to(m)



    mapa_html = m._repr_html_()



    # Renderizar la plantilla HTML

    return render_template('mapa.html', mapa=mapa_html)





@app.route('/pedido', methods=['GET', 'POST'])

@login_required

@role_required('driver') # <--- PROTEGIDO CON TU NUEVO DECORADOR

def pedido():

    if request.method == 'POST':

        # Aquí iría la lógica para procesar los datos del formulario

        flash('Pedido entregado exitosamente!', 'success')

        return redirect(url_for('dashboard'))



    # Si es GET, solo mostrar la página

    return render_template('pedido.html')





# --- EJECUCIÓN DE LA APP ---



if __name__ == '__main__':

    app.run(debug=True)