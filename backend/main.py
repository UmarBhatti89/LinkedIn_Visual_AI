from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from gemini_service import generate_linkedin_comment

app = FastAPI()

# CORS Middleware (Jo aapka pehle se chal raha hai)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BETA ACCESS KEYS LIST ---
# Aap manually ya script se generate karke yahan keys add kar sakte hain
VALID_BETA_KEYS = {
    "BCREQ-83A1-92F4",
    "BCREQ-K7X2-P0W9",
    "BCREQ-M5Z1-L3W8",
    "BCREQ-B7V4-Q1X9",
    "BCREQ-ADMIN-TEST" # Testing ke liye ek easy key
}

# Request Data Model Update
class CommentRequest(BaseModel):
    post_text: str
    author_name: str
    tone: Optional[str] = "Insightful"
    length: Optional[str] = "Medium"
    image_url: Optional[str] = ""
    license_key: Optional[str] = ""  # <--- NAYI FIELD FOR ACCESS CONTROL

class CommentResponse(BaseModel):
    suggested_comment: str

@app.get("/")
def home():
    return {"message": "bCreatiq LinkedIn AI Comment API is running!"}

@app.post("/generate-comment", response_model=CommentResponse)
def get_comment(request: CommentRequest):
    # CRITICAL: License Key Check
    if not request.license_key or request.license_key not in VALID_BETA_KEYS:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Invalid Beta Key. DM Umar Bhatti on LinkedIn to get a key! https://www.linkedin.com/in/umarfb/ "
        )
    
    # Agar key valid hai, toh hi Gemini service call hogi
    comment = generate_linkedin_comment(
        post_text=request.post_text,
        author_name=request.author_name,
        tone=request.tone,
        length=request.length,
        image_url=request.image_url
    )
    
    return CommentResponse(suggested_comment=comment)