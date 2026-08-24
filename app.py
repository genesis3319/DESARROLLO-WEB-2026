from flask import Flask, render_template

app = Flask(__name__)


# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')


# Ruta de productos
@app.route('/productos')
def productos():
    return render_template('productos.html')


# Ruta de clientes
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')


# Ruta de proveedores
@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html')


# Ruta de facturación
@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html')


if __name__ == '__main__':
    app.run(debug=True)