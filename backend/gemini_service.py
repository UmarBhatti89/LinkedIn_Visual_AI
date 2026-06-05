import os
import io
import base64
from PIL import Image
from google import genai  # Google's new official SDK package
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_all_gemini_keys():
    """.env se saari available keys load karne ke liye"""
    keys = []
    for i in range(1, 6):  # 1 se lekar 5 tak check karega
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)

    # Backup: Agar dynamic keys na milen toh purani default key use karein
    if not keys and os.getenv("GEMINI_API_KEY"):
        keys.append(os.getenv("GEMINI_API_KEY"))
    return keys

def generate_linkedin_comment(post_text: str, author_name: str, tone: str, length: str, image_base64: str = "") -> str:
    # 1. Fetch all rotated keys
    api_keys = get_all_gemini_keys()
    if not api_keys:
        return "Error: No Gemini API keys configured on server."

    # Length mapping dynamically handled
    if length == "Short":
        length_instruction = "Strictly maximum 1 short, punchy sentence."
    elif length == "Long":
        length_instruction = "Provide a detailed response with 3 to 4 sentences."
    else:
        length_instruction = "Keep it balanced, maximum 2 to 3 concise sentences."

    # Prompt Template
    prompt_template = """
    You are a highly adaptable, emotionally intelligent LinkedIn user. Your core skill is matching the exact context, intent, visual details, and the EXACT LANGUAGE/SCRIPT of the post.

    CRITICAL STEP 0: UNIVERSAL LANGUAGE MATCHING (MANDATORY)
    - Analyze the language and script of the 'Text Content' and the pixels of the provided image (if any).
    - You MUST write the final comment in the SAME language and script that the post or image is primarily using:
      * If the post/image is in Arabic script, reply in beautiful, respectful Arabic.
      * If the post/image uses Roman Urdu/Hinglish, reply in natural Roman Urdu.
      * If the post/image is in Standard English, reply in Standard English.

    STEP 1: DYNAMIC CONTEXT CLASSIFICATION (TEXT + VISUAL)
    - IF an image is present, read its content carefully:
      * If it's a Meme or Funny image: Understand the joke and relate to it as a tech peer.
      * If it's an Islamic Quote, Hadith, or Blessing: Write a highly respectful, aligned, and meaningful response matching its exact script.
      * If it's a Certificate or Job Change: Directly congratulate them on that specific achievement or topic.
      * If it's a Project Showcase or UI Design: Praise the specific layout, stack, or visual output.
      * If it's a news/humanitarian crisis post (e.g., Gaza, poverty, human suffering): Be deeply empathetic, human, and supportive. DO NOT use generic corporate, trade, or innovation comments.

    REQUIRED TONE: {selected_tone}
    REQUIRED LENGTH RULE: {selected_length}

    CRITICAL HUMANITARIAN RULES:
    1. SPEAK LIKE A LIVE HUMAN: Do NOT talk like an observer, AI bot, or professor. Talk directly to the author.
    2. BANNED WORDS (ENGLISH): NEVER use corporate AI filler words like 'highlights the importance', 'testament', 'delve', 'landscape', 'realm', 'pivotal', 'crucial', or 'dynamic'.
    3. NO HASHTAGS. Use emojis very sparingly (maximum 1).

    Post Author: {author}
    Text Content (if any): "{content}"

    Write the final comment directly below:
    """

    final_prompt = prompt_template.format(
        selected_tone=tone,
        selected_length=length_instruction,
        author=author_name,
        content=post_text,
    )

    # Decode incoming Base64 image payload inside server memory
    img = None
    if image_base64:
        try:
            print("[BACKEND] Decoding incoming Base64 image payload from browser...")
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]

            img_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(img_data))
            print("[BACKEND] Base64 Image parsed successfully into PIL instance.")
        except Exception as img_err:
            print(f"[BACKEND] Base64 image decoding failed: {img_err}")

    # 2. KEY ROTATION FAILOVER LOOP (Updated for Google's New GenAI Client)
    for idx, current_key in enumerate(api_keys):
        try:
            print(f"[API ROTATION] Attempting generation with Key #{idx + 1} using New SDK...")

            # Google's New SDK client instantiation
            client = genai.Client(api_key=current_key)

            # Creating request contents array
            contents_payload = [final_prompt]
            if img:
                contents_payload.append(img)

            # Generating content using the updated SDK structure
            ai_response = client.models.generate_content(
                model="gemini-3.1-flash-lite", contents=contents_payload
            )

            print(f"[BACKEND] Success! Comment generated using Key #{idx + 1}")
            return ai_response.text.strip()

        except Exception as api_error:
            print(f"[API WARN] Key #{idx + 1} failed or hit rate-limit. Error: {str(api_error)}")
            print("[API ROTATION] Switching to next available fallback key...")
            continue

    return "Error: All configured Gemini API keys hit rate limits or failed. Please try again later."

# ==========================================
# FEATURE UPGRADE: THREAD-AWARE REPLY ENGINE
# ==========================================
def generate_linkedin_reply(post_text: str, my_comment: str, their_reply: str, tone: str, length: str) -> str:
    api_keys = get_all_gemini_keys()
    if not api_keys:
        return "Error: No Gemini API keys configured on server."

    if length == "Short":
        length_instruction = "Strictly maximum 1 short, punchy sentence."
    elif length == "Long":
        length_instruction = "Provide a detailed response with 3 to 4 sentences."
    else:
        length_instruction = "Keep it balanced, maximum 2 to 3 concise sentences."

    prompt_template = """
    You are engaged in an ongoing LinkedIn conversation thread. Your goal is to reply to a user who just commented on your thread, maintaining a completely natural, human, and professional tone.

    CRITICAL RULE:
    - Write the response in the EXACT same language and script used in 'Their Reply'. If they replied in Roman Urdu, you must answer in Roman Urdu. If English, answer in English.

    CRITICAL CONVERSATIONAL DEPTH RULE:
    - Analyze the depth of 'Their Reply to Me'. 
    - If it is a short courtesy reply (e.g., "Thanks", "Great", "Agreed", "True"), provide a short, polite, and punchy acknowledgement. DO NOT over-explain or write long paragraphs.
    - If it contains a question, deep thought, or critique related to the post, read the 'Original Post Content' thoroughly, analyze 'My Previous Comment', and provide a deeply contextual, intellectual, and high-value counter-reply.

    CONTEXT TRACE:
    1. Original Post Content: "{post}"
    2. My Previous Comment: "{my_old_comment}"
    3. Their Reply to Me: "{reply_to_me}"

    REQUIRED TONE: {selected_tone}
    REQUIRED LENGTH RULE: {selected_length}

    HUMANITARIAN RULES:
    - Reply directly to the author of 'Their Reply'. Do NOT sound robotic.
    - No corporate filler words or hashtags. Max 1 emoji.

    Write the final reply directly below:
    """

    final_prompt = prompt_template.format(
        post=post_text,
        my_old_comment=my_comment,
        reply_to_me=their_reply,
        selected_tone=tone,
        selected_length=length_instruction
    )

    # KEY ROTATION LOOP
    for idx, current_key in enumerate(api_keys):
        try:
            print(f"[REPLY ENGINE] Attempting with Key #{idx + 1}...")
            client = genai.Client(api_key=current_key)
            
            ai_response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=[final_prompt]
            )
            return ai_response.text.strip()
        except Exception as api_error:
            print(f"[REPLY WARN] Key #{idx + 1} failed: {str(api_error)}")
            continue

    return "Error: Generation failed across all keys."
