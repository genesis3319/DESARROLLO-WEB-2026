from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre del producto',
        validators=[
            DataRequired(message='El nombre del producto es obligatorio.'),
            Length(min=3, max=50, message='El nombre debe tener entre 3 y 50 caracteres.')
        ]
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es obligatoria.'),
            Length(min=5, max=200, message='La descripción debe tener entre 5 y 200 caracteres.')
        ]
    )

    categoria = StringField(
        'Categoría',
        validators=[
            DataRequired(message='La categoría es obligatoria.')
        ]
    )

    precio = DecimalField(
        'Precio',
        validators=[
            InputRequired(message='El precio es obligatorio.'),
            NumberRange(min=0.01, message='El precio debe ser mayor que 0.')
        ]
    )

    stock = IntegerField(
        'Stock',
        validators=[
            InputRequired(message='El stock es obligatorio.'),
            NumberRange(min=0, message='El stock no puede ser negativo.')
        ]
    )

    submit = SubmitField('Guardar producto')