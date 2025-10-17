
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)

app.secret_key = 'Gardevoir2621'


users = {
    'admin': {'password': '12345', 'role': 'admin'},
    'editor': {'password': '1234', 'role': 'editor'},
    'usuario': {'password': '123', 'role': 'usuario'}
}



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



@app.route('/')
def home():
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

@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/editor')
@login_required
@role_required('editor')
def editor_page():
    return render_template('editor_page.html')


if __name__ == '__main__':
    app.run(debug=True)
