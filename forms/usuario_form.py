from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UsuarioForm(FlaskForm):

    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres.')
        ]
    )

    correo = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio.'),
            Email(message='Ingrese un correo electrónico válido.')
        ]
    )

    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres.')
        ]
    )

    submit = SubmitField('Registrarse')