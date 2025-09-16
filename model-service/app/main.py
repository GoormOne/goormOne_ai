from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

class TextInput(BaseModel):
    text: str

@app.post("/embed")
def embed(input: TextInput):
    vector = model.encode([input.text])[0].tolist()
    return {"embedding": vector}
