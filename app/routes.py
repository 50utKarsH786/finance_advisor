from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage
from app.schemas import ChatRequest, ChatResponse
from app.graph import app_graph
from app.config import settings
from app.limiter import limiter

router = APIRouter()

def is_quota_error(e: Exception) -> bool:
    msg = str(e).lower()
    return "resource_exhausted" in msg or "quota" in msg or "429" in msg

@router.get("/")
@router.head("/")
def home():
    return {"message": "Finance agentic chatbot API is running"}

@router.get("/health")
@router.head("/health")
def health():
    return {"status": "healthy"}

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_STRING)
async def chat(req: ChatRequest, request: Request):
    try:
        # Try primary graph executor
        inputs = {"messages": [HumanMessage(content=req.query)]}
        result = await app_graph.ainvoke(inputs)
        
        # Extract the last AI message
        final_message = result["messages"][-1].content
        return ChatResponse(answer=final_message)
    except Exception as e:
        if is_quota_error(e):
            detail = (
                "Model quota exhausted or billing limit reached. "
                "Please check your Google GenAI limits."
            )
            raise HTTPException(status_code=503, detail=detail)
        raise HTTPException(status_code=500, detail=str(e))