# =====================================================================
#  TP02 - Programacion I
#  Controlador de misiones
#
#  ESTE ES EL ARCHIVO DONDE ESCRIBIS TU PROGRAMA.
#
#  Antes de ejecutarlo:
#    1. Abri INICIAR_SIMULADOR (elegi G1 o Go2)
#    2. Espera a que aparezca la ventana con el robot
#    3. Recien ahi ejecuta este archivo
#
#  Nombre y apellido:  .....................................
#  Comision:           .....................................
# =====================================================================

import sys

from robot import ErrorDeSeguridad, Robot

from misiones import MISIONES

# Cuantos datos lleva cada comando ademas de su nombre.
DATOS_POR_COMANDO = {
    "avanzar": 2,
    "girar": 2,
    "detenerse": 0,
    "saludar": 0,
}

# Prefijo que usa ejecutar_comando cuando el robot rechaza la orden.
PREFIJO_RECHAZO = "RECHAZADO POR EL ROBOT: "


# =====================================================================
#  PARTE 1 - Validar un comando
# =====================================================================
def comando_es_valido(comando):
    """Decide si un comando se puede ejecutar. Devuelve True o False.

    Un comando es una tupla. El primer elemento dice que hacer:

        ("avanzar", velocidad, tiempo)    velocidad en m/s, tiempo en s
        ("girar", velocidad, tiempo)      velocidad en rad/s, tiempo en s
        ("detenerse",)
        ("saludar",)

    Cosas que conviene revisar:
      - que la tupla no este vacia
      - que el nombre del comando sea uno de los cuatro validos
      - que tenga la cantidad de datos que corresponde
        (avanzar y girar llevan dos; detenerse y saludar, ninguno)
      - que velocidad y tiempo sean numeros de verdad, no textos
      - que el tiempo no sea negativo
    """
    return motivo_invalido(comando) is None


def es_numero(valor):
    """True si el valor es un int o un float (un bool no cuenta como numero)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def motivo_invalido(comando):
    """Devuelve por que el comando no es valido, o None si esta bien."""
    if not isinstance(comando, tuple) or len(comando) == 0:
        return "el comando esta vacio o no es una tupla"

    nombre = comando[0]
    if nombre not in DATOS_POR_COMANDO:
        return f"'{nombre}' no es un comando conocido"

    esperados = DATOS_POR_COMANDO[nombre]
    datos = comando[1:]
    if len(datos) != esperados:
        return f"'{nombre}' lleva {esperados} datos y recibio {len(datos)}"

    if esperados == 2:
        velocidad, tiempo = datos
        if not es_numero(velocidad):
            return f"la velocidad {velocidad!r} no es un numero"
        if not es_numero(tiempo):
            return f"el tiempo {tiempo!r} no es un numero"
        if tiempo < 0:
            return f"el tiempo no puede ser negativo ({tiempo} s)"

    return None


# =====================================================================
#  PARTE 2 - Ejecutar un comando
# =====================================================================
def ejecutar_comando(robot, comando):
    """Ejecuta UN comando en el robot. Devuelve un texto con lo que paso.

    Ordenes que podes usar:

        robot.avanzar(velocidad=..., tiempo=...)
        robot.girar(velocidad=..., tiempo=...)
        robot.detenerse()
        robot.saludar()

    Ojo: aunque el comando parezca valido, el robot puede rechazarlo
    igual (por ejemplo, si la velocidad supera el limite de la materia).
    Eso llega como un ErrorDeSeguridad y conviene atraparlo.
    """
    nombre = comando[0]
    try:
        if nombre == "avanzar":
            velocidad, tiempo = comando[1:]
            robot.avanzar(velocidad=velocidad, tiempo=tiempo)
            return f"avanzo {velocidad * tiempo:.2f} m ({velocidad} m/s durante {tiempo} s)"
        if nombre == "girar":
            velocidad, tiempo = comando[1:]
            sentido = "izquierda" if velocidad >= 0 else "derecha"
            texto = f"giro {abs(velocidad * tiempo):.2f} rad hacia la {sentido}"
            robot.girar(velocidad=velocidad, tiempo=tiempo)
            return texto
        if nombre == "detenerse":
            robot.detenerse()
            return "se detuvo"
        robot.saludar()
        return "saludo"
    except ErrorDeSeguridad as error:
        robot.detenerse()
        return PREFIJO_RECHAZO + str(error)


# =====================================================================
#  PARTE 3 - Recorrer la mision entera
# =====================================================================
def ejecutar_mision(robot, mision, historial):
    """Recorre la lista de comandos, uno por uno.

    Por cada comando:
      - si NO es valido, lo rechaza y sigue con el siguiente
      - si es valido, lo ejecuta
      - en los dos casos, guarda en 'historial' que fue lo que paso

    Un comando invalido NO tiene que cortar la mision.
    """
    for numero, comando in enumerate(mision, start=1):
        motivo = motivo_invalido(comando)
        if motivo is not None:
            estado, detalle = "rechazado", f"comando invalido: {motivo}"
        else:
            resultado = ejecutar_comando(robot, comando)
            if resultado.startswith(PREFIJO_RECHAZO):
                estado, detalle = "rechazado", resultado[len(PREFIJO_RECHAZO):]
            else:
                estado, detalle = "ejecutado", resultado

        historial.append({"numero": numero, "comando": comando,
                          "estado": estado, "detalle": detalle})
        marca = "OK " if estado == "ejecutado" else "XX "
        print(f"  {marca} #{numero} {comando}: {detalle}")


# =====================================================================
#  PARTE 4 - El reporte final
# =====================================================================
def generar_reporte(historial):
    """Muestra por pantalla un resumen de la mision.

    Tiene que decir, como minimo:
      - cuantos comandos se ejecutaron bien
      - cuantos se rechazaron
      - cual fue el motivo de cada rechazo
    """
    ejecutados = [paso for paso in historial if paso["estado"] == "ejecutado"]
    rechazados = [paso for paso in historial if paso["estado"] == "rechazado"]

    print()
    print("=" * 60)
    print("  REPORTE DE LA MISION")
    print("=" * 60)
    print(f"  Comandos totales:    {len(historial)}")
    print(f"  Ejecutados bien:     {len(ejecutados)}")
    print(f"  Rechazados:          {len(rechazados)}")

    if rechazados:
        print()
        print("  Motivo de cada rechazo:")
        for paso in rechazados:
            print(f"    #{paso['numero']} {paso['comando']}")
            print(f"        -> {paso['detalle']}")
    print("=" * 60)


# =====================================================================
#  PROGRAMA PRINCIPAL
# =====================================================================
def elegir_misiones():
    """Pregunta que mision correr. Devuelve una lista de nombres."""
    if len(sys.argv) > 1:
        eleccion = sys.argv[1].lower()
    else:
        print("Misiones disponibles:", ", ".join(MISIONES), "o todas")
        eleccion = input("Cual queres correr? [todas]: ").strip().lower() or "todas"

    if eleccion == "todas":
        return list(MISIONES)
    if eleccion not in MISIONES:
        print(f"No existe la mision '{eleccion}'. Corro todas.")
        return list(MISIONES)
    return [eleccion]


def main():
    nombres = elegir_misiones()

    robot = Robot()
    robot.conectar()

    try:
        for nombre in nombres:
            historial = []
            print()
            print(f">>> MISION {nombre.upper()}")
            ejecutar_mision(robot, MISIONES[nombre], historial)
            generar_reporte(historial)
    finally:
        robot.detenerse()
        robot.desconectar()


if __name__ == "__main__":
    main()
