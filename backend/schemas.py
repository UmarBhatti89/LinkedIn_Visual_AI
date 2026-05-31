from pydantic import BaseModel
from typing import Optional

class CommentRequest(BaseModel):
    post_text: str
    author_name: str
    tone: Optional[str] = "Insightful"
    length: Optional[str] = "Medium"
    image_url: Optional[str] = ""  # <--- Yeh field yahan hona zaroori hai

class CommentResponse(BaseModel):
    suggested_comment: str