from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from tools.rag_core import (
    load_investor_documents,
    split_investor_documents,
    load_decision_rules,
    load_vectorstore,
    create_vectorstore,
    query_vectorstore
)

app = FastAPI(title="Investment Masters RAG API")

# 全局向量库实例
vectorstore = None
PERSIST_DIR = str(PROJECT_ROOT / "vectorstore")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    investor_id: Optional[str] = None
    source_type: Optional[str] = None
    kind: Optional[str] = None

class QueryResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity_estimate: float

@app.on_event("startup")
async def startup_event():
    global vectorstore
    print(f"正在初始化 RAG 服务，持久化目录: {PERSIST_DIR}")
    
    if os.path.exists(PERSIST_DIR):
        print("发现已持久化的向量库，正在加载...")
        try:
            vectorstore = load_vectorstore(PERSIST_DIR)
            print("向量库加载成功!")
        except Exception as e:
            print(f"加载失败: {e}，将重新构建...")
            vectorstore = None

    if vectorstore is None:
        print("正在构建新的向量库（这可能需要一些时间）...")
        investor_docs = load_investor_documents()
        investor_docs = split_investor_documents(investor_docs)
        rule_docs = load_decision_rules()
        all_docs = investor_docs + rule_docs
        vectorstore = create_vectorstore(all_docs, PERSIST_DIR)
        print("向量库构建并保存成功!")

@app.get("/health")
async def health():
    return {"status": "ok", "vectorstore_ready": vectorstore is not None}

@app.post("/query", response_model=List[QueryResponse])
async def query(req: QueryRequest):
    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vectorstore not ready")

    # 构建过滤器
    filter_dict = {}
    if req.investor_id:
        filter_dict["investor_id"] = req.investor_id
    if req.source_type:
        filter_dict["source_type"] = req.source_type
    if req.kind:
        filter_dict["kind"] = req.kind
    
    if not filter_dict:
        filter_dict = None

    try:
        results = query_vectorstore(vectorstore, req.query, k=req.top_k, filter_dict=filter_dict)
        
        responses = []
        for doc, score in results:
            responses.append(QueryResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                similarity_estimate=round(1 - score, 4)
            ))
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
