from flask import Flask, render_template

app = Flask(__name__)


# Ruta principal
@app.route('/')
def inicio():
    return render_template('index.html')


# Ruta de productos
@app.route('/productos')
def productos():

    titulo = "Nuestros productos artesanales"

    productos = [
        {
            "nombre": "Pulsera artesanal",
            "descripcion": "Pulsera elaborada con mostacillas de diferentes colores.",
            "categoria": "Pulsera",
            "precio": 5.00,
            "stock": 8,
            "imagen": "PULCERA.jpeg"
        },
        {
            "nombre": "Collar artesanal",
            "descripcion": "Collar elaborado a mano para diferentes ocasiones.",
            "categoria": "Collar",
            "precio": 15.00,
            "stock": 4,
            "imagen": "COLLAR 2.jpeg"
        },
        {
            "nombre": "Aretes artesanales",
            "descripcion": "Aretes creativos elaborados con mostacillas.",
            "categoria": "Aretes",
            "precio": 8.00,
            "stock": 0,
            "imagen": "ARETES.jpeg"
        }
    ]

    return render_template(
        'productos.html',
        titulo=titulo,
        productos=productos
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

if __name__ == '__main__':
    app.run(debug=True)