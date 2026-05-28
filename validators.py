def validar_registro(data):
    """Valida los datos principales del registro del negocio.

    Esta función puede adaptarse según el giro del proyecto:
    productos, servicios, citas, reparaciones, pedidos, etc.
    """
    errores = []
    if not data:
        errores.append("No se recibieron datos.")
        return errores

    if not data.get("nombre"):
        errores.append("El nombre es obligatorio.")

    if not data.get("categoria"):
        errores.append("La categoría es obligatoria.")

    if not data.get("descripcion"):
        errores.append("La descripción es obligatoria.")

    try:
        precio = float(data.get("precio", 0))
        if precio <= 0:
            errores.append("El precio debe ser mayor que 0.")
    except ValueError:
        errores.append("El precio debe ser un número válido.")

    return errores


def validar_login(data):
    errores = []

    if not data:
        errores.append("No se recibieron datos.")
        return errores

    if not data.get("correo"):
        errores.append("El correo es obligatorio.")

    if not data.get("password"):
        errores.append("La contraseña es obligatoria.")

    return errores


def validar_contacto(data):
    errores = []

    if not data:
        errores.append("No se recibieron datos.")
        return errores

    if not data.get("nombre"):
        errores.append("El nombre es obligatorio.")

    if not data.get("correo"):
        errores.append("El correo es obligatorio.")

    if not data.get("mensaje"):
        errores.append("El mensaje es obligatorio.")

    return errores
