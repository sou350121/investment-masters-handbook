import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def load_investor_documents():
    """加载投资者文档为 LangChain Document 格式"""
    from langchain.schema import Document
    
    documents = []
    investors_dir = PROJECT_ROOT / "investors"
    
    # 加载投资者索引获取元数据
    index_file = PROJECT_ROOT / "config" / "investor_index.yaml"
    investor_meta = {}
    
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f)
            for inv in index_data.get("investors", []):
                investor_meta[inv["id"]] = inv
    
    # 加载每个投资者的 Markdown 文件
    for md_file in investors_dir.glob("*.md"):
        investor_id = md_file.stem
        
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 获取元数据
        meta = investor_meta.get(investor_id, {})
        
        doc = Document(
            page_content=content,
            metadata={
                "source": str(md_file.relative_to(PROJECT_ROOT)),
                "investor_id": investor_id,
                "investor_name": meta.get("full_name", investor_id),
                "chinese_name": meta.get("chinese_name", ""),
                "style": ", ".join(meta.get("style", [])),
                "best_for": ", ".join(meta.get("best_for", [])),
            }
        )
        documents.append(doc)
    
    return documents

def split_investor_documents(documents, chunk_size: int = 900, chunk_overlap: int = 200):
    """将投资者长文档分块，并记录 start_index 用于精确溯源"""
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "],
        add_start_index=True,
    )

    split_docs = []

    for parent in documents:
        investor_id = parent.metadata.get("investor_id", "unknown")
        chunks = splitter.split_documents([parent])

        for idx, doc in enumerate(chunks):
            # 标题提示：取 chunk 内第一个 markdown 标题
            m = re.search(r"(?m)^(#{1,4})\s+(.+?)\s*$", doc.page_content)
            title_hint = m.group(2) if m else ""

            doc.metadata["source_type"] = "investor_doc"
            doc.metadata["chunk_index"] = idx
            doc.metadata["chunk_id"] = f"{investor_id}#{idx}"
            if title_hint:
                doc.metadata["title_hint"] = title_hint

        split_docs.extend(chunks)

    return split_docs

def load_decision_rules():
    """加载决策规则为 Document 格式"""
    from langchain.schema import Document
    
    rules_file = PROJECT_ROOT / "config" / "decision_rules.generated.json"
    if not rules_file.exists():
        return []
    
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    for rule in data.get("rules", []):
        content = f"""
投资者: {rule.get('investor_id', 'unknown')}
规则类型: {rule.get('kind', 'other')}

IF {rule.get('when', 'N/A')}
THEN {rule.get('then', 'N/A')}
BECAUSE {rule.get('because', 'N/A')}
        """.strip()
        
        doc = Document(
            page_content=content,
            metadata={
                "source": "decision_rules.generated.json",
                "investor_id": rule.get("investor_id", "unknown"),
                "rule_id": rule.get("rule_id", ""),
                "kind": rule.get("kind", "other"),
                "source_type": "rule",
            }
        )
        documents.append(doc)
    
    return documents

def get_embeddings():
    """获取 Embedding 模型配置"""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

def create_vectorstore(documents, persist_dir=None):
    """创建并可选持久化向量存储"""
    from langchain_community.vectorstores import Chroma
    embeddings = get_embeddings()
    
    if persist_dir:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        vectorstore.persist()
    else:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings
        )
    return vectorstore

def load_vectorstore(persist_dir: str):
    """从持久化目录加载向量存储"""
    from langchain_community.vectorstores import Chroma
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=get_embeddings(),
    )

def query_vectorstore(vectorstore, query: str, k: int = 5, filter_dict: dict = None):
    """查询向量存储，支持元数据过滤"""
    return vectorstore.similarity_search_with_score(
        query, 
        k=k,
        filter=filter_dict
    )
