#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investment Masters RAG Integration Example (Optimized)

使用 tools/rag_core.py 实现投资大师知识库的 RAG 检索。
"""

import argparse
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

def check_dependencies():
    """检查基础依赖"""
    missing = []
    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")
    try:
        from langchain.schema import Document
    except ImportError:
        missing.append("langchain")
    try:
        import chromadb
    except ImportError:
        missing.append("chromadb")
    
    if missing:
        print("缺少依赖，请安装:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

def format_results(results):
    """格式化搜索结果"""
    output = []
    for i, (doc, score) in enumerate(results, 1):
        investor_id = doc.metadata.get("investor_id", "unknown")
        investor_name = doc.metadata.get("chinese_name") or doc.metadata.get("investor_name") or investor_id
        source = doc.metadata.get("source", "unknown")
        source_type = doc.metadata.get("source_type", "unknown")
        rule_id = doc.metadata.get("rule_id", "")
        chunk_id = doc.metadata.get("chunk_id", "")
        title_hint = doc.metadata.get("title_hint", "")
        start_index = doc.metadata.get("start_index", 0)

        citation = rule_id or chunk_id or "N/A"
        
        output.append(f"\n{'='*60}")
        output.append(f"[{i}] 相似度(估算): {1-score:.2%} | 类型: {source_type} | 来源: {source}")
        output.append(f"    投资者: {investor_name} ({investor_id})")
        if title_hint:
            output.append(f"    章节: {title_hint}")
        if source_type == "investor_doc":
            output.append(f"    位置: 字符偏移 {start_index}")
        output.append(f"    引用: {citation}")
        output.append("-" * 60)
        
        content = doc.page_content[:500]
        if len(doc.page_content) > 500:
            content += "..."
        output.append(content)
        output.append(f"\n📌 可溯源引用: {source}  ->  {citation} (offset: {start_index})")
    
    return "\n".join(output)

def interactive_mode(vectorstore, filter_dict=None):
    """交互模式"""
    print("\n" + "=" * 60)
    print("投资大师知识库 - 交互查询模式")
    if filter_dict:
        print(f"活动过滤器: {filter_dict}")
    print("输入问题进行查询，输入 'quit' 退出")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n🔍 你的问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break
        
        if query.lower() in ["quit", "exit", "q"]:
            print("再见!")
            break
        
        if not query:
            continue
        
        results = query_vectorstore(vectorstore, query, filter_dict=filter_dict)
        print(format_results(results))

def main():
    parser = argparse.ArgumentParser(description="Investment Masters RAG Query")
    parser.add_argument("query", nargs="?", help="查询问题")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--persist", "-p", help="向量存储持久化目录")
    parser.add_argument("--load", "-l", help="加载已保存的向量存储目录")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="返回结果数量")
    parser.add_argument("--rules-only", action="store_true", help="仅加载决策规则")
    parser.add_argument("--investor", "-inv", help="按投资者 ID 过滤")
    parser.add_argument("--source-type", "-t", choices=["investor_doc", "rule"], help="按来源类型过滤")
    parser.add_argument("--kind", "-knd", choices=["entry", "exit", "risk_management", "other"], help="按规则类型过滤")
    parser.add_argument("--chunk-size", type=int, default=900, help="分块大小")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="分块重叠")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    
    args = parser.parse_args()
    check_dependencies()

    filter_dict = {}
    if args.investor: filter_dict["investor_id"] = args.investor
    if args.source_type: filter_dict["source_type"] = args.source_type
    if args.kind: filter_dict["kind"] = args.kind
    if not filter_dict: filter_dict = None

    if args.load:
        vectorstore = load_vectorstore(args.load)
    else:
        if args.rules_only:
            documents = load_decision_rules()
        else:
            investor_docs = load_investor_documents()
            investor_docs = split_investor_documents(investor_docs, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
            rule_docs = load_decision_rules()
            documents = investor_docs + rule_docs
        vectorstore = create_vectorstore(documents, args.persist)
    
    if args.interactive:
        interactive_mode(vectorstore, filter_dict=filter_dict)
    elif args.query:
        results = query_vectorstore(vectorstore, args.query, args.top_k, filter_dict=filter_dict)
        if args.format == "json":
            import json
            json_results = [{"content": d.page_content, "metadata": d.metadata, "similarity": round(1-s, 4)} for d, s in results]
            print(json.dumps(json_results, ensure_ascii=False, indent=2))
        else:
            print(format_results(results))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
