CREATE DATABASE IF NOT EXISTS arte_mostacilla;

USE arte_mostacilla;

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    id_proveedor INT,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- ==========================================
-- TABLA DE USUARIOS PARA AUTENTICACIÓN
-- ==========================================

-- Almacena los usuarios registrados en el sistema
CREATE TABLE IF NOT EXISTS usuarios (

    id_usuario INT AUTO_INCREMENT PRIMARY KEY,

    -- Nombre del usuario
    nombre VARCHAR(100) NOT NULL,

    -- Correo utilizado para iniciar sesión
    correo VARCHAR(100) NOT NULL UNIQUE,

    -- Contraseña almacenada de forma segura mediante hash
    password VARCHAR(255) NOT NULL

);

-- Consulta relacionada entre productos y proveedores
SELECT 
    productos.nombre AS producto,
    proveedores.nombre AS proveedor
FROM productos
INNER JOIN proveedores
ON productos.id_proveedor = proveedores.id_proveedor;