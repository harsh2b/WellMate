
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from pydantic import BaseModel




# Load .env from root directory
load_dotenv()


supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL or SUPABASE_ANON_KEY not set in .env")

supabase: Client = create_client(supabase_url, supabase_key)

class GuestData(BaseModel):
    session_id: str
    patient_name: str | None = None
    patient_age: int | None = None
    patient_gender: str | None = None
    patient_language: str | None = None
    patient_phone: str | None = None
    chat_history: list = []

def create_guest_data(guest_data: dict):
    """Create guest data for guest users"""
    data = GuestData(**guest_data).dict(exclude_unset=True)
    try:
        response = supabase.table("guest_data").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return None

def get_guest_data_by_session_id(session_id: str):
    """Get guest data by session ID"""
    try:
        response = supabase.table("guest_data").select("*").eq("session_id", session_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return None

def update_guest_data(session_id: str, guest_data: dict):
    """Update guest data by session ID"""
    data = GuestData(**guest_data).dict(exclude_unset=True)

    if 'session_id' in guest_data:
        del guest_data['session_id']  # Remove session_id from update data
    try:
        response = supabase.table("guest_data").update(data).eq("session_id", session_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return None

