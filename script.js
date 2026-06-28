// Obtener el formulario
const formProducto = document.getElementById("formProducto");

// Obtener los campos del formulario
const nombre = document.getElementById("nombre");
const descripcion = document.getElementById("descripcion");
const categoria = document.getElementById("categoria");

// Variable para contar los productos registrados
let total = 0;

// Crear un mensaje para avisos
const mensaje = document.createElement("p");
mensaje.className = "mt-3";

// Crear el texto del total
const contador = document.createElement("p");
contador.textContent = "Total de productos registrados: 0";

// Crear el contenedor donde aparecerán los productos
const listaProductos = document.createElement("div");
listaProductos.className = "row";

// Agregar mensaje, contador y lista debajo del formulario
formProducto.appendChild(mensaje);
formProducto.appendChild(contador);
formProducto.appendChild(listaProductos);

// Evento para registrar producto
formProducto.addEventListener("submit", function(event) {

    // Evitar que la página se recargue
    event.preventDefault();

    // Validar campos vacíos
    if (nombre.value.trim() === "" || descripcion.value.trim() === "" || categoria.value === "") {
        mensaje.textContent = "Complete todos los campos.";
        mensaje.className = "alert alert-danger mt-3";
        return;
    }

    // Crear columna Bootstrap
    const columna = document.createElement("div");
    columna.className = "col-md-4";

    // Crear tarjeta Bootstrap
    const tarjeta = document.createElement("div");
    tarjeta.className = "card m-3 shadow";

    // Crear cuerpo de la tarjeta
    const cuerpo = document.createElement("div");
    cuerpo.className = "card-body";

    // Crear título del producto
    const titulo = document.createElement("h5");
    titulo.className = "card-title";
    titulo.textContent = nombre.value;

    // Crear descripción del producto
    const texto = document.createElement("p");
    texto.className = "card-text";
    texto.textContent = descripcion.value;

    // Crear categoría
    const tipo = document.createElement("p");
    tipo.innerHTML = "<strong>Categoría:</strong> " + categoria.value;

    // Crear botón eliminar
    const botonEliminar = document.createElement("button");
    botonEliminar.textContent = "Eliminar";
    botonEliminar.className = "btn btn-danger";

    // Evento para eliminar producto
    botonEliminar.addEventListener("click", function() {
        listaProductos.removeChild(columna);
        total--;
        contador.textContent = "Total de productos registrados: " + total;
    });

    // Agregar elementos a la tarjeta
    cuerpo.appendChild(titulo);
    cuerpo.appendChild(texto);
    cuerpo.appendChild(tipo);
    cuerpo.appendChild(botonEliminar);

    tarjeta.appendChild(cuerpo);
    columna.appendChild(tarjeta);
    listaProductos.appendChild(columna);

    // Actualizar contador
    total++;
    contador.textContent = "Total de productos registrados: " + total;

    // Mostrar mensaje de éxito
    mensaje.textContent = "Producto registrado correctamente.";
    mensaje.className = "alert alert-success mt-3";

    // Limpiar formulario
    formProducto.reset();
});