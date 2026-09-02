from flask import Flask, render_template, flash, redirect, url_for
import sqlite3

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)

# Clave secreta para la protección CSRF
app.config['SECRET_KEY'] = 'arte-mostacilla-clave-secreta-2026'

# Ruta de la base de datos SQLite
DATABASE = 'data/ferreteria.db'

# Función para crear la base de datos y la tabla productos
def inicializar_bd():
    conexion = sqlite3.connect(DATABASE)
    cursor = conexion.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()

# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')


# Ruta de productos
@app.route('/productos', methods=['GET', 'POST'])
def productos():

    titulo = "Nuestros productos artesanales"

    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute('''
        SELECT id, nombre, descripcion, categoria, precio, stock
        FROM productos
    ''')

    productos = cursor.fetchall()

    conexion.close()

    return render_template(
        'productos.html',
        titulo=titulo,
        productos=productos
    )

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():

    form = ProductoForm()

    if form.validate_on_submit():

        conexion = sqlite3.connect(DATABASE)
        cursor = conexion.cursor()

        cursor.execute(
            '''
            INSERT INTO productos (nombre, descripcion, categoria, precio, stock)
            VALUES (?, ?, ?, ?, ?)
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
        conexion.close()

        flash('Producto registrado correctamente.', 'success')
        return redirect(url_for('nuevo_producto'))

    return render_template(
        'formulario_producto.html',
        form=form
    )

# Ruta de clientes
@app.route('/clientes')
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

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
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

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
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
    inicializar_bd()
    app.run(debug=True)