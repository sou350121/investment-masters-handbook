#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investment Masters Rule Query Engine

根据场景、投资者、关键词查询匹配的 IF-THEN 规则。

Usage:
    python rule_query.py --scenario "市场恐慌"
    python rule_query.py --investor buffett
    python rule_query.py --keyword "护城河"
    python rule_query.py --when "估值" --then "买入"
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

# 规则文件路径
RULES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "decision_rules.generated.json"
)

# 场景到关键词的映射
SCENARIO_KEYWORDS = {
    "市场恐慌": ["恐慌", "危机", "抛售", "极低", "恐惧"],
    "市场狂热": ["狂热", "泡沫", "过热", "估值极端", "散户", "FOMO"],
    "经济衰退": ["衰退", "通缩", "违约", "去杠杆"],
    "利率转向": ["Fed", "加息", "降息", "转向", "利率"],
    "流动性收紧": ["流动性", "收紧", "TGA", "RRP"],
    "选股": ["买入", "护城河", "估值", "PEG", "ROIC", "安全边际"],
    "卖出": ["卖出", "止损", "减仓", "获利"],
    "风控": ["风险", "止损", "仓位", "回撤", "偏误"],
}

# 投资者 ID 到中文名的映射
INVESTOR_NAMES = {
    "warren_buffett": "巴菲特",
    "charlie_munger": "芒格",
    "peter_lynch": "林奇",
    "seth_klarman": "卡拉曼",
    "ray_dalio": "达利奥",
    "stanley_druckenmiller": "德鲁肯米勒",
    "george_soros": "索罗斯",
    "howard_marks": "马克斯",
    "michael_burry": "伯里",
    "james_simons": "西蒙斯",
    "ed_thorp": "索普",
    "cliff_asness": "阿斯内斯",
    "carl_icahn": "伊坎",
    "qiu_guolu": "邱国鹭",
    "feng_liu": "冯柳",
    "greg_abel": "阿贝尔",
}


def load_rules() -> List[Dict[str, Any]]:
    """加载规则文件"""
    if not os.path.exists(RULES_FILE):
        print(f"错误: 规则文件不存在: {RULES_FILE}")
        print("请先运行: python scripts/generate_artifacts.py")
        sys.exit(1)
    
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("rules", [])


def filter_by_investor(rules: List[Dict], investor: str) -> List[Dict]:
    """按投资者过滤"""
    investor_lower = investor.lower()
    return [
        r for r in rules
        if investor_lower in r.get("investor_id", "").lower()
    ]


def filter_by_keyword(rules: List[Dict], keyword: str) -> List[Dict]:
    """按关键词过滤（搜索 when/then/because 字段）"""
    keyword_lower = keyword.lower()
    results = []
    for r in rules:
        when = r.get("when", "").lower()
        then = r.get("then", "").lower()
        because = (r.get("because") or "").lower()
        
        if keyword_lower in when or keyword_lower in then or keyword_lower in because:
            results.append(r)
    
    return results


def filter_by_scenario(rules: List[Dict], scenario: str) -> List[Dict]:
    """按场景过滤（使用预定义的关键词映射）"""
    keywords = SCENARIO_KEYWORDS.get(scenario, [scenario])
    
    results = []
    for r in rules:
        when = r.get("when", "").lower()
        then = r.get("then", "").lower()
        because = (r.get("because") or "").lower()
        combined = f"{when} {then} {because}"
        
        if any(kw.lower() in combined for kw in keywords):
            results.append(r)
    
    return results


def filter_by_when_then(rules: List[Dict], when: str = None, then: str = None) -> List[Dict]:
    """按 when/then 条件过滤"""
    results = rules
    
    if when:
        results = [r for r in results if when.lower() in r.get("when", "").lower()]
    
    if then:
        results = [r for r in results if then.lower() in r.get("then", "").lower()]
    
    return results


def format_rule(rule: Dict) -> str:
    """格式化单条规则为可读字符串"""
    investor_id = rule.get("investor_id", "unknown")
    investor_name = INVESTOR_NAMES.get(investor_id, investor_id)
    
    lines = [
        f"┌─ {investor_name} ({investor_id})",
        f"│  IF   {rule.get('when', 'N/A')}",
        f"│  THEN {rule.get('then', 'N/A')}",
    ]
    
    because = rule.get("because")
    if because:
        lines.append(f"│  WHY  {because}")
    
    lines.append(f"└─ [{rule.get('kind', 'other')}] {rule.get('rule_id', 'N/A')}")
    
    return "\n".join(lines)


def output_json(rules: List[Dict]):
    """输出 JSON 格式"""
    print(json.dumps(rules, ensure_ascii=False, indent=2))


def output_text(rules: List[Dict]):
    """输出文本格式"""
    if not rules:
        print("没有找到匹配的规则。")
        return
    
    print(f"找到 {len(rules)} 条匹配规则:\n")
    print("=" * 60)
    
    for i, rule in enumerate(rules, 1):
        print(f"\n[{i}] {format_rule(rule)}")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Investment Masters Rule Query Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --scenario "市场恐慌"
  %(prog)s --investor buffett
  %(prog)s --keyword "护城河"
  %(prog)s --when "估值" --then "买入"
  %(prog)s --scenario "选股" --investor lynch --format json

可用场景:
  市场恐慌, 市场狂热, 经济衰退, 利率转向, 流动性收紧, 选股, 卖出, 风控
        """
    )
    
    parser.add_argument(
        "--scenario", "-s",
        help="场景名称（如：市场恐慌、选股、风控）"
    )
    parser.add_argument(
        "--investor", "-i",
        help="投资者 ID（如：buffett、munger、qiu_guolu）"
    )
    parser.add_argument(
        "--keyword", "-k",
        help="关键词搜索"
    )
    parser.add_argument(
        "--when", "-w",
        help="过滤 IF 条件包含的内容"
    )
    parser.add_argument(
        "--then", "-t",
        help="过滤 THEN 结果包含的内容"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式（默认: text）"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=20,
        help="最大返回数量（默认: 20）"
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="列出所有可用场景"
    )
    parser.add_argument(
        "--list-investors",
        action="store_true",
        help="列出所有投资者"
    )
    
    args = parser.parse_args()
    
    # 列出场景
    if args.list_scenarios:
        print("可用场景:")
        for scenario, keywords in SCENARIO_KEYWORDS.items():
            print(f"  {scenario}: {', '.join(keywords)}")
        return
    
    # 列出投资者
    if args.list_investors:
        print("可用投资者:")
        for investor_id, name in INVESTOR_NAMES.items():
            print(f"  {investor_id}: {name}")
        return
    
    # 至少需要一个过滤条件
    if not any([args.scenario, args.investor, args.keyword, args.when, args.then]):
        parser.print_help()
        return
    
    # 加载规则
    rules = load_rules()
    print(f"已加载 {len(rules)} 条规则\n")
    
    # 应用过滤器
    if args.scenario:
        rules = filter_by_scenario(rules, args.scenario)
        print(f"场景 '{args.scenario}' 过滤后: {len(rules)} 条")
    
    if args.investor:
        rules = filter_by_investor(rules, args.investor)
        print(f"投资者 '{args.investor}' 过滤后: {len(rules)} 条")
    
    if args.keyword:
        rules = filter_by_keyword(rules, args.keyword)
        print(f"关键词 '{args.keyword}' 过滤后: {len(rules)} 条")
    
    if args.when or args.then:
        rules = filter_by_when_then(rules, args.when, args.then)
        print(f"条件过滤后: {len(rules)} 条")
    
    # 限制数量
    if len(rules) > args.limit:
        rules = rules[:args.limit]
        print(f"限制显示前 {args.limit} 条")
    
    print()
    
    # 输出结果
    if args.format == "json":
        output_json(rules)
    else:
        output_text(rules)


if __name__ == "__main__":
    main()

