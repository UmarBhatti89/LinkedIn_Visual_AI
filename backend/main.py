from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from gemini_service import generate_linkedin_comment

# Initialize FastAPI App
app = FastAPI(title="bCreatiq LinkedIn AI Comment API")

# Global CORS Configuration (Vercel ke liye strict permissions open rakhna zaroori hai)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BETA ACCESS KEYS LIST ---
VALID_BETA_KEYS = {
    "BCREQ-83A1-92F4",
    "BCREQ-K7X2-P0W9",
    "BCREQ-M5Z1-L3W8",
    "BCREQ-B7V4-Q1X9",
    "BCREQ-ADMIN-TEST"
}

class CommentRequest(BaseModel):
    post_text: str
    author_name: str
    tone: Optional[str] = "Insightful"
    length: Optional[str] = "Medium"
    image_url: Optional[str] = ""
    license_key: Optional[str] = ""

class CommentResponse(BaseModel):
    suggested_comment: str

# Root route for Vercel health checks
@app.get("/")
def home():
    return {"status": "healthy", "message": "bCreatiq LinkedIn AI Comment API is running on Vercel!"}

@app.post("/generate-comment", response_model=CommentResponse)
def get_comment(request: CommentRequest):
    # License Key Verification
    if not request.license_key or request.license_key not in VALID_BETA_KEYS:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Invalid Beta Key. DM Abdul Qadeer on LinkedIn to get a key!"
        )
    
    # Gemini Multimodal Execution
    comment = generate_linkedin_comment(
        post_text=request.post_text,
        author_name=request.author_name,
        tone=request.tone,
        length=request.length,
        image_url=request.image_url
    )
    
    return CommentResponse(suggested_comment=comment)
