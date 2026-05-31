from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from gemini_service import generate_linkedin_comment

# Initialize FastAPI instance
app = FastAPI(title="bCreatiq LinkedIn AI Comment API")

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
    image_base64: Optional[str] = "" # Updated field to receive raw pixels
    license_key: Optional[str] = ""

class CommentResponse(BaseModel):
    suggested_comment: str

@app.get("/")
def home():
    return {
        "status": "healthy", 
        "message": "bCreatiq LinkedIn AI Comment API is running flawlessly on Vercel!"
    }

@app.post("/generate-comment", response_model=CommentResponse)
def get_comment(request: CommentRequest):
    # License Key Security Layer
    if not request.license_key or request.license_key not in VALID_BETA_KEYS:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Invalid Beta Key. DM Abdul Qadeer on LinkedIn to get a key!"
        )
    
    # Core Vision / Prompt Service Execution (Passing base64 directly)
    comment = generate_linkedin_comment(
        post_text=request.post_text,
        author_name=request.author_name,
        tone=request.tone,
        length=request.length,
        image_base64=request.image_base64
    )
    
    return CommentResponse(suggested_comment=comment)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
