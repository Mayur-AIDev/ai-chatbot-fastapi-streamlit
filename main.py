import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from huggingface_hub import InferenceClient
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

SECRET_CODE = os.environ.get("My_HuggingFace_API")
if not SECRET_CODE:
    raise RuntimeError("CRITICAL: My_HuggingFace_API environment variable is missing!")

app = FastAPI(title="Production AI Chat API with Memory Management")
client = InferenceClient(api_key=SECRET_CODE)

session_db: Dict[str, List[Dict[str, str]]] = {}


MAX_WINDOW_SIZE = 6

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID for tracking isolated user sessions")
    prompt: str = Field(..., min_length=1, max_length=4096, description="The message payload")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The generated string output from the LLM")

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(data: ChatRequest):
    try:
        if data.user_id not in session_db:
            session_db[data.user_id] = []
        
        
        session_db[data.user_id].append({"role": "user", "content": data.prompt})

        
        if len(session_db[data.user_id]) > MAX_WINDOW_SIZE:
            session_db[data.user_id] = session_db[data.user_id][-MAX_WINDOW_SIZE:]

        
        output = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=session_db[data.user_id],
            max_tokens=512,
            temperature=0.7
        )
        
        ai_response = output.choices[0].message.content
        if not ai_response:
            raise HTTPException(status_code=502, detail="Empty response from LLM Hub")

        # 4. Append AI response back to history
        session_db[data.user_id].append({"role": "assistant", "content": ai_response})

        return ChatResponse(response=ai_response)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference Engine Exception: {str(e)}"
        )
