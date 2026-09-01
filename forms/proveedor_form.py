from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ProveedorForm(FlaskForm):
    nombre = StringField(
        'Nombre del proveedor',
        validators=[
            DataRequired(message='El nombre del proveedor es obligatorio.'),
            Length(min=3, max=60, message='El nombre debe tener entre 3 y 60 caracteres.')
        ]
    )

    producto = StringField(
        'Producto suministrado',
        validators=[
            DataRequired(message='El producto suministrado es obligatorio.'),
            Length(min=3, max=100, message='El producto debe tener entre 3 y 100 caracteres.')
        ]
    )

    ciudad = StringField(
        'Ciudad',
        validators=[
            DataRequired(message='La ciudad es obligatoria.'),
            Length(min=3, max=50, message='La ciudad debe tener entre 3 y 50 caracteres.')
        ]
    )

    submit = SubmitField('Guardar proveedor')