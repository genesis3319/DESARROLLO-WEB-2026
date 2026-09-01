from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class FacturacionForm(FlaskForm):
    numero = StringField(
        'Número de factura',
        validators=[
            DataRequired(message='El número de factura es obligatorio.'),
            Length(min=3, max=10, message='El número debe tener entre 3 y 10 caracteres.')
        ]
    )

    cliente = StringField(
        'Cliente',
        validators=[
            DataRequired(message='El cliente es obligatorio.'),
            Length(min=3, max=60, message='El nombre del cliente debe tener entre 3 y 60 caracteres.')
        ]
    )

    producto = StringField(
        'Producto',
        validators=[
            DataRequired(message='El producto es obligatorio.'),
            Length(min=3, max=100, message='El producto debe tener entre 3 y 100 caracteres.')
        ]
    )

    total = DecimalField(
        'Total',
        validators=[
            DataRequired(message='El total es obligatorio.'),
            NumberRange(min=0.01, message='El total debe ser mayor que 0.')
        ]
    )

    submit = SubmitField('Guardar factura')