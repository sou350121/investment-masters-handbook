"""
Investment Masters Handbook - 精簡反饋閉環系統

設計理念:
1. 輕量級：基於 JSON 文件存儲，無需數據庫
2. 實用：聚焦核心功能 (評分 + 點贊/倒讚)
3. 簡單：NPS 計算 + 基本統計

核心組件:
1. FeedbackCollector: 反饋收集
2. FeedbackAnalyzer: 反饋分析 (NPS + 統計)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import random


# ============================================
# 反饋收集器
# ============================================
class FeedbackCollector:
    """
    反饋收集器 - 收集用戶對投資建議的評分和反饋
    """
    
    def __init__(self, storage_dir: str = ".feedback"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.storage_dir / "feedback.json"
        
        if not self.feedback_file.exists():
            self._init_storage()
    
    def _init_storage(self):
        """初始化存儲文件"""
        data = {"feedback_records": [], "metadata": {"created_at": datetime.now().isoformat()}}
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def submit_feedback(
        self,
        session_id: str,
        query: str,
        response_id: str,
        feedback_type: str,  # "thumbs_up", "thumbs_down", "rating"
        rating: Optional[int] = None,  # 1-5 分
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        提交反饋
        
        Args:
            session_id: 會話 ID
            query: 用戶查詢
            response_id: 回應 ID
            feedback_type: 反饋類型 (thumbs_up/thumbs_down/rating)
            rating: 評分 (1-5, 僅當 feedback_type="rating" 時需要)
            comment: 評論 (可選)
        
        Returns:
            反饋記錄
        """
        # 驗證評分
        if feedback_type == "rating" and rating:
            if not 1 <= rating <= 5:
                raise ValueError("評分必須在 1-5 之間")
        
        # 創建記錄
        record = {
            "id": f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "session_id": session_id,
            "query": query,
            "response_id": response_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        self._save_record(record)
        print(f"✅ 反饋已保存：{record['id']}")
        return record
    
    def _save_record(self, record: Dict[str, Any]):
        """保存記錄到文件"""
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data["feedback_records"].append(record)
        
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_recent_feedback(self, days: int = 7) -> List[Dict[str, Any]]:
        """獲取最近的反饋"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = []
        for record_data in data["feedback_records"]:
            record_time = datetime.fromisoformat(record_data["timestamp"])
            if record_time >= cutoff_date:
                records.append(record_data)
        
        return records
    
    def clear_feedback(self):
        """清空所有反饋"""
        self._init_storage()
        print("✅ 反饋數據已清空")


# ============================================
# 反饋分析器
# ============================================
class FeedbackAnalyzer:
    """
    反饋分析器 - 計算 NPS 和基本統計
    """
    
    def __init__(self, collector: FeedbackCollector):
        self.collector = collector
    
    def analyze(self, days: int = 7) -> Dict[str, Any]:
        """
        分析反饋數據
        
        Args:
            days: 分析天數
        
        Returns:
            統計數據字典
        """
        records = self.collector.get_recent_feedback(days)
        
        if not records:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "nps": 0.0,
                "thumbs_up_ratio": 0.0,
                "total_thumbs_up": 0,
                "total_thumbs_down": 0
            }
        
        total = len(records)
        
        # 點贊/倒讚
        thumbs_up = sum(1 for r in records if r["feedback_type"] == "thumbs_up")
        thumbs_down = sum(1 for r in records if r["feedback_type"] == "thumbs_down")
        thumbs_up_ratio = thumbs_up / total if total > 0 else 0.0
        
        # 評分
        ratings = [r["rating"] for r in records if r["feedback_type"] == "rating" and r["rating"]]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # NPS (Net Promoter Score)
        # 5 星=10 分，4 星=9 分，3 星=7-8 分，2 星=5-6 分，1 星=0-6 分
        promoters = sum(1 for r in ratings if r >= 4)  # 4-5 星
        detractors = sum(1 for r in ratings if r <= 2)  # 1-2 星
        nps = ((promoters - detractors) / len(ratings) * 100) if ratings else 0.0
        
        return {
            "total_feedback": total,
            "average_rating": round(avg_rating, 2),
            "nps": round(nps, 1),
            "thumbs_up_ratio": round(thumbs_up_ratio, 3),
            "total_thumbs_up": thumbs_up,
            "total_thumbs_down": thumbs_down
        }
    
    def generate_report(self, days: int = 7) -> str:
        """生成簡易報告"""
        stats = self.analyze(days)
        
        report = []
        report.append("=" * 60)
        report.append("📊 反饋分析報告 (最近 {} 天)".format(days))
        report.append("=" * 60)
        report.append(f"\n總反饋數：{stats['total_feedback']}")
        report.append(f"平均評分：{stats['average_rating']:.2f}/5.0")
        report.append(f"點贊率：{stats['thumbs_up_ratio']:.1%}")
        report.append(f"NPS: {stats['nps']:.1f}")
        report.append(f"\n👍 點贊：{stats['total_thumbs_up']}")
        report.append(f"👎 倒讚：{stats['total_thumbs_down']}")
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


# ============================================
# 使用示例
# ============================================
if __name__ == "__main__":
    print("\n🔄 反饋閉環系統 Toy Example\n")
    
    # 1. 創建收集器
    collector = FeedbackCollector()
    
    # 2. 創建分析器
    analyzer = FeedbackAnalyzer(collector)
    
    # 3. 模擬提交反饋
    print("📝 模擬提交反饋...\n")
    
    sample_feedback = [
        {
            "session_id": "session_001",
            "query": "如何評估當前市場估值？",
            "response_id": "resp_001",
            "feedback_type": "rating",
            "rating": 5,
            "comment": "非常詳細，很有幫助"
        },
        {
            "session_id": "session_002",
            "query": "現在應該買入還是賣出？",
            "response_id": "resp_002",
            "feedback_type": "thumbs_up"
        },
        {
            "session_id": "session_003",
            "query": "通膨對投資有什麼影響？",
            "response_id": "resp_003",
            "feedback_type": "rating",
            "rating": 4,
            "comment": "不錯，但希望可以更具體"
        },
        {
            "session_id": "session_004",
            "query": "如何配置資產？",
            "response_id": "resp_004",
            "feedback_type": "thumbs_down",
            "comment": "回答太模糊"
        },
        {
            "session_id": "session_005",
            "query": "VIX 是什麼意思？",
            "response_id": "resp_005",
            "feedback_type": "rating",
            "rating": 5,
            "comment": "解釋很清楚"
        }
    ]
    
    for fb in sample_feedback:
        collector.submit_feedback(**fb)
    
    # 4. 分析反饋
    print("\n📊 分析反饋數據:\n")
    stats = analyzer.analyze(days=7)
    
    print(f"總反饋數：{stats['total_feedback']}")
    print(f"平均評分：{stats['average_rating']:.2f}/5.0")
    print(f"NPS: {stats['nps']:.1f}")
    print(f"點贊率：{stats['thumbs_up_ratio']:.1%}")
    
    # 5. 生成報告
    print("\n" + "=" * 60)
    report = analyzer.generate_report(days=7)
    print(report)
    
    print("\n✅ 反饋閉環系統 Toy Example 完成!\n")
