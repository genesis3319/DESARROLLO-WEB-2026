# Importar FlaskForm para crear formularios con Flask-WTF
from flask_wtf import FlaskForm

# Campos que utilizaremos en el formulario
from wtforms import IntegerField, DateField, DecimalField, SubmitField, SelectField

# Validadores para comprobar los datos ingresados
from wtforms.validators import DataRequired, NumberRange


class FacturacionForm(FlaskForm):

    # Cliente registrado en la base de datos
    # lista desplegable con los clientes disponibles
    id_cliente = SelectField(
        'Cliente',
        coerce=int,
        validators=[
        DataRequired(message='Seleccione un cliente.')
        ]
    )

    # Fecha de la factura
    fecha = DateField(
        'Fecha',
        validators=[
            DataRequired(message='La fecha es obligatoria.')
        ]
    )

    # Producto que se incluirá en la factura
    id_producto = SelectField(
        'Producto',
        coerce=int,
        validators=[
            DataRequired(message='Seleccione un producto.')
        ]
    )

    # Cantidad del producto vendido
    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message='La cantidad es obligatoria.'),
            NumberRange(
                min=1,
                message='La cantidad debe ser mayor que 0.'
            )
        ]
    )

    # Valor total de la factura
    total = DecimalField(
        'Total',
        validators=[
            DataRequired(message='El total es obligatorio.'),
            NumberRange(
                min=0.01,
                message='El total debe ser mayor que 0.'
            )
        ]
    )

    # Botón para guardar la factura
    submit = SubmitField('Guardar factura')