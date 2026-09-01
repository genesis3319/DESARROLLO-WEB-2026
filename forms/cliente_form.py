from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ClienteForm(FlaskForm):
    nombre = StringField(
        'Nombre del cliente',
        validators=[
            DataRequired(message='El nombre del cliente es obligatorio.'),
            Length(min=3, max=60, message='El nombre debe tener entre 3 y 60 caracteres.')
        ]
    )

    telefono = StringField(
        'Teléfono',
        validators=[
            DataRequired(message='El teléfono es obligatorio.'),
            Length(min=10, max=10, message='El teléfono debe tener 10 dígitos.')
        ]
    )

    ciudad = StringField(
        'Ciudad',
        validators=[
            DataRequired(message='La ciudad es obligatoria.'),
            Length(min=3, max=50, message='La ciudad debe tener entre 3 y 50 caracteres.')
        ]
    )

    submit = SubmitField('Guardar cliente')