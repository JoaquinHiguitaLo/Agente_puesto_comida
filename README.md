**Introducción**

El presente proyecto desarrolla un asistente inteligente basado en modelos de lenguaje (LLM) para apoyar la gestión de un pequeño puesto de comida.

El sistema busca facilitar la consulta y análisis de información relacionada con las ventas, productos, inventario, compras, proveedores y fechas del negocio.
Para ello, se implementa una arquitectura agéntica que combina un Router Chain, un Response Chain, un Agent, herramientas especializadas (Tools) y un mecanismo 
de estado y memoria conversacional.

El asistente puede determinar qué tipo de procesamiento requiere cada solicitud. Las consultas generales pueden resolverse mediante una cadena de respuesta 
directa, mientras que las solicitudes que necesitan información real del negocio son dirigidas hacia un agente capaz de utilizar las herramientas disponibles.

De esta manera, el proyecto aplica el concepto de orquestación basada en cadenas, permitiendo que diferentes componentes colaboren para producir una respuesta 
según las características de cada consulta.

**Planteamiento del problema**

La administración de un pequeño puesto de comida puede involucrar diferentes tipos de información, como:

Ventas realizadas.
Productos disponibles.
Cantidades existentes en inventario.
Compras realizadas.
Proveedores.
Precios.
Costos.
Información histórica del negocio.

Cuando esta información se administra manualmente o se encuentra distribuida en diferentes registros, resulta más difícil realizar consultas rápidas, 
identificar situaciones relevantes y obtener una visión general del comportamiento del negocio.

**Usuario objetivo**

El usuario principal del sistema es:

Propietario o administrador de un pequeño puesto de comida.

El sistema está pensado para una persona que necesita consultar y analizar información de su negocio sin tener que realizar manualmente cada búsqueda sobre 
las diferentes fuentes de datos.

El usuario conserva el control sobre las decisiones importantes del negocio. El agente funciona principalmente como un sistema de consulta, análisis y 
recomendación.

**Objetivo general**

Desarrollar un asistente inteligente basado en LLM capaz de consultar y analizar información de un pequeño puesto de comida mediante una arquitectura de 
orquestación que combine cadenas, agentes, herramientas, memoria y contexto.

**Objetivos específicos**

- Consultar información de las ventas registradas.
- Consultar el inventario disponible.
- Consultar los productos registrados.
- Consultar las compras realizadas.
- Consultar los proveedores registrados.
- Obtener información relacionada con la fecha actual.
- Analizar información proveniente de una o varias herramientas.
- Diferenciar entre consultas generales y consultas que requieren datos reales del negocio.
- Mantener memoria conversacional reciente.
- Mostrar información sobre la ruta utilizada y las herramientas ejecutadas.
- Evitar generar información que no esté disponible en las fuentes consultadas.

**Información utilizada por el agente**

El agente trabaja con diferentes fuentes de información estructuradas en archivos JSON.

Fuente	Información

- ventas.json	Ventas realizadas, productos, cantidades, precios y valores totales
- inventario.json	Existencias y niveles de inventario
- productos.json	Productos registrados en el negocio
- compras.json	Compras realizadas
- proveedores.json	Proveedores registrados
- Fecha	Información temporal obtenida mediante una herramienta

Estas fuentes son consultadas mediante herramientas especializadas.

**Herramientas del agente**

El sistema implementa diferentes Tools, donde cada herramienta tiene una responsabilidad específica.

  **consultar_ventas**

    Permite consultar las ventas almacenadas en ventas.json.

    Se utiliza cuando el usuario realiza preguntas relacionadas con:

    - Ventas.
    - Productos más vendidos.
    - Cantidades vendidas.
    - Ingresos registrados.
    
  **consultar_inventario**

    Consulta el estado actual del inventario.
    
    Permite responder preguntas relacionadas con:

    - Existencias.
    - Productos con bajo inventario.
    - Productos disponibles.
    - Niveles de stock.

  **consultar_productos**

    Consulta el catálogo de productos registrados.

  **consultar_compras**

    Consulta las compras almacenadas en el sistema.

  **consultar_proveedores**

    Consulta los proveedores registrados.
    
    Si no existen proveedores registrados, la herramienta devuelve esta situación al agente para que pueda comunicarla al usuario.

  **obtener_fecha**

    Permite obtener información relacionada con la fecha actual.
    
**Arquitectura del sistema**

La arquitectura implementada es híbrida, basada principalmente en una organización por capas e incorporando elementos orientados a eventos para 
situaciones que puedan requerir alertas

                    USUARIO
                       │
                       ▼
                 INTERFAZ CHAT
                       │
                       ▼
                 AGENTE DE IA
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       ROUTER CHAIN        ESTADO / MEMORIA
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
     CHAIN       AGENT
       │           │
       │      ┌────┴────┐
       │      │         │
       │      ▼         ▼
       │    LLM       TOOLS
       │                │
       │       ┌────────┼────────┐
       │       ▼        ▼        ▼
       │    Ventas / Inventario / Productos
       │
       │   Compras / Proveedores / Fecha
       │                │
       └────────────────┘
                       │
                       ▼
                   RESPUESTA
                       │
                       ▼
                USUARIO / UI

**Componentes principales**

**Interfaz**
Aplicación desarrollada con Streamlit que permite al usuario interactuar mediante un chat.

**Router Chain**
Clasifica la consulta y determina si debe procesarse mediante Chain o Agent.

**Response Chain**
Resuelve consultas generales que no necesitan consultar herramientas.

**Agent**
Procesa solicitudes que requieren información del negocio y puede utilizar una o varias herramientas.

**LLM**
Modelo de lenguaje Gemini utilizado para interpretar las solicitudes, razonar sobre los resultados de las herramientas y generar respuestas.

**Tools**
Funciones especializadas que permiten acceder a las fuentes de información del negocio.

**Estado y memoria**
Conservan información del negocio identificada durante la conversación y los mensajes recientes.

**Flujo de funcionamiento**

El funcionamiento del agente sigue el siguiente proceso:

      1. Usuario realiza una consulta
                    ↓
      2. Se actualiza el estado y memoria
                    ↓
      3. Router Chain analiza la consulta
                    ↓
             ┌──────┴──────┐
             ↓             ↓
         Consulta       Consulta
          general       de datos
             ↓             ↓
           Chain         Agent
             │             │
             │        Selecciona Tools
             │             │
             │        Consulta datos
             │             │
             │        Analiza resultados
             │             │
             └──────┬──────┘
                    ↓
             Generación respuesta
                    ↓
             Registro ejecución
                    ↓
                  Usuario

**Orquestación mediante Router Chain**

El Router Chain constituye el primer componente de decisión del sistema.

Su función no es responder la pregunta, sino determinar qué ruta debe seguir la solicitud.

Para esto se utiliza una salida estructurada mediante Pydantic:

    class RutaConsulta(BaseModel):
        ruta: Literal["chain", "agent"]
        motivo: str

    El router puede producir:
    
    ruta: chain
    motivo: La consulta es conceptual y no requiere
            información específica del negocio.
    
    o:
    
    ruta: agent
    motivo: La consulta requiere consultar información
            almacenada en las fuentes del negocio.
            
    Esto permite separar la responsabilidad de clasificación de la responsabilidad de ejecución.

**Response Chain**

Cuando el Router determina que la consulta es general, se utiliza el Response Chain.

Su estructura sigue el patrón de LangChain:

      Prompt
         ↓
      Modelo Gemini
         ↓
      StrOutputParser
         ↓
      Respuesta

**Agent y Multi-Tools**

Cuando la consulta requiere datos reales del negocio, el Router selecciona la ruta Agent.

El agente recibe las herramientas disponibles:

    TOOLS = [
        obtener_fecha,
        consultar_ventas,
        consultar_inventario,
        consultar_proveedores,
        consultar_compras,
        consultar_productos,
    ]

    El Agent puede determinar qué herramienta necesita utilizar y, cuando la consulta lo requiere, puede utilizar más de una herramienta.

**Estado y memoria**

El sistema mantiene un estado utilizando st.session_state.

Se manejan principalmente:

      contexto_negocio
      mensajes
      ultima_ejecucion

**Contexto del negocio**

Permite almacenar información identificada durante la conversación, como el nombre del puesto.

**Memoria**

El sistema conserva los últimos mensajes de la conversación para proporcionar contexto al agente.

Actualmente se utiliza una memoria deslizante de hasta 6 mensajes.

**Última ejecución**

El sistema registra:

Ruta utilizada.
Motivo de la decisión del Router.
Herramientas utilizadas.

Esta información se muestra en la barra lateral de Streamlit.


