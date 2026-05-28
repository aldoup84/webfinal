CREATE DATABASE IF NOT EXISTS mcc_2026;
USE mcc_2026;

CREATE TABLE IF NOT EXISTS registros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10,2) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    destacado BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO registros (nombre, categoria, descripcion, precio, activo, destacado)
VALUES
('Servicio de mantenimiento', 'Servicios', 'Revisión general del equipo o servicio.', 500.00, TRUE, FALSE),
('Producto básico', 'Productos', 'Producto de ejemplo para el negocio.', 150.00, TRUE, FALSE),
('Cita de diagnóstico', 'Citas', 'Agenda inicial para revisar una solicitud.', 0.00, TRUE, FALSE);
