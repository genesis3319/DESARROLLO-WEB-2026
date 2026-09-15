from flask import Flask, render_template, flash, redirect, url_for
from conexion.conexion import obtener_conexion

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)

# Clave secreta para la protección CSRF
app.config['SECRET_KEY'] = 'arte-mostacilla-clave-secreta-2026'

# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')


# Ruta de productos
@app.route('/productos')
def productos():

    titulo = "Nuestros productos artesanales"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

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

@app.route('/productos/nuevo', methods=['GET', 'POST'])
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
def editar_producto(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

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

@app.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
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
    app.run(debug=True)