from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .document_processor import process_documents, query_document
from .gpt_interface import ask_gpt, transform_question
from .ado_interface import create_ado_ticket
from .config import load_config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
config = load_config()
vector_store = process_documents("documents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: Query):
    try:
        relevant_contexts = query_document(vector_store, query.question)
        context = " ".join(relevant_contexts) if relevant_contexts else ""
        
        formatted_prompt = f"""
        You are an AI assistant to resolve questions related to HR policies. 
        If you receive just a greeting, respond with a greeting.
        Provide the most accurate response based on the given context.
        If the question is not addressed in the context, inform the user that you don't have information on the question and suggest they raise a support ticket using the feedback form below.
        <context>
        {context}
        </context>
        Question: {query.question}
        """
        
        response = ask_gpt(formatted_prompt)
        
        if response:
            transformed = transform_question(query.question)
            
            return {
                "answer": response,
                "ticket_info": transformed if transformed else None
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get a response from JLL GPT")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TicketData(BaseModel):
    title: str
    description: str
    priority: int

@app.post("/create-ticket")
async def create_ticket(ticket_data: TicketData):
    try:
        ticket_id = create_ado_ticket(ticket_data.dict())
        return {"ticket_id": ticket_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
