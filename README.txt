cd users/lpoggio/documents/opencode/backend

uvicorn main:app --reload --port 8000


═══════════════════════════════════════════════════════════════════════════════
                     BACKEND - CHAT CON IA
═══════════════════════════════════════════════════════════════════════════════

Este es el backend de tu aplicacion de chat con IA.
Esta guia esta escrita para que puedas entender y aprender como funciona.


───────────────────────────────────────────────────────────────────────────────────────────────
QUE ES UN BACKEND?
───────────────────────────────────────────────────────────────────────────────────────────────

Un backend es la parte "invisible" de una aplicacion web.
Es el servidor que procesa datos, conecta con bases de datos, y comunica
con servicios externos (como la IA).

El frontend (tu web en React) le envia peticiones al backend, y el backend
le devuelve respuestas.

Frontend (tu web)  -->  Peticion HTTP  -->  Backend  -->  IA
                                                        |
                                                        v
                                              Respuesta JSON <--


───────────────────────────────────────────────────────────────────────────────────────────────
TECNOLOGIAS USADAS
───────────────────────────────────────────────────────────────────────────────────────────────

LENGUAJE DE PROGRAMACION:
- Python 3.10+  - Lenguaje principal del backend

FRAMEWORKS:
- FastAPI        - Framework web moderno y rapido
- Uvicorn        - Servidor ASGI para ejecutar FastAPI

LIBRERIAS:
- requests      - Para hacer peticiones HTTP a otros servidores
- pydantic     - Validacion de datos


───────────────────────────────────────────────────────────────────────────────────────────────
ESTRUCTURA DEL PROYECTO
───────────────────────────────────────────────────────────────────────────────────────────────

backend/
├── main.py          - Codigo principal de la API
├── requirements.txt - Lista de dependencias
└── README.txt      - Este archivo


───────────────────────────────────────────────────────────────────────────────────────────────
COMO EJECUTAR EL BACKEND
───────────────────────────────────────────────────────────────────────────────────────────────

cd users/lpoggio/documents/opencode/backend

1. Instalar dependencias (solo la primera vez):
   pip install -r requirements.txt

2. Iniciar el servidor:
   uvicorn main:app --reload --port 8000

3. Probar que funcione:
   Abrir en el navegador: http://localhost:8000

   Debe mostrar: {"api":"Chat IA","status":"running"}


───────────────────────────────────────────────────────────────────────────────────────────────
ENDPOINTS (RUTAS DE LA API)
───────────────────────────────────────────────────────────────────────────────────────────────

Un endpoint es una URL especial que el frontend llama para
pedir algo al backend.

GET /
   - Ruta raiz, solo para verificar que la API funciona
   - Ejemplo: http://localhost:8000/
   - Respuesta: {"api":"Chat IA","status":"running"}

GET /chats
   - Obtiene todos los chats guardados
   - Devuelve: {"chats": [chat1, chat2, ...]}

POST /chats
   - Crea un nuevo chat
   - Envia: {"message": "Hola"}
   - Devuelve: {"chat": {...}}

DELETE /chats/{id}
   - Elimina un chat por su ID
   - Devuelve: {"success": true}

POST /chat
   - Envia un mensaje y recibe respuesta de la IA
   - Envia: {"message": "Hola", "chat_id": "opcional"}
   - Devuelve: {"chat": {...}, "response": {...}}

POST /chat/stream
   - Envia mensaje con respuesta en tiempo real (streaming)
   - Similar a /chat pero la respuesta llega pedacito a pedacito


───────────────────────────────────────────────────────────────────────────────────────────────
COMUNICACION FRONTEND <-> BACKEND
───────────────────────────────────────────────────────────────────────────────────────────────

El frontend hace peticiones al backend usando fetch() o axios.

Ejemplo en JavaScript:
   // Enviar mensaje
   const response = await fetch('http://localhost:8000/chat', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ message: 'Hola' })
   })
   const data = await response.json()
   console.log(data.response.text)


───────────────────────────────────────────────────────────────────────────────────────────────
COMO CONECTAR CON MINIMAX
───────────────────────────────────────────────────────────────────────────────────────────────

CUANDO TENGAS TU API KEY:

1. Ve a https://www.minimaxi.ai/open/platform
2. Registrate / Loggeate
3. Copia tu API Key
4. En main.py, busca la seccion "# CONFIGURACION DE MINIMAX"
5. Reemplaza "TU_API_KEY_AQUI" por tu key
6. Descomenta el codigo de call_minimax()

La funcion call_minimax() hace esto:

1. Recibe el mensaje del usuario
2. Lo arma en formato JSON con el modelo a usar
3. Lo envia a la API de MiniMax (https://api.minimaxi.chat)
4. Espera la respuesta
5. La devuelve al frontend

Parametros importantes:
- model: "MiniMax-M2.5" (el mas nuevo)
- temperature: 0.7 (que tan creativo, 0-1)
- max_tokens: 2000 (maximo de palabras)


───────────────────────────────────────────────────────────────────────────────────────────────
CONCEPTOS IMPORTANTES
───────────────────────────────────────────────────────────────────────────────────────────────

1. FastAPI
   Framework de Python para crear APIs web.
   Ventajas:
   -Muy rapido
   -Documentacion automatica en /docs
   -Validacion de datos automatica
   -Facil de usar

2. Pydantic BaseModel
   Define la estructura de los datos.
   Ejemplo:
      class Usuario(BaseModel):
          nombre: str
          edad: int
   
   Si mandas {"nombre": "Lucas"} sin edad, FastAPI da error.

3. UUID
   Identificador unico de 36 caracteres.
   Ejemplo: "550e8400-e29b-41d4-a716-446655440000"
   Casi imposible de duplicar.

4. Streaming
   Responder en tiempo real, pedacito a pedacito.
   En lugar de esperar a que termine todo, vas mostrando
   lo que se va generando.

5. CORS
   Cross-Origin Resource Sharing.
   Permite que el frontend pueda acceder al backend
   aunque esten en puertos distintos.


───────────────────────────────────────────────────────────────────────────────────────────────
QUE FALTA IMPLEMENTAR?
───────────────────────────────────────────────────────────────────────────────────────────────

- [x] Estructura basica de FastAPI
- [x] Rutas para chats (crear, listar, eliminar)
- [x] Respuesta basica simulada
- [ ] Conectar con MiniMax real (necesitas API Key)
- [ ] Streaming real
- [ ] Guardar en base de datos
- [ ] Autenticacion de usuarios

Vamos paso a paso!


═══════════════════════════════════════════════════════════════════════════════