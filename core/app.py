from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from PhiRag import RAGAgent
from fastapi.middleware.cors import CORSMiddleware


"""
Handle CORS middleware:
"""
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agent = RAGAgent()

class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str

@app.post("/load/")
async def load_and_index(url_request: URLRequest):
    """
    Load and index the content from the provided URL.
    """
    try:
        agent.load_and_index(url_request.url)
        return {"status": "success", "message": "Content loaded and indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/")
async def answer_query(query_request: QueryRequest):
    """
    Handle incoming user queries based on the indexed content.
    """
    try:
        print(query_request.query)
        response = agent.answer_query(query_request.query)
        return {"status": "success", "response": response}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear/")
async def clear_collection():
    """
    Clear the indexed content and reset the agent.
    """
    try:
        agent.clear_collection()
        return {"status": "success", "message": "Collection cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
