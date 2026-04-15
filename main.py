"""
Backend - Chat con IA
Este backend conecta con Groq (modelos gratuitos).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import requests
import json
import os


# ==============================================================================
# CONFIGURACION
# ==============================================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# MODELOS
# ==============================================================================

class Message(BaseModel):
    id: str
    text: str
    is_user: bool
    time: str


class Chat(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: str


class ChatCreate(BaseModel):
    message: str


class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None


# ==============================================================================
# ALMACENAMIENTO
# ==============================================================================

chats_db = []
chats_counter = 0
tokens_used = 0
tokens_limit = 50000  # Límite gratuito de Groq (~50000 tokens/mes)


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def generate_id():
    return str(uuid.uuid4())


def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%H:%M")


# ==============================================================================
# GROQ (MODELOS GratuitOS)
# ==============================================================================

"""
GROQ es una API gratuita con modelos muy rapidos.
Modelos disponibles:
- llama-3.3-70b-versatile (el mejor gratuito)
- llama-3.1-70b-versatile  
- mixtral-8x7b-32768
- gemma2-9b-it
"""

#GROQ_API_KEY = ""
api_key = os.getenv("API_KEY")

def call_groq(user_message: str, chat_history: List[dict] = None) -> str:
    """
    Envia un mensaje a Groq y devuelve la respuesta.
    """
    from groq import Groq
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Construimos los mensajes para dar contexto
    messages = []
    
    # Instruccion del sistema
    messages.append({
        "role": "system",
        "content": "Eres un asistente util y amable. Responde siempre en español de manera clara y concisa. NO uses formato markdown, asteriscos, ni negritas. Escribe en texto plano normal."
    })
    
    # Historial del chat
    if chat_history:
        for msg in chat_history:
            role = "user" if msg.get('is_user') else "assistant"
            messages.append({
                "role": role,
                "content": msg.get('text', '')
            })
    
    # Mensaje actual
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Modelo: llama-3.3-70b-versatile es el mejor gratuito
    MODEL = "llama-3.3-70b-versatile"
    
    global tokens_used
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        
        # Extraemos la respuesta y el uso de tokens
        if response.choices:
            # Contamos tokens usados (prompt + completion)
            usage = response.usage
            if usage:
                tokens_used += usage.total_tokens
            return response.choices[0].message.content
        else:
            return "No hubo respuesta del modelo"
            
    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@app.get("/")
def root():
    return {"api": "Chat IA", "status": "running", "model": "Llama 3.3 (Groq)"}


@app.get("/metrics")
def get_metrics():
    """Devuelve las metricas de uso de tokens"""
    percentage = (tokens_used / tokens_limit) * 100 if tokens_limit > 0 else 0
    return {
        "used": tokens_used,
        "limit": tokens_limit,
        "percentage": round(percentage, 1),
        "remaining": tokens_limit - tokens_used
    }


@app.get("/chats")
def get_chats():
    return {"chats": chats_db}


@app.post("/chats")
def create_chat(data: ChatCreate):
    global chats_counter
    chats_counter += 1
    
    chat = {
        "id": generate_id(),
        "title": data.message[:30] + "..." if len(data.message) > 30 else data.message,
        "messages": [
            {
                "id": generate_id(),
                "text": data.message,
                "is_user": True,
                "time": get_current_time()
            }
        ],
        "created_at": get_current_time()
    }
    
    chats_db.append(chat)
    return {"chat": chat}


@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    global chats_db
    chats_db = [c for c in chats_db if c["id"] != chat_id]
    return {"success": True}


@app.post("/chat")
def send_message(data: ChatRequest):
    """
    Recibe un mensaje y devuelve la respuesta de la IA.
    """
    
    user_message = {
        "id": generate_id(),
        "text": data.message,
        "is_user": True,
        "time": get_current_time()
    }
    
    # Obtenemos el historial
    chat_history = []
    if data.chat_id:
        for chat in chats_db:
            if chat["id"] == data.chat_id:
                chat_history = chat.get("messages", [])
                break
    
    # Llamamos a Groq
    ai_text = call_groq(data.message, chat_history)
    
    ai_message = {
        "id": generate_id(),
        "text": ai_text,
        "is_user": False,
        "time": get_current_time()
    }
    
    # Guardamos en el historial
    if data.chat_id:
        for chat in chats_db:
            if chat["id"] == data.chat_id:
                chat["messages"].append(user_message)
                chat["messages"].append(ai_message)
                return {"chat": chat, "response": ai_message}
    
    # Crear nuevo chat
    chat = {
        "id": generate_id(),
        "title": data.message[:30] + "..." if len(data.message) > 30 else data.message,
        "messages": [user_message, ai_message],
        "created_at": get_current_time()
    }
    chats_db.append(chat)
    
    return {"chat": chat, "response": ai_message}


@app.post("/chat/stream")
async def send_message_stream(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    
    try:
        ai_text = call_groq(user_message)
    except Exception as e:
        ai_text = f"Error: {str(e)}"
    
    def generate():
        words = ai_text.split()
        for word in words:
            yield f"data: {json.dumps({'text': word, 'done': False})}\n\n"
        yield f"data: {json.dumps({'text': '', 'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )