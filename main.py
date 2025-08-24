from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_message_histories import ChatMessageHistory
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
from  chatbot import generate_response
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from supabase_client import (
    create_guest_data, get_guest_data_by_session_id, update_guest_data
)

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wellmate.harshkb.shop", "http://localhost:8000", "http://wellmate.harshkb.shop:8000"],  # Update with your live domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Pydantic models for request validation
class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str
    language: str
    phone: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

# Test endpoint to verify server is running
@app.get("/test")
def test_endpoint():
    return {"status": "Server is running", "message": "Test endpoint reached"}

# Serve login page as root
@app.get("/")
def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "login_classic.html"))

# Create new chat session
@app.post("/new-chat")
async def new_chat():
    session_id = f"guest-{str(uuid.uuid4())}"
    new_guest_data = {
        "session_id": session_id,
        "patient_name": "Guest",
        "patient_age": 0,
        "patient_gender": "Unknown",
        "patient_language": "English",
        "patient_phone": "",
        "chat_history": []
    }
    guest_data = create_guest_data(new_guest_data)
    if not guest_data:
        raise HTTPException(status_code=500, detail="Failed to create new session")
    return {"session_id": session_id}

# Update patient info endpoint
@app.post("/update-patient")
async def update_patient_info(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    patient_info = data.get("patient_info")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    if not patient_info or not isinstance(patient_info, dict):
        raise HTTPException(status_code=400, detail="Invalid patient info")
    
    required_fields = {"name": "Unknown", "age": 0, "gender": "Unknown", "language": "English", "phone": ""}
    updated_info = {key: patient_info.get(key, default) for key, default in required_fields.items()}
    updated_info["age"] = int(updated_info["age"]) if isinstance(updated_info["age"], (str, int)) else 0

    guest_data = get_guest_data_by_session_id(session_id)
    if not guest_data:
        new_guest_data = {
            "session_id": session_id,
            "patient_name": updated_info["name"],
            "patient_age": updated_info["age"],
            "patient_gender": updated_info["gender"],
            "patient_language": updated_info["language"],
            "patient_phone": updated_info["phone"],
            "chat_history": []
        }
        guest_data = create_guest_data(new_guest_data)
    else:
        guest_data["patient_name"] = updated_info["name"]
        guest_data["patient_age"] = updated_info["age"]
        guest_data["patient_gender"] = updated_info["gender"]
        guest_data["patient_language"] = updated_info["language"]
        guest_data["patient_phone"] = updated_info["phone"]
        update_guest_data(session_id, guest_data)
    
    return {"status": "success"}

# Chat endpoint
@app.post("/chat")
async def chat(chat_request: ChatRequest, request: Request):
    session_id = chat_request.session_id
    user_message = chat_request.message
    guest_data = get_guest_data_by_session_id(session_id)
    if not guest_data:
        raise HTTPException(status_code=404, detail="Session not found")
    patient_info = {
        "name": guest_data.get("patient_name", "Guest"),
        "age": guest_data.get("patient_age", 0),
        "gender": guest_data.get("patient_gender", "Unknown"),
        "language": guest_data.get("patient_language", "English"),
        "phone": guest_data.get("patient_phone", "")
    }
    chat_history = ChatMessageHistory()
    for msg in guest_data.get("chat_history", []):
        try:
            if msg["type"] == "human":
                chat_history.add_user_message(msg["content"])
            elif msg["type"] == "ai":
                chat_history.add_ai_message(msg["content"])
        except KeyError:
            continue
    default_info = {"name": "Unknown", "age": 0, "gender": "Unknown", "language": "English", "phone": ""}
    for key, default in default_info.items():
        if key not in patient_info:
            patient_info[key] = default
    patient_info["age"] = int(patient_info["age"]) if isinstance(patient_info["age"], (str, int)) else 0

    system_prompt = (
        "You are a female physician with 30 years of experience in general practice; your name is Dr. Black. "
        f"IMPORTANT PATIENT INFO: The patient's name is {patient_info['name']}, age {patient_info['age']}, gender {patient_info['gender']}. "
        f"You MUST always respond in the patient's preferred language ({patient_info['language']}) using simple, clear sentences. "
        f"Always consider the patient's age ({patient_info['age']}) and gender ({patient_info['gender']}) in your responses. "
        "Act as a doctor: ask clarifying questions to understand symptoms before diagnosing or prescribing. "
        "NEVER use apologetic sentences like 'Sorry to hear that...'. "
        "You MUST use retrieved documents if they exist; otherwise, say 'I don’t know'. "
        "DO NOT suggest visiting your clinic, but DO NOT forget to prescribe medicine if needed after a full consultation. "
        "When prescribing medicine, ALWAYS include how to use it (e.g., dosage and timing) and how many days to take it. "
        "Use positive vibes and emojis (e.g., 😊) appropriately. "
        "During prescribe must use context : {context}"
    )
    
    try:
        bot_response = generate_response(system_prompt, chat_history, user_message)
        guest_data["chat_history"].append({"type": "human", "content": user_message})
        guest_data["chat_history"].append({"type": "ai", "content": bot_response})
        update_guest_data(session_id, {"session_id": session_id, "chat_history": guest_data["chat_history"]})
        return {"response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/logout")
async def logout(request: Request):
    session_id = request.session.get("session_id")
    if session_id:
        request.session.clear()
    return RedirectResponse(url="/")