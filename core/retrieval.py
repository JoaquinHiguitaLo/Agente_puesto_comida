
"""Recuperación documental básica para Picanteo."""

import re
import unicodedata
from pathlib import Path


DOCUMENTO = (
    Path(__file__).resolve().parents[1]
    / "knowledge"
    / "guia_operativa.md"
)

PALABRAS_COMUNES = {
    "el", "la", "los", "las", "un", "una",
    "de", "del", "en", "con", "por", "para",
    "que", "como", "cual", "cuales",
    "puedo", "debo", "es", "son", "y",
    "a", "al", "mi", "mis", "su",
}


def normalizar(texto: str) -> list[str]:
    """Convierte texto en palabras normalizadas."""

    texto = unicodedata.normalize(
        "NFKD",
        texto.lower(),
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    palabras = re.findall(r"[a-z0-9]+", texto)

    return [
        palabra
        for palabra in palabras
        if palabra not in PALABRAS_COMUNES
        and len(palabra) > 2
    ]


def cargar_documentos() -> list[dict]:
    """Carga la guía y la divide por encabezados de sección."""

    contenido = DOCUMENTO.read_text(encoding="utf-8")

    secciones = re.split(
        r"(?=^## \d+\.)",
        contenido,
        flags=re.MULTILINE,
    )

    documentos = []

    for seccion in secciones:
        seccion = seccion.strip()

        if not seccion.startswith("## "):
            continue

        titulo = seccion.splitlines()[0].replace("## ", "")

        documentos.append({
            "fuente": DOCUMENTO.name,
            "titulo": titulo,
            "contenido": seccion,
        })

    return documentos


def recuperar_documentos(
    pregunta: str,
    limite: int = 2,
) -> list[dict]:
    """Recupera secciones usando coincidencia textual."""

    if limite < 1:
        return []

    consulta = set(normalizar(pregunta))

    if not consulta:
        return []

    resultados = []

    for documento in cargar_documentos():

        palabras_titulo = set(
            normalizar(documento["titulo"])
        )

        palabras_contenido = set(
            normalizar(documento["contenido"])
        )

        coincidencias_titulo = consulta.intersection(
            palabras_titulo
        )

        coincidencias_contenido = consulta.intersection(
            palabras_contenido
        )

        # Las palabras del título tienen mayor relevancia.
        puntuacion = (
            len(coincidencias_titulo) * 3
            + len(coincidencias_contenido)
        )


        if puntuacion > 0:
            resultados.append({
                **documento,
                "puntuacion": puntuacion,
            })

    resultados.sort(
        key=lambda documento: documento["puntuacion"],
        reverse=True,
    )

    return resultados[:limite]
