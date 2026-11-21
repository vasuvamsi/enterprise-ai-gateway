from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from app.graph import agent_graph

app = FastAPI(title="Enterprise AI Gateway")
Instrumentator().instrument(app).expose(app)

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(req: ChatRequest):
    result = await agent_graph.ainvoke({
        "messages": [("user", req.query)],
        "is_safe": True,
        "flags": [],
    })
    return {
        "reply": result["messages"][-1].content,
        "security_flags": result["flags"],
    }