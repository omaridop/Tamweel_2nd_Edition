from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
# import asyncpg  # Pseudo-code for pgvector DB connection

app = FastAPI(title="Tamweel Knowledge Retrieval API")

class TransactionContext(BaseModel):
    transaction_id: str
    amount: float
    date: str
    description: str

class RAGPayloadResponse(BaseModel):
    user_id: str
    policy_chunks: List[str]
    transaction_context: List[TransactionContext]
    synthesized_prompt: str

# Mock database dependency
async def get_db():
    # conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    # yield conn
    # await conn.close()
    yield None

@app.get("/api/v1/rag-payload/{user_id}", response_model=RAGPayloadResponse)
async def get_rag_payload(user_id: str, db = Depends(get_db)):
    """
    Retrieves recent transaction context for a user and relevant credit policy chunks
    from pgvector to construct a RAG payload.
    """
    
    # 1. Fetch Transaction Context (From Transaction Context Boundary)
    # Query: SELECT * FROM transactions WHERE user_id = $1 ORDER BY date DESC LIMIT 10
    recent_transactions = [
        TransactionContext(
            transaction_id="TXN-1001",
            amount=1500.00,
            date="2026-06-25",
            description="Salary Deposit"
        ),
        TransactionContext(
            transaction_id="TXN-1002",
            amount=-350.00,
            date="2026-06-26",
            description="Utility Bill"
        )
    ]
    
    # 2. Embed user query/context to search pgvector (Knowledge Retrieval Context)
    # Query: 
    # SELECT content FROM policy_chunks 
    # ORDER BY embedding <-> $1 LIMIT 5;
    policy_chunks = [
        "[Chapter 4 > Section 4.1] Debt-to-Income Ratio: Applicants must maintain a DTI below 40%...",
        "[Chapter 4 > Section 4.2] Recent Transactions: Consistent salary deposits are required..."
    ]
    
    # 3. Construct the Synthesized RAG Payload
    txn_text = "\n".join([f"- {t.date}: {t.description} ({t.amount})" for t in recent_transactions])
    policy_text = "\n\n".join(policy_chunks)
    
    synthesized_prompt = f"""You are a financial credit decision assistant for Tamweel.
    
USER TRANSACTION CONTEXT:
{txn_text}
    
RELEVANT CREDIT POLICIES:
{policy_text}
    
Based on the policies and the user's recent transactions, evaluate the credit risk.
"""
    
    return RAGPayloadResponse(
        user_id=user_id,
        policy_chunks=policy_chunks,
        transaction_context=recent_transactions,
        synthesized_prompt=synthesized_prompt
    )
