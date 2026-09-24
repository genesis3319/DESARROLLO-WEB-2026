import os

# Permite obtener los resultados de PostgreSQL como diccionarios
from psycopg2.extras import RealDictCursor

from flask import Flask, render_template, flash, redirect, url_for
from conexion.conexion import obtener_conexion

# Formularios utilizados en el proyecto
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

# Formularios para el registro e inicio de sesión
from forms.usuario_form import UsuarioForm
from forms.login_form import LoginForm

# Funciones para proteger y verificar las contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

# Funciones para manejar las sesiones de los usuarios
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

# Clave secreta obtenida desde una variable de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# ==========================================
# CONFIGURACIÓN DE FLASK-LOGIN
# ==========================================

# Crear el administrador de inicio de sesión
login_manager = LoginManager()

# Vincular Flask-Login con nuestra aplicación
login_manager.init_app(app)

# Indicar a qué página enviar al usuario si necesita iniciar sesión
login_manager.login_view = 'login'

# Mensaje que aparecerá cuando se intente acceder sin iniciar sesión
login_manager.login_message = 'Debe iniciar sesión para acceder a esta página.'

# Tipo de alerta de Bootstrap para el mensaje
login_manager.login_message_category = 'warning'

# ==========================================
# MODELO DE USUARIO PARA FLASK-LOGIN
# ==========================================

# Clase que representa al usuario que inicia sesión
class Usuario(UserMixin):

    # Recibir los datos del usuario desde PostgreSQL
    def __init__(self, id_usuario, nombre, correo):
        self.id = id_usuario
        self.nombre = nombre
        self.correo = correo

# ==========================================
# CARGAR USUARIO DESDE POSTGRESQL
# ==========================================

# Flask-Login utiliza esta función para recuperar
# al usuario que tiene una sesión iniciada
@login_manager.user_loader
def cargar_usuario(user_id):

    # Conectar con la base de datos PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Buscar al usuario mediante su ID
    cursor.execute(
        '''
        SELECT id_usuario, nombre, correo
        FROM usuarios
        WHERE id_usuario = %s
        ''',
        (user_id,)
    )

    usuario = cursor.fetchone()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Si el usuario existe, crear un objeto Usuario
    if usuario:
        return Usuario(
            usuario['id_usuario'],
            usuario['nombre'],
            usuario['correo']
        )

    # Si el usuario no existe, Flask-Login recibe None
    return None

# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')

# ==========================================
# REGISTRO E INICIO DE SESIÓN DE USUARIOS
# ==========================================
# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['GET', 'POST'])
def registro():

    # Crear el formulario de registro
    form = UsuarioForm()

    # Verificar que el formulario sea válido
    if form.validate_on_submit():

        # Conectar con la base de datos PostgreSQL
        conexion = obtener_conexion()

        # Obtener los resultados como diccionarios
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        # Verificar si el correo ya está registrado
        cursor.execute(
            'SELECT id_usuario FROM usuarios WHERE correo = %s',
            (form.correo.data,)
        )

        usuario_existente = cursor.fetchone()

        # Si el correo ya existe, mostrar un mensaje
        if usuario_existente:
            cursor.close()
            conexion.close()

            flash('El correo ya está registrado.', 'danger')

            return render_template(
                'registro.html',
                form=form
            )

        # Proteger la contraseña antes de guardarla
        password_hash = generate_password_hash(form.password.data)

        # Guardar el nuevo usuario en PostgreSQL
        cursor.execute(
            '''
            INSERT INTO usuarios (nombre, correo, password)
            VALUES (%s, %s, %s)
            ''',
            (
                form.nombre.data,
                form.correo.data,
                password_hash
            )
        )

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de registro exitoso
        flash('Usuario registrado correctamente.', 'success')

        # Enviar al usuario a la página de inicio de sesión
        return redirect(url_for('login'))

    # Mostrar el formulario de registro
    return render_template(
        'registro.html',
        form=form
    )

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Crear el formulario de inicio de sesión
    form = LoginForm()

    # Verificar que el formulario sea válido
    if form.validate_on_submit():

        # Conectar con la base de datos PostgreSQL
        conexion = obtener_conexion()

        # Obtener los resultados como diccionarios
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        # Buscar al usuario mediante su correo electrónico
        cursor.execute(
            '''
            SELECT id_usuario, nombre, correo, password
            FROM usuarios
            WHERE correo = %s
            ''',
            (form.correo.data,)
        )

        usuario = cursor.fetchone()

        # Cerrar cursor y conexión después de realizar la consulta
        cursor.close()
        conexion.close()

        # Verificar que el usuario exista y que la contraseña sea correcta
        if usuario and check_password_hash(
            usuario['password'],
            form.password.data
        ):

           # Crear el objeto del usuario autenticado
           usuario_login = Usuario(
               usuario['id_usuario'],
               usuario['nombre'],
               usuario['correo']
           )

           # Iniciar y guardar la sesión del usuario con Flask-Login
           login_user(usuario_login)

           # Mostrar mensaje de inicio de sesión exitoso
           flash('Inicio de sesión exitoso.', 'success')

           # Regresar a la página principal
           return redirect(url_for('inicio'))

        # Mensaje cuando el correo o la contraseña son incorrectos
        flash('Correo o contraseña incorrectos.', 'danger')

    # Mostrar el formulario de inicio de sesión
    return render_template(
        'login.html',
        form=form
    )

# Ruta para cerrar la sesión del usuario
@app.route('/logout')
@login_required
def logout():

    # Cerrar la sesión actual con Flask-Login
    logout_user()

    # Mostrar mensaje al usuario
    flash('Sesión cerrada correctamente.', 'success')

    # Regresar a la página principal
    return redirect(url_for('inicio'))

# Ruta de productos
@app.route('/productos')
def productos():

    titulo = "Nuestros productos artesanales"

    conexion = obtener_conexion()

    # Obtener los productos como diccionarios desde PostgreSQL
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute('''
        SELECT id_producto AS id,
               nombre,
               descripcion,
               categoria,
               precio,
               stock
        FROM productos
    ''')

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'productos.html',
        titulo=titulo,
        productos=productos
    )

# Ruta para registrar un nuevo producto
@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():

    form = ProductoForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            '''
            INSERT INTO productos
            (nombre, descripcion, categoria, precio, stock)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (
                form.nombre.data,
                form.descripcion.data,
                form.categoria.data,
                float(form.precio.data),
                form.stock.data
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash('Producto registrado correctamente.', 'success')
        return redirect(url_for('productos'))

    return render_template(
        'formulario_producto.html',
        form=form
    )

@app.route('/productos/editar/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def editar_producto(id_producto):

    conexion = obtener_conexion()

    # Obtener el producto como diccionario desde PostgreSQL
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        '''
        SELECT id_producto, nombre, descripcion, categoria, precio, stock
        FROM productos
        WHERE id_producto = %s
        ''',
        (id_producto,)
    )

    producto = cursor.fetchone()

    if producto is None:
        cursor.close()
        conexion.close()
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('productos'))

    form = ProductoForm()

    if form.validate_on_submit():

        cursor.execute(
            '''
            UPDATE productos
            SET nombre = %s,
                descripcion = %s,
                categoria = %s,
                precio = %s,
                stock = %s
            WHERE id_producto = %s
            ''',
            (
                form.nombre.data,
                form.descripcion.data,
                form.categoria.data,
                float(form.precio.data),
                form.stock.data,
                id_producto
            )
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('productos'))

    if not form.is_submitted():
        form.nombre.data = producto['nombre']
        form.descripcion.data = producto['descripcion']
        form.categoria.data = producto['categoria']
        form.precio.data = producto['precio']
        form.stock.data = producto['stock']

    cursor.close()
    conexion.close()

    return render_template(
        'formulario_producto.html',
        form=form
    )

# Ruta para eliminar un producto
@app.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
@login_required
def eliminar_producto(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        '''
        DELETE FROM productos
        WHERE id_producto = %s
        ''',
        (id_producto,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('productos'))

# Ruta de clientes
@app.route('/clientes')
@login_required
def clientes():

    titulo = "Nuestros clientes"

    clientes = [
        {
            "nombre": "María López",
            "telefono": "0991234567",
            "ciudad": "Arajuno"
        },
        {
            "nombre": "Genesis Andy",
            "telefono": "0986318935",
            "ciudad": "Puyo"
        },
        {
            "nombre": "Carolina Chimbo",
            "telefono": "0974561230",
            "ciudad": "Pastaza"
        }
    ]

    return render_template(
        'clientes.html',
        titulo=titulo,
        clientes=clientes
    )

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():

    form = ClienteForm()

    if form.validate_on_submit():
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('nuevo_cliente'))

    return render_template(
        'formulario_cliente.html',
        form=form
    )

# Ruta de proveedores
@app.route('/proveedores')
@login_required
def proveedores():

    titulo = "Nuestros proveedores"

    proveedores = [
        {
            "nombre": "Manualidades Rosita",
            "producto": "Mostacillas",
            "ciudad": "Puyo"
        },
        {
            "nombre": "Accesorios Creativos",
            "producto": "Broches e hilos",
            "ciudad": "Quito"
        },
        {
            "nombre": "Mundo Artesanal",
            "producto": "Mostacillas y accesorios",
            "ciudad": "Ambato"
        }
    ]

    return render_template(
        'proveedores.html',
        titulo=titulo,
        proveedores=proveedores
    )

# Ruta para registrar un nuevo proveedor
@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():

    form = ProveedorForm()

    if form.validate_on_submit():
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('nuevo_proveedor'))

    return render_template(
        'formulario_proveedor.html',
        form=form
    )

# Ruta de facturación
@app.route('/facturacion')
@login_required
def facturacion():

    titulo = "Registro de facturación"

    facturas = [
        {
            "numero": "001",
            "cliente": "María López",
            "producto": "Pulsera artesanal",
            "total": 5.00
        },
        {
            "numero": "002",
            "cliente": "Genesis Andy",
            "producto": "Collar artesanal",
            "total": 15.00
        },
        {
            "numero": "003",
            "cliente": "Carolina Chimbo",
            "producto": "Aretes artesanales",
            "total": 5.00
        }
    ]

    return render_template(
        'facturacion.html',
        titulo=titulo,
        facturas=facturas
    )

# Ruta para registrar una nueva factura
@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():

    form = FacturacionForm()

    if form.validate_on_submit():
        flash('Factura registrada correctamente.', 'success')
        return redirect(url_for('nueva_factura'))

    return render_template(
        'formulario_facturacion.html',
        form=form
    )

if __name__ == '__main__':
    app.run(debug=True)