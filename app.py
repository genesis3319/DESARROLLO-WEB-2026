import os

# Permite obtener los resultados de PostgreSQL como diccionarios
from psycopg2.extras import RealDictCursor

from flask import Flask, render_template, flash, redirect, url_for
from conexion.conexion import obtener_conexion

# Protección CSRF para los formularios
from flask_wtf.csrf import CSRFProtect

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

# Activar la protección CSRF en toda la aplicación
csrf = CSRFProtect(app)

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

    # Consultar los productos junto con su proveedor.
    # LEFT JOIN permite mostrar también productos que todavía no tienen proveedor.
    cursor.execute('''
        SELECT
            p.id_producto AS id,
            p.nombre,
            p.descripcion,
            p.categoria,
            p.precio,
            p.stock,
            pr.nombre AS proveedor
        FROM productos p
        LEFT JOIN proveedores pr
            ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id_producto
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

    # Conectar con PostgreSQL para obtener los proveedores registrados
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Consultar el ID y el nombre de los proveedores
    cursor.execute(
        '''
        SELECT id_proveedor, nombre
        FROM proveedores
        ORDER BY nombre
        '''
    )

    proveedores = cursor.fetchall()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Cargar los proveedores en la lista desplegable
    form.proveedor.choices = [
        (proveedor[0], proveedor[1])
        for proveedor in proveedores
    ]

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Guardar el producto junto con el proveedor seleccionado
        cursor.execute(
            '''
            INSERT INTO productos
            (nombre, descripcion, categoria, precio, stock, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (
                form.nombre.data,
                form.descripcion.data,
                form.categoria.data,
                float(form.precio.data),
                form.stock.data,
                form.proveedor.data
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

    # Obtener los datos del producto, incluyendo su proveedor
    cursor.execute(
        '''
        SELECT id_producto, nombre, descripcion, categoria, precio, stock, id_proveedor
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

    # Consultar los proveedores registrados en PostgreSQL
    cursor.execute(
        '''
        SELECT id_proveedor, nombre
        FROM proveedores
        ORDER BY nombre
        '''
    )

    # Obtener todos los proveedores
    proveedores = cursor.fetchall()

    # Cargar los proveedores en la lista desplegable
    form.proveedor.choices = [
        (proveedor['id_proveedor'], proveedor['nombre'])
        for proveedor in proveedores
    ]

    if form.validate_on_submit():

        # Actualizar el producto y su proveedor en PostgreSQL
        cursor.execute(
            '''
            UPDATE productos
            SET nombre = %s,
                descripcion = %s,
                categoria = %s,
                precio = %s,
                stock = %s,
                id_proveedor = %s
            WHERE id_producto = %s
            ''',
            (
                form.nombre.data,
                form.descripcion.data,
                form.categoria.data,
                float(form.precio.data),
                form.stock.data,
                form.proveedor.data,
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

        # Mostrar el proveedor actual del producto en la lista desplegable
        form.proveedor.data = producto['id_proveedor']

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

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Consultar los clientes almacenados en PostgreSQL
    cursor.execute(
    '''
    SELECT
        id_cliente,
        nombre,
        telefono,
        ciudad
    FROM clientes
    ORDER BY id_cliente
    '''
)

    # Obtener todos los clientes encontrados
    clientes = cursor.fetchall()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

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
        # Conectar con PostgreSQL
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Guardar el cliente en la base de datos
        cursor.execute(
            '''
            INSERT INTO clientes (nombre, telefono, ciudad)
            VALUES (%s, %s, %s)
            ''',
            (
                form.nombre.data,
                form.telefono.data,
                form.ciudad.data
            )
        )

        # Confirmar los cambios en PostgreSQL
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Cliente registrado correctamente.', 'success')

        # Regresar a la lista de clientes
        return redirect(url_for('clientes'))

    return render_template(
        'formulario_cliente.html',
        form=form
    )

# Ruta para editar un cliente
@app.route('/clientes/editar/<int:id_cliente>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id_cliente):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionario
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Buscar el cliente que se desea editar
    cursor.execute(
        '''
        SELECT id_cliente, nombre, telefono, ciudad
        FROM clientes
        WHERE id_cliente = %s
        ''',
        (id_cliente,)
    )

    cliente = cursor.fetchone()

    # Comprobar que el cliente exista
    if cliente is None:
        cursor.close()
        conexion.close()
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))

    # Crear el formulario
    form = ClienteForm()

    # Si se envía el formulario, actualizar los datos
    if form.validate_on_submit():

        cursor.execute(
            '''
            UPDATE clientes
            SET nombre = %s,
                telefono = %s,
                ciudad = %s
            WHERE id_cliente = %s
            ''',
            (
                form.nombre.data,
                form.telefono.data,
                form.ciudad.data,
                id_cliente
            )
        )

        # Confirmar los cambios
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Cliente actualizado correctamente.', 'success')

        # Regresar a la lista de clientes
        return redirect(url_for('clientes'))

    # Cargar los datos actuales en el formulario
    if not form.is_submitted():
        form.nombre.data = cliente['nombre']
        form.telefono.data = cliente['telefono']
        form.ciudad.data = cliente['ciudad']

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar el formulario con los datos del cliente
    return render_template(
        'formulario_cliente.html',
        form=form
    )

# Ruta para eliminar un cliente
@app.route('/clientes/eliminar/<int:id_cliente>', methods=['POST'])
@login_required
def eliminar_cliente(id_cliente):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Eliminar el cliente mediante su ID
    cursor.execute(
        '''
        DELETE FROM clientes
        WHERE id_cliente = %s
        ''',
        (id_cliente,)
    )

    # Confirmar los cambios en PostgreSQL
    conexion.commit()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar mensaje de confirmación
    flash('Cliente eliminado correctamente.', 'success')

    # Regresar a la lista de clientes
    return redirect(url_for('clientes'))

# Ruta de proveedores
@app.route('/proveedores')
@login_required
def proveedores():

    # Título que se mostrará en la página
    titulo = "Nuestros proveedores"

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Consultar los proveedores almacenados en PostgreSQL
    cursor.execute(
        '''
        SELECT
            id_proveedor,
            nombre,
            producto,
            ciudad
        FROM proveedores
        ORDER BY id_proveedor
        '''
    )

    # Obtener todos los proveedores encontrados
    proveedores = cursor.fetchall()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Enviar los proveedores reales a la plantilla
    return render_template(
        'proveedores.html',
        titulo=titulo,
        proveedores=proveedores
    )

# Ruta para registrar un nuevo proveedor
@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proveedor():

    # Crear el formulario para registrar proveedores
    form = ProveedorForm()

    # Validar los datos enviados por el formulario
    if form.validate_on_submit():

        # Conectar con PostgreSQL
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Guardar el proveedor en la base de datos
        cursor.execute(
            '''
            INSERT INTO proveedores (nombre, producto, ciudad)
            VALUES (%s, %s, %s)
            ''',
            (
                form.nombre.data,
                form.producto.data,
                form.ciudad.data
            )
        )

        # Confirmar los cambios en PostgreSQL
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Proveedor registrado correctamente.', 'success')

        # Regresar a la lista de proveedores
        return redirect(url_for('proveedores'))

    # Mostrar el formulario
    return render_template(
        'formulario_proveedor.html',
        form=form
    )

# Ruta para editar un proveedor
@app.route('/proveedores/editar/<int:id_proveedor>', methods=['GET', 'POST'])
@login_required
def editar_proveedor(id_proveedor):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Buscar el proveedor que se desea editar
    cursor.execute(
        '''
        SELECT
            id_proveedor,
            nombre,
            producto,
            ciudad
        FROM proveedores
        WHERE id_proveedor = %s
        ''',
        (id_proveedor,)
    )

    # Obtener el proveedor encontrado
    proveedor = cursor.fetchone()

    # Si el proveedor no existe, regresar a la lista
    if not proveedor:
        cursor.close()
        conexion.close()

        flash('Proveedor no encontrado.', 'danger')
        return redirect(url_for('proveedores'))

    # Crear el formulario
    form = ProveedorForm()

    # Si el formulario fue enviado y los datos son válidos
    if form.validate_on_submit():

        # Actualizar los datos del proveedor en PostgreSQL
        cursor.execute(
            '''
            UPDATE proveedores
            SET nombre = %s,
                producto = %s,
                ciudad = %s
            WHERE id_proveedor = %s
            ''',
            (
                form.nombre.data,
                form.producto.data,
                form.ciudad.data,
                id_proveedor
            )
        )

        # Confirmar los cambios
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Proveedor actualizado correctamente.', 'success')

        # Regresar a la lista de proveedores
        return redirect(url_for('proveedores'))

    # Cargar los datos actuales del proveedor en el formulario
    if not form.is_submitted():
        form.nombre.data = proveedor['nombre']
        form.producto.data = proveedor['producto']
        form.ciudad.data = proveedor['ciudad']

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar el formulario con los datos actuales
    return render_template(
        'formulario_proveedor.html',
        form=form
    )
# Ruta para eliminar un proveedor
@app.route('/proveedores/eliminar/<int:id_proveedor>', methods=['POST'])
@login_required
def eliminar_proveedor(id_proveedor):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Quitar la relación del proveedor con los productos
    # Los productos se conservan y solamente quedan sin proveedor asignado
    cursor.execute(
       '''
       UPDATE productos
       SET id_proveedor = NULL
       WHERE id_proveedor = %s
       ''',
       (id_proveedor,)
    )

    # Eliminar el proveedor mediante su ID
    cursor.execute(
        '''
        DELETE FROM proveedores
        WHERE id_proveedor = %s
        ''',
        (id_proveedor,)
    )

    # Confirmar los cambios en PostgreSQL
    conexion.commit()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar mensaje de confirmación
    flash('Proveedor eliminado correctamente.', 'success')

    # Regresar a la lista de proveedores
    return redirect(url_for('proveedores'))

# ==========================================
# RUTA PARA MOSTRAR LA FACTURACIÓN
# ==========================================

@app.route('/facturacion')
@login_required
def facturacion():

    # Título que se mostrará en la página
    titulo = "Registro de facturación"

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Consultar las facturas junto con el cliente,
    # el producto y la cantidad vendida
    cursor.execute(
        '''
        SELECT
            f.id_factura,
            c.nombre AS cliente,
            p.nombre AS producto,
            d.cantidad,
            f.fecha,
            f.total
        FROM facturas f

        -- Relacionar la factura con el cliente
        INNER JOIN clientes c
            ON f.id_cliente = c.id_cliente

        -- Relacionar la factura con su detalle
        LEFT JOIN detalle_factura d
            ON f.id_factura = d.id_factura

        -- Relacionar el detalle con el producto
        LEFT JOIN productos p
            ON d.id_producto = p.id_producto

        ORDER BY f.id_factura
        '''
    )

    # Obtener todas las facturas encontradas
    facturas = cursor.fetchall()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Enviar las facturas a la página HTML
    return render_template(
        'facturacion.html',
        titulo=titulo,
        facturas=facturas
    )

# Ruta para registrar una nueva factura
@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():

    # Crear el formulario para registrar una factura
    form = FacturacionForm()

    # Conectar con PostgreSQL para obtener los productos registrados
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Consultar los productos disponibles
    cursor.execute(
        '''
        SELECT id_producto, nombre
        FROM productos
        ORDER BY nombre
        '''
    )

    # Obtener todos los productos
    productos = cursor.fetchall()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Cargar los productos en la lista desplegable del formulario
    form.id_producto.choices = [
         (producto[0], producto[1])
         for producto in productos
    ]

    # Validar los datos enviados por el formulario
    if form.validate_on_submit():

        # Conectar con PostgreSQL
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Guardar la factura en PostgreSQL
        # RETURNING permite obtener el ID de la factura recién creada
        cursor.execute(
            '''
            INSERT INTO facturas (id_cliente, fecha, total)
            VALUES (%s, %s, %s)
            RETURNING id_factura
            ''',
            (
               form.id_cliente.data,
               form.fecha.data,
               form.total.data
            )
        )

        # Obtener el ID de la nueva factura
        id_factura = cursor.fetchone()[0]

        # Consultar el precio actual del producto seleccionado
        cursor.execute(
            '''
            SELECT precio
            FROM productos
            WHERE id_producto = %s
            ''',
            (form.id_producto.data,)
        )

        producto = cursor.fetchone()

        # Guardar el producto y la cantidad en el detalle de la factura
        cursor.execute(
            '''
            INSERT INTO detalle_factura
                (id_factura, id_producto, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
            ''',
            (
               id_factura,
               form.id_producto.data,
               form.cantidad.data,
               producto[0]
            )
        )

        # Confirmar los cambios en PostgreSQL
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Factura registrada correctamente.', 'success')

        # Regresar a la lista de facturas
        return redirect(url_for('facturacion'))

    # Mostrar el formulario
    return render_template(
        'formulario_facturacion.html',
        form=form
    )

# ==========================================
# RUTA PARA EDITAR UNA FACTURA
# ==========================================

@app.route('/facturacion/editar/<int:id_factura>', methods=['GET', 'POST'])
@login_required
def editar_factura(id_factura):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()

    # Obtener los resultados como diccionarios
    cursor = conexion.cursor(cursor_factory=RealDictCursor)

    # Buscar la factura y su detalle relacionado
    cursor.execute(
        '''
        SELECT
            f.id_factura,
            f.id_cliente,
            f.fecha,
            f.total,
            d.id_producto,
            d.cantidad
        FROM facturas f
        LEFT JOIN detalle_factura d
            ON f.id_factura = d.id_factura
        WHERE f.id_factura = %s
        ''',
        (id_factura,)
    )

    # Obtener la factura encontrada
    factura = cursor.fetchone()

    # Si la factura no existe, regresar a la lista
    if not factura:
        cursor.close()
        conexion.close()

        flash('La factura no existe.', 'danger')
        return redirect(url_for('facturacion'))

    # Crear el formulario
    form = FacturacionForm()

    # Consultar los productos registrados
    cursor.execute(
        '''
        SELECT id_producto, nombre
        FROM productos
        ORDER BY nombre
        '''
    )

    productos = cursor.fetchall()

    # Cargar los productos en la lista desplegable
    form.id_producto.choices = [
        (producto['id_producto'], producto['nombre'])
        for producto in productos
    ]

    # Procesar la actualización
    if form.validate_on_submit():

        # Actualizar los datos principales de la factura
        cursor.execute(
            '''
            UPDATE facturas
            SET id_cliente = %s,
                fecha = %s,
                total = %s
            WHERE id_factura = %s
            ''',
            (
                form.id_cliente.data,
                form.fecha.data,
                form.total.data,
                id_factura
            )
        )

        # Consultar el precio actual del producto seleccionado
        cursor.execute(
            '''
            SELECT precio
            FROM productos
            WHERE id_producto = %s
            ''',
            (form.id_producto.data,)
        )

        producto = cursor.fetchone()

        # Comprobar si la factura ya tiene un detalle
        cursor.execute(
            '''
            SELECT id_detalle
            FROM detalle_factura
            WHERE id_factura = %s
            ''',
            (id_factura,)
        )

        detalle = cursor.fetchone()

        if detalle:

            # Si ya existe el detalle, actualizarlo
            cursor.execute(
                '''
                UPDATE detalle_factura
                SET id_producto = %s,
                    cantidad = %s,
                    precio_unitario = %s
                WHERE id_factura = %s
                ''',
                (
                    form.id_producto.data,
                    form.cantidad.data,
                    producto['precio'],
                    id_factura
                )
            )

        else:

            # Si la factura antigua no tiene detalle, crearlo
            cursor.execute(
                '''
                INSERT INTO detalle_factura
                    (id_factura, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
                ''',
                (
                    id_factura,
                    form.id_producto.data,
                    form.cantidad.data,
                    producto['precio']
                )
            )

        # Confirmar todos los cambios
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

        # Mostrar mensaje de confirmación
        flash('Factura actualizada correctamente.', 'success')

        # Regresar a la lista de facturas
        return redirect(url_for('facturacion'))

    # Cargar los datos actuales en el formulario
    if not form.is_submitted():

        form.id_cliente.data = factura['id_cliente']
        form.fecha.data = factura['fecha']
        form.total.data = factura['total']

        # Cargar producto y cantidad si ya existe el detalle
        if factura['id_producto'] is not None:
            form.id_producto.data = factura['id_producto']
            form.cantidad.data = factura['cantidad']

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar el formulario
    return render_template(
        'formulario_facturacion.html',
        form=form
    )

# ==========================================
# RUTA PARA ELIMINAR UNA FACTURA
# ==========================================

@app.route('/facturacion/eliminar/<int:id_factura>', methods=['POST'])
@login_required
def eliminar_factura(id_factura):

    # Conectar con PostgreSQL
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Primero eliminar los detalles relacionados con la factura
    # Esto evita problemas con la clave foránea
    cursor.execute(
        '''
        DELETE FROM detalle_factura
        WHERE id_factura = %s
        ''',
        (id_factura,)
    )

    # Después eliminar la factura
    cursor.execute(
        '''
        DELETE FROM facturas
        WHERE id_factura = %s
        ''',
        (id_factura,)
    )

    # Confirmar los cambios en PostgreSQL
    conexion.commit()

    # Cerrar cursor y conexión
    cursor.close()
    conexion.close()

    # Mostrar mensaje de confirmación
    flash('Factura eliminada correctamente.', 'success')

    # Regresar a la lista de facturas
    return redirect(url_for('facturacion'))

if __name__ == '__main__':
    app.run(debug=True)