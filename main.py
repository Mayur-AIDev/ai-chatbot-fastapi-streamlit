from fastapi import FastAPI
from pydantic import BaseModel, Field
from huggingface_hub import InferenceClient
from typing import Annotated

app = FastAPI()

my_secret_token = "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"
client = InferenceClient(api_key=my_secret_token)

chat_history = []

class chatRequest(BaseModel):
    prompt: Annotated[str, Field(..., description="The message you want to send to the AI")]

@app.get("/")
def home():
    return {"status": "FastAPI Server is Running Perfectly!"}

@app.post("/chat")
def chat(data: chatRequest):
    try:
        chat_history.append({"role": "user", "content": data.prompt})

        output = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=chat_history
        )
        
        ai_response = output.choices[0].message.content

        chat_history.append({"role": "assistant", "content": ai_response})

        return {"response": ai_response}
        
    except Exception as e:
        return {"error": str(e)}
