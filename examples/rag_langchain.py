#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investment Masters RAG Integration Example

使用 LangChain + ChromaDB 实现投资大师知识库的 RAG 检索。

Requirements:
    pip install langchain langchain-community chromadb pyyaml sentence-transformers

Usage:
    python rag_langchain.py "这个股票值得买吗？"
    python rag_langchain.py --interactive
    python rag_langchain.py --persist ./vectorstore "护城河分析"
    python rag_langchain.py --load ./vectorstore "巴菲特如何选股？"
    python rag_langchain.py "止损" --kind risk_management
    python rag_langchain.py "护城河" --investor warren_buffett
"""

import argparse
import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def check_dependencies():
    """检查依赖是否安装"""
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

    # HuggingFaceEmbeddings 默认依赖 sentence-transformers
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        missing.append("sentence-transformers")
    
    if missing:
        print("缺少依赖，请安装:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def load_investor_documents():
    """加载投资者文档为 LangChain Document 格式"""
    from langchain.schema import Document
    import yaml
    
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
    """
    将投资者长文档分块，提升检索精度，并为每个块附加引用信息。

    - 保留原 metadata（source/investor_id 等）
    - 增加 chunk_index/chunk_id/title_hint/source_type
    - 记录 start_index 用于精确溯源
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    import re

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
    import json
    
    rules_file = PROJECT_ROOT / "config" / "decision_rules.generated.json"
    
    if not rules_file.exists():
        print(f"规则文件不存在: {rules_file}")
        return []
    
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    for rule in data.get("rules", []):
        # 将规则转为自然语言
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


def create_vectorstore(documents, persist_dir=None):
    """创建向量存储"""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    
    # 使用免费的本地 embedding 模型
    # 如果有 OpenAI API key，可以改用 OpenAIEmbeddings
    print("加载 embedding 模型...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    
    print(f"创建向量存储，共 {len(documents)} 个文档...")
    
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
    """从持久化目录加载向量存储（需与创建时使用同一 embedding 配置）"""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )


def query_vectorstore(vectorstore, query: str, k: int = 5, filter_dict: dict = None):
    """查询向量存储，支持元数据过滤"""
    # Chroma 过滤语法：{"metadata_key": "value"} 或 {"$and": [...]}
    results = vectorstore.similarity_search_with_score(
        query, 
        k=k,
        filter=filter_dict
    )
    return results


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

        # 引用：优先 rule_id，其次 chunk_id
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
        
        # 截取内容预览
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
    parser = argparse.ArgumentParser(
        description="Investment Masters RAG Query",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "这个股票值得买吗？"
  %(prog)s "市场恐慌时该怎么办？"
  %(prog)s --interactive
  %(prog)s --persist ./vectorstore "护城河分析"
  %(prog)s --load ./vectorstore "芒格的决策清单"
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="查询问题"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="交互模式"
    )
    parser.add_argument(
        "--persist", "-p",
        help="向量存储持久化目录"
    )
    parser.add_argument(
        "--load", "-l",
        help="加载已保存的向量存储目录（更快）"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="返回结果数量（默认: 5）"
    )
    parser.add_argument(
        "--rules-only",
        action="store_true",
        help="仅加载决策规则（更快）"
    )
    parser.add_argument(
        "--investor", "-inv",
        help="按投资者 ID 过滤 (例如: warren_buffett)"
    )
    parser.add_argument(
        "--source-type", "-t",
        choices=["investor_doc", "rule"],
        help="按来源类型过滤"
    )
    parser.add_argument(
        "--kind", "-knd",
        choices=["entry", "exit", "risk_management", "other"],
        help="按规则类型过滤 (仅对 rule 类型有效)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=900,
        help="投资者文档分块大小 (默认: 900)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="分块重叠大小 (默认: 200)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)"
    )
    
    args = parser.parse_args()
    
    # 检查依赖
    check_dependencies()

    # 构建过滤器
    filter_dict = {}
    if args.investor:
        filter_dict["investor_id"] = args.investor
    if args.source_type:
        filter_dict["source_type"] = args.source_type
    if args.kind:
        filter_dict["kind"] = args.kind
    
    if not filter_dict:
        filter_dict = None

    # 加载或创建向量存储
    if args.load:
        load_dir = Path(args.load)
        if not load_dir.exists():
            print(f"向量库目录不存在: {load_dir}")
            print("提示：首次运行请使用 --persist ./vectorstore 先创建向量库")
            sys.exit(1)

        print(f"加载向量存储: {load_dir}")
        vectorstore = load_vectorstore(str(load_dir))
        print("向量存储加载完成!")
    else:
        # 加载文档
        print("加载文档...")

        if args.rules_only:
            documents = load_decision_rules()
            print(f"已加载 {len(documents)} 条决策规则")
        else:
            investor_docs = load_investor_documents()
            investor_docs = split_investor_documents(
                investor_docs, 
                chunk_size=args.chunk_size, 
                chunk_overlap=args.chunk_overlap
            )
            rule_docs = load_decision_rules()
            documents = investor_docs + rule_docs
            print(f"已加载 {len(investor_docs)} 个投资者文档分块 + {len(rule_docs)} 条决策规则")

        # 创建向量存储
        vectorstore = create_vectorstore(documents, args.persist)
        print("向量存储创建完成!")
    
    # 执行查询
    if args.interactive:
        interactive_mode(vectorstore, filter_dict=filter_dict)
    elif args.query:
        results = query_vectorstore(vectorstore, args.query, args.top_k, filter_dict=filter_dict)
        
        if args.format == "json":
            import json
            json_results = []
            for doc, score in results:
                res = doc.metadata.copy()
                res["content"] = doc.page_content
                res["similarity_estimate"] = round(1 - score, 4)
                json_results.append(res)
            print(json.dumps(json_results, ensure_ascii=False, indent=2))
        else:
            print(format_results(results))
    else:
        parser.print_help()


# === 简化版本（无需安装额外依赖）===

def simple_keyword_search(query: str):
    """
    简化版关键词搜索（无需安装 LangChain）
    
    Usage:
        from rag_langchain import simple_keyword_search
        results = simple_keyword_search("护城河")
    """
    import json
    import re
    
    # 加载规则
    rules_file = PROJECT_ROOT / "config" / "decision_rules.generated.json"
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = []
    query_lower = query.lower()
    
    for rule in data.get("rules", []):
        when = rule.get("when", "").lower()
        then = rule.get("then", "").lower()
        because = (rule.get("because") or "").lower()
        
        # 简单关键词匹配
        if query_lower in when or query_lower in then or query_lower in because:
            results.append(rule)
    
    return results


if __name__ == "__main__":
    main()


