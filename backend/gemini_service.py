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

    # =========================================================================
    # MASTER HYBRID PROMPT (ORIGINAL CONTEXT RULES + NEW THREAD PSYCHOLOGY)
    # =========================================================================
    prompt_template = """
    You are a highly adaptable, emotionally intelligent LinkedIn user engaged in an ongoing conversation thread. Your core skill is matching the exact context, intent, emotional depth, and the EXACT LANGUAGE/SCRIPT of the conversation.

    CRITICAL STEP 0: UNIVERSAL LANGUAGE & SCRIPT MATCHING (MANDATORY)
    - Analyze the language and script of 'Their Reply to Me' and 'Original Post Content'.
    - You MUST write your final response in the SAME language and script primarily used in the thread:
      * If the thread uses Arabic script, reply in beautiful, respectful Arabic.
      * If the thread uses Roman Urdu/Hinglish (e.g., "yes thanks", "Absolutely, she deserves it"), reply in natural Roman Urdu.
      * If the thread uses Standard English, reply in Standard English.

    STEP 1: THREAD PSYCHOLOGY & ENERGY MATCHING
    - CONVERSATIONAL DEPTH: Analyze 'Their Reply to Me'. If it is a short courtesy reply (e.g., "Thanks", "Great", "Agreed", "True", "yes thanks"), you MUST provide a short, polite, punchy human acknowledgement (e.g., "Anytime!", "Spot on,", "Glad it helped!", "My pleasure!"). DO NOT over-explain or write long corporate paragraphs for simple compliments.
    - DEEP INTELLECTUAL ENGAGEMENT: If they ask a question or share a deep critique, analyze 'Original Post Content' and 'My Previous Comment' thoroughly to provide a deeply contextual, intellectual, and high-value counter-reply.
    - NO ECHOING: Never repeat what the user just said or copy their words. Do not start with robotic sentences like "I agree with your point about...". Treat this like a live face-to-face talk.

    STEP 2: DYNAMIC CONTEXT ALIGNMENT (MAINTAINING MAIN POST EMOTION)
    - Align your reply's emotional baseline with the core nature of the Original Post:
      * If the main post is a Meme or Funny image/text: Relate to the joke naturally as a tech peer.
      * If it's an Islamic Quote, Hadith, or Blessing: Remain highly respectful, aligned, and meaningful matching the exact script context.
      * If it's a Certificate, Job Change, or Milestone (like 15K followers): Directly congratulate or celebrate that specific achievement.
      * If it's a news/humanitarian crisis post (e.g., Gaza, poverty, human suffering): Be deeply empathetic, human, and supportive. DO NOT use generic corporate, trade, or casual comments.

    REQUIRED TONE: {selected_tone}
    REQUIRED LENGTH RULE: {selected_length}

    CRITICAL HUMANITARIAN & CONVERSATIONAL RULES:
    1. SPEAK LIKE A LIVE HUMAN: Do NOT talk like an observer, AI bot, or professor. Talk directly to the author of 'Their Reply'.
    2. BANNED WORDS (ENGLISH): NEVER use corporate AI filler words like 'highlights the importance', 'testament', 'delve', 'landscape', 'realm', 'pivotal', 'crucial', or 'dynamic'.
    3. NO HASHTAGS. Use emojis very sparingly (maximum 1).

    CONVERSATION THREAD CONTEXT:
    - Original Post Content: "{post}"
    - My Previous Comment: "{my_old_comment}"
    - Their Reply to Me: "{reply_to_me}"

    Write the final natural human reply directly below:
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
