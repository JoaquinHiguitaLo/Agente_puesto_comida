# PICANTEO — Asistente Inteligente para la Gestión de un Puesto de Comida

**Asignatura:** Sistemas Agénticos y Orquestadores de IA
**Actividad:** P4 — Orquestación, despliegue y observabilidad
**Tecnologías:** Python, Streamlit, LangChain, LangGraph y Google Gemini

## 1. Introducción

Picanteo es un asistente inteligente desarrollado para apoyar la administración de un pequeño puesto de comida mediante consultas en lenguaje natural.

El sistema permite consultar información sobre ventas, inventario, productos, compras y proveedores, además de ofrecer orientación sobre la gestión del negocio.

La arquitectura combina cadenas de lenguaje, un agente con herramientas especializadas, recuperación documental RAG, memoria conversacional y mecanismos de observabilidad.

El asistente está orientado a la consulta, el análisis y las recomendaciones. No ejecuta compras, pagos ni modificaciones económicas de forma autónoma.

## 2. Planteamiento del problema

La administración de un pequeño negocio de comida requiere consultar información que suele encontrarse distribuida en diferentes registros.

Esta situación dificulta analizar las ventas, identificar productos con existencias bajas, consultar proveedores y organizar las compras.

Picanteo busca centralizar estas consultas mediante un asistente capaz de seleccionar las fuentes de información adecuadas y proporcionar respuestas fundamentadas.

## 3. Objetivos

### Objetivo general

Desarrollar y validar un asistente inteligente para la gestión de un pequeño puesto de comida mediante una arquitectura de orquestación que integre LangChain, LangGraph, herramientas, memoria, recuperación documental y observabilidad.

### Objetivos específicos

- Consultar información estructurada del negocio.
- Diferenciar consultas generales, documentales y de datos reales.
- Ejecutar una o varias herramientas según la necesidad.
- Mantener contexto conversacional mediante LangGraph.
- Recuperar información de una guía operativa utilizando RAG.
- Registrar duración, tokens, invocaciones y errores.
- Validar el funcionamiento mediante pruebas técnicas y funcionales.
- Desplegar la aplicación para su demostración.

## 4. Arquitectura del sistema

El proyecto utiliza LangGraph para administrar un grafo de estado con tres rutas principales.

```text
                    USUARIO
                       |
                       v
                STREAMLIT CHAT
                       |
                       v
                 ROUTER CHAIN
                       |
           +-----------+-----------+
           |           |           |
           v           v           v
         CHAIN        AGENT        RAG
           |           |           |
           v           v           v
        Gemini       Gemini     Recuperador
                       |           |
                       v           v
                     Tools       Documento
                       |           |
                       v           v
                    Datos JSON   Gemini
           |           |           |
           +-----------+-----------+
                       |
                       v
               RESPUESTA FINAL
                       |
                       v
                OBSERVABILIDAD
```

### Chain

Procesa preguntas generales y conceptuales que no necesitan consultar datos reales ni documentos específicos.

Ejemplo: ¿Qué es el margen de ganancia?

### Agent

Procesa solicitudes que requieren datos del negocio y ejecuta las herramientas autorizadas.

Ejemplo: ¿Cuántas ventas tenemos registradas?

Puede utilizar varias herramientas durante una misma consulta.

### RAG

Recupera fragmentos de `knowledge/guia_operativa.md` y utiliza Gemini para generar respuestas fundamentadas en la información documental.

Ejemplo: Según la guía operativa de Picanteo, ¿cómo prevenir desperdicios?

El recuperador utiliza coincidencias léxicas y puntuaciones de relevancia, dando mayor importancia a los títulos de las secciones. No utiliza embeddings ni una base de datos vectorial.

## 5. Componentes tecnológicos

| Tecnología | Función |
|---|---|
| Python | Lenguaje principal |
| Streamlit | Interfaz conversacional |
| LangChain | Prompts, cadenas, modelo y herramientas |
| LangGraph | Orquestación y flujo de estados |
| Google Gemini | Modelo de lenguaje |
| Pydantic | Clasificación estructurada de consultas |
| MemorySaver | Checkpoints conversacionales en memoria |
| JSON | Almacenamiento de datos del negocio |
| Markdown | Base documental de RAG |

## 6. Herramientas disponibles

El agente dispone de seis herramientas:

| Herramienta | Responsabilidad |
|---|---|
| `consultar_ventas` | Consultar transacciones y calcular totales registrados |
| `consultar_inventario` | Consultar existencias y niveles de stock |
| `consultar_productos` | Consultar el catálogo de productos |
| `consultar_compras` | Consultar registros de compras |
| `consultar_proveedores` | Consultar información de proveedores |
| `obtener_fecha` | Obtener información de la fecha actual |

Los datos estructurados se almacenan en `data/`.

Los cálculos numéricos de ventas se realizan mediante Python para reducir errores de interpretación del modelo.

## 7. Recuperación documental RAG

La base de conocimiento se encuentra en:

`knowledge/guia_operativa.md`

Contiene seis secciones:

1. Control de inventario.
2. Registro y análisis de ventas.
3. Gestión de compras.
4. Gestión de proveedores.
5. Prevención de desperdicios.
6. Límites de la información documental.

El módulo `core/retrieval.py` carga el documento, lo divide en secciones y recupera fragmentos mediante coincidencias de palabras normalizadas y puntuaciones de relevancia.

El nodo `rag_node` utiliza los fragmentos recuperados como contexto para Gemini y registra los documentos utilizados.

La guía contiene recomendaciones generales elaboradas para el proyecto académico. No representa procedimientos internos oficiales confirmados del negocio.

Las cantidades y valores reales se consultan mediante las herramientas JSON.

## 8. Estado y memoria conversacional

El proyecto utiliza dos mecanismos complementarios:

**Streamlit Session State:** conserva los mensajes visibles, el contexto del negocio y la información de la última ejecución.

**LangGraph MemorySaver:** conserva checkpoints asociados a un `thread_id` para mantener la continuidad conversacional.

Al iniciar una nueva conversación se genera un identificador diferente.

La persistencia de MemorySaver es temporal, dependiente del proceso de ejecución. No constituye almacenamiento permanente después de reiniciar el servidor.

## 9. Observabilidad y métricas

Se implementó un módulo `core/observability.py` para medir el comportamiento del agente.

Las métricas incluyen:

- Duración de las ejecuciones.
- Ruta seleccionada.
- Herramientas utilizadas.
- Llamadas completadas al modelo.
- Tokens de entrada y salida reportados por Gemini.
- Errores notificados por el modelo.
- Registro de errores generales de ejecución.

Las métricas se muestran en el panel lateral de Streamlit.

El sistema utiliza callbacks de LangChain y `perf_counter()` para recopilar información durante cada consulta.

Cuando no existen metadatos de tokens, se indica que no están disponibles, en lugar de inventar valores.

## 10. Pruebas y validación P4

Se realizaron pruebas manuales, pruebas directas de herramientas, comprobaciones de sintaxis y simulaciones controladas.

| Prueba | Resultado observado |
|---|---|
| Clasificación Chain | Funcionamiento verificado |
| Clasificación Agent | Funcionamiento verificado |
| Consulta de ventas | 50 ventas y $2.315.000 COP |
| Consulta de inventario | 18 productos; Flor jamaica en stock mínimo |
| Herramientas por ejecución | Se corrigió la acumulación entre consultas |
| Duración de Chain y Agent | Medición y visualización verificadas |
| Callback de LangChain | Registra llamadas y tokens reportados |
| Registro de errores | Prueba simulada satisfactoria |
| Carga documental | Seis secciones identificadas |
| Recuperación léxica | Cuatro casos de prueba satisfactorios |
| Ruta RAG | Consulta documental ejecutada correctamente |
| Continuidad contextual de RAG | Caso de seguimiento sobre la sección 5 satisfactorio |
| Sintaxis Python | Validaciones completadas sin errores |
| Dependencias | `pip check` sin requisitos incompatibles |

Estas verificaciones corresponden a las pruebas locales realizadas durante P4. No representan una cobertura automatizada exhaustiva ni sustituyen la validación final del despliegue.

## 11. Hallazgos y acciones correctivas

### Inconsistencias en el total de ventas

**Hallazgo:** Gemini produjo diferentes importes para las mismas transacciones.

**Corrección:** Se agregó `total_vendido` a `consultar_ventas`, calculado mediante Python a partir de `valor_total`.

**Verificación:** Se comprobó el importe de $2.315.000 COP tanto directamente como mediante el agente.

### Acumulación de herramientas

**Hallazgo:** El panel mostraba herramientas utilizadas en consultas anteriores.

**Corrección:** Se reinició `herramientas_usadas` al comenzar una nueva ejecución.

**Verificación:** Consultas sucesivas de ventas, inventario y conceptos mostraron sus herramientas correspondientes.

### Actualización de observabilidad

**Hallazgo:** El panel lateral conservaba datos de ejecuciones anteriores.

**Corrección:** Se implementó un contenedor actualizable mediante `st.empty()`.

**Verificación:** La ruta, el motivo, las herramientas y la duración se actualizaron correctamente en pruebas posteriores.

### Interpretación de inventario

**Hallazgo:** Algunas expresiones sobre productos próximos a agotarse producían resultados vacíos.

**Corrección:** Se agregó normalización de texto y reconocimiento de diferentes expresiones de stock bajo.

**Verificación:** Cinco expresiones de consulta recuperaron correctamente el producto en stock mínimo.

### Recuperación contextual RAG

**Hallazgo:** Una pregunta de seguimiento identificó una sección documental incorrecta.

**Corrección:** Se incorporaron preguntas recientes al contexto de recuperación.

**Verificación:** Una prueba posterior identificó correctamente la sección 5, Prevención de desperdicios.

### Optimización del contexto

Se evaluó limitar el historial enviado al modelo, pero las pruebas mostraron respuestas de inventario incorrectas y un aumento de llamadas y tokens.

Se decidió restaurar la construcción original del contexto y priorizar la estabilidad funcional.

### Pérdida de contexto en preguntas de seguimiento RAG

**Componente:** LangGraph — Nodo RAG  
**Entorno:** Render (producción)  
**Tipo:** Error de continuidad conversacional  
**Estado:** Detectado; corrección propuesta, pendiente de validación en producción.

#### 1. Descripción del hallazgo

Durante las pruebas funcionales de la versión P4 de Picanteo se identificó una inconsistencia en el manejo de preguntas de seguimiento dentro de la ruta RAG.

El asistente respondió correctamente una consulta basada en la guía operativa, pero no logró relacionar una segunda pregunta con la información presentada anteriormente.

#### 2. Procedimiento de reproducción

**Primera consulta:**

«Según la guía operativa de Picanteo, ¿cómo podemos prevenir desperdicios?»

**Resultado obtenido:** El asistente recuperó correctamente las recomendaciones documentadas y señaló la sección 5, *Prevención de desperdicios*, de `guia_operativa.md`.

**Segunda consulta:**

«¿En qué sección de la guía se encuentra esa recomendación?»

**Resultado esperado:** Identificar la sección 5, *Prevención de desperdicios*, utilizando el contexto de la consulta anterior.

**Resultado obtenido:** El asistente solicitó una aclaración sobre cuál recomendación se estaba mencionando, a pesar de que acababa de responder sobre la prevención de desperdicios.

#### 3. Análisis de la causa

La revisión del nodo `rag_node()` identificó una posible causa relacionada con la construcción del contexto enviado al modelo.

Aunque el recuperador combinaba preguntas recientes, el mensaje enviado a Gemini incluía únicamente el último mensaje conversacional mediante:

```python
*state.get("messages", [])[-1:]
```

Esta configuración puede limitar la capacidad del modelo para interpretar referencias como «esa recomendación» o «lo anterior».

El hallazgo indica que recuperar fragmentos documentales no siempre es suficiente para resolver referencias conversacionales si el modelo no recibe el historial pertinente.

#### 4. Acción correctiva propuesta

Se propone mejorar el nodo RAG mediante dos ajustes:

1. Enviar los tres mensajes más recientes a Gemini, incluyendo la pregunta anterior, su respuesta y la nueva consulta.
2. Detectar expresiones de referencia conversacional y priorizar la pregunta anterior para recuperar los documentos correspondientes.

Las modificaciones buscan mejorar la continuidad contextual sin alterar las rutas Chain y Agent.

#### 5. Plan de verificación

Después de aplicar la corrección se deberán realizar las siguientes comprobaciones:

- Validar la sintaxis de `graph/nodes.py`.
- Repetir las dos preguntas en una conversación nueva de Streamlit.
- Confirmar que la segunda respuesta identifique la sección 5.
- Publicar la corrección en GitHub.
- Comprobar el despliegue actualizado en Render.
- Repetir las consultas en producción y registrar las métricas.

#### 6. Resultado y estado

**Estado:** Corregido y validado funcionalmente.

**Problema identificado:** El asistente no conservaba adecuadamente el contexto de determinadas preguntas de seguimiento en la ruta RAG.

**Acción correctiva:** Se ajustó el contexto conversacional enviado a Gemini y la recuperación documental para interpretar referencias a recomendaciones anteriores.

**Prueba de validación:**

- Pregunta inicial: «Según la guía operativa de Picanteo, ¿cómo podemos prevenir desperdicios?»
- Pregunta de seguimiento: «¿En qué sección de la guía se encuentra esa recomendación?»

**Resultado:** El asistente identificó correctamente la sección 5, *Prevención de desperdicios*, del documento `guia_operativa.md`.

**Conclusión:** La corrección resolvió el escenario de continuidad conversacional evaluado, mejorando la integración entre la memoria de LangGraph y la recuperación documental.

## 12. Instalación y ejecución local

### Requisitos

- Python compatible con las dependencias del proyecto.
- Acceso a internet.
- Clave API válida de Google Gemini.

### Clonar el repositorio

```bash
git clone https://github.com/JoaquinHiguitaLo/Agente_puesto_comida.git
cd Agente_puesto_comida
```

### Crear el entorno virtual en Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

### Configuración

Crear un archivo `.env` en la raíz del proyecto:

```dotenv
GEMINI_API_KEY=TU_CLAVE_API
```

La selección de modelo se administra mediante `config/settings.py` y puede configurarse usando `GEMINI_MODEL`.

No se deben publicar claves ni archivos `.env` en GitHub.

### Ejecutar

```bash
python -m streamlit run app.py
```

Abrir la dirección local indicada por Streamlit, normalmente:

`http://localhost:8501`

## 13. Despliegue

El proyecto dispone de configuración para Render mediante `render.yaml`.

El despliegue requiere configurar las variables de entorno necesarias en el servicio, instalar las dependencias y ejecutar Streamlit.

La aplicación debe verificarse después de cada despliegue, especialmente en las rutas Chain, Agent y RAG.

**URL de despliegue utilizada anteriormente:**
https://agente-puesto-comida.onrender.com

**Estado:** Pendiente de revalidación final con la versión P4.

## 14. Limitaciones

- Los datos del negocio provienen de archivos JSON y no de una base de datos transaccional en tiempo real.
- MemorySaver mantiene memoria durante la vida del proceso; no garantiza persistencia permanente.
- El recuperador RAG es léxico, por lo que puede tener limitaciones con sinónimos y preguntas ambiguas.
- La optimización de contexto fue descartada después de detectar regresiones funcionales.
- La calidad de las respuestas depende de las fuentes disponibles y de la interpretación del modelo.
- El asistente no ejecuta acciones económicas ni modifica registros mediante las herramientas actuales.

## 15. Conclusión

Picanteo integra LangChain, LangGraph, Gemini, herramientas de negocio, memoria conversacional, recuperación documental y observabilidad.

Durante P4 se implementaron mejoras técnicas, se identificaron y corrigieron problemas funcionales y se realizaron pruebas para comprobar las principales capacidades del agente.

El resultado es un asistente orientado a facilitar consultas, análisis y recomendaciones para la administración de pequeños negocios de comida, con mecanismos de trazabilidad que permiten observar su comportamiento y evaluar sus resultados.
