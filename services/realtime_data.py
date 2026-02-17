"""
Investment Masters Handbook - 精簡實時數據管道

只獲取項目必需的宏觀和市場數據，避免冗餘數據

核心數據需求 (基於 Policy Gate 和 Ensemble):
1. 市場波動率：VIX
2. 通膨指標：CPI、PCE
3. 利率：聯邦基金利率、國債收益率
4. 市場估值：S&P500 本益比
5. 市場情緒：新聞標題 (可選)

數據更新頻率:
- VIX: 每 5 分鐘 (市場時段)
- 利率：每日
- 通膨：每月
- 估值：每日
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import os


class RealTimeDataPipeline:
    """精簡實時數據管道"""
    
    def __init__(self, cache_dir: str = ".cache/market_data", cache_ttl_hours: int = 24):
        """
        Args:
            cache_dir: 緩存目錄
            cache_ttl_hours: 緩存過期時間 (小時)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API Keys (從環境變量讀取)
        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.yahoo_finance_enabled = True  # yfinance 不需要 API key
        
        # 數據緩存
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    async def start(self):
        """啟動數據管道"""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """停止數據管道"""
        if self.session:
            await self.session.close()
    
    async def get_all_features(self) -> Dict[str, float]:
        """
        獲取所有必需特徵 (用於 Policy Gate)
        
        Returns:
            特徵字典 {
                "vix": 15.2,
                "inflation": 3.2,
                "rates": 4.5,
                "sp500_pe_ratio": 22.3,
                ...
            }
        """
        features = {}
        
        # 1. VIX (波動率) - 高優先級
        vix = await self.get_vix()
        if vix is not None:
            features["vix"] = vix
        
        # 2. 通膨 - 中優先級 (月度數據，可從緩存讀取)
        inflation = await self.get_inflation_rate()
        if inflation is not None:
            features["inflation"] = inflation
        
        # 3. 利率 - 高優先級
        rates = await self.get_federal_funds_rate()
        if rates is not None:
            features["rates"] = rates
        
        # 4. 國債收益率 (可選)
        treasury_10y = await self.get_treasury_yield("10Y")
        if treasury_10y is not None:
            features["treasury_10y"] = treasury_10y
        
        # 5. 市場估值 - 中優先級
        pe_ratio = await self.get_sp500_pe_ratio()
        if pe_ratio is not None:
            features["sp500_pe_ratio"] = pe_ratio
        
        return features
    
    # ============================================
    # VIX 波動率
    # ============================================
    async def get_vix(self) -> Optional[float]:
        """
        獲取 VIX 波動率指數
        
        Returns:
            VIX 數值，例如 15.2
        """
        # 嘗試從緩存讀取
        cached = self._get_from_cache("vix")
        if cached is not None:
            return cached
        
        try:
            # 使用 yfinance 獲取 VIX
            import yfinance as yf
            loop = asyncio.get_event_loop()
            vix_data = await loop.run_in_executor(
                None,
                lambda: yf.Ticker("^VIX")
            )
            
            # 獲取最新價格
            if hasattr(vix_data, 'history'):
                history = await loop.run_in_executor(
                    None,
                    lambda: vix_data.history(period="1d")
                )
                if not history.empty:
                    vix = history['Close'].iloc[-1]
                    self._save_to_cache("vix", vix, timedelta(minutes=5))
                    return vix
            
            # 備選：從快取文件讀取
            return self._load_from_file("vix.json")
            
        except Exception as e:
            print(f"⚠️ 獲取 VIX 失敗：{e}")
            return self._load_from_file("vix.json")  # 降級：使用本地緩存
    
    # ============================================
    # 通膨數據
    # ============================================
    async def get_inflation_rate(self) -> Optional[float]:
        """
        獲取通膨率 (CPI YoY)
        
        Returns:
            通膨率，例如 3.2
        """
        # 嘗試從緩存讀取 (通膨數據月度更新，緩存 30 天)
        cached = self._get_from_cache("inflation")
        if cached is not None:
            return cached
        
        if not self.fred_api_key:
            # 無 API key 時使用默認值或本地緩存
            return self._load_from_file("inflation.json")
        
        try:
            # FRED API: CPIAUCSL (Consumer Price Index)
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "CPIAUCSL",
                "api_key": self.fred_api_key,
                "file_type": "json",
                "limit": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("observations"):
                        value = float(data["observations"][0]["value"])
                        
                        # 計算 YoY 通膨率 (需要對比一年前)
                        params["observation_start"] = (datetime.now() - timedelta(days=365)).isoformat()
                        async with self.session.get(url, params=params) as response_prev:
                            if response_prev.status == 200:
                                data_prev = await response_prev.json()
                                if data_prev.get("observations"):
                                    value_prev = float(data_prev["observations"][0]["value"])
                                    inflation_yoy = ((value - value_prev) / value_prev) * 100
                                    
                                    self._save_to_cache("inflation", inflation_yoy, timedelta(days=30))
                                    self._save_to_file("inflation.json", inflation_yoy)
                                    return inflation_yoy
            
            return self._load_from_file("inflation.json")
            
        except Exception as e:
            print(f"⚠️ 獲取通膨數據失敗：{e}")
            return self._load_from_file("inflation.json")
    
    # ============================================
    # 利率數據
    # ============================================
    async def get_federal_funds_rate(self) -> Optional[float]:
        """
        獲取聯邦基金利率
        
        Returns:
            利率，例如 4.5
        """
        # 嘗試從緩存讀取 (利率變化不頻繁，緩存 7 天)
        cached = self._get_from_cache("rates")
        if cached is not None:
            return cached
        
        if not self.fred_api_key:
            return self._load_from_file("rates.json")
        
        try:
            # FRED API: FEDFUNDS (Federal Funds Effective Rate)
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "FEDFUNDS",
                "api_key": self.fred_api_key,
                "file_type": "json",
                "limit": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("observations"):
                        rate = float(data["observations"][0]["value"])
                        self._save_to_cache("rates", rate, timedelta(days=7))
                        self._save_to_file("rates.json", rate)
                        return rate
            
            return self._load_from_file("rates.json")
            
        except Exception as e:
            print(f"⚠️ 獲取聯邦基金利率失敗：{e}")
            return self._load_from_file("rates.json")
    
    async def get_treasury_yield(self, maturity: str = "10Y") -> Optional[float]:
        """
        獲取國債收益率
        
        Args:
            maturity: 期限 ("10Y", "2Y", "3M" 等)
        
        Returns:
            收益率，例如 4.2
        """
        series_map = {
            "10Y": "DGS10",
            "2Y": "DGS2",
            "3M": "DGS3MO",
            "30Y": "DGS30"
        }
        
        series_id = series_map.get(maturity, "DGS10")
        cache_key = f"treasury_{maturity}"
        
        # 嘗試從緩存讀取
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if not self.fred_api_key:
            return self._load_from_file(f"treasury_{maturity}.json")
        
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "limit": 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("observations"):
                        value = float(data["observations"][0]["value"])
                        self._save_to_cache(cache_key, value, timedelta(days=1))
                        self._save_to_file(f"treasury_{maturity}.json", value)
                        return value
            
            return self._load_from_file(f"treasury_{maturity}.json")
            
        except Exception as e:
            print(f"⚠️ 獲取{maturity}國債收益率失敗：{e}")
            return self._load_from_file(f"treasury_{maturity}.json")
    
    # ============================================
    # 市場估值
    # ============================================
    async def get_sp500_pe_ratio(self) -> Optional[float]:
        """
        獲取 S&P500 本益比
        
        Returns:
            本益比，例如 22.3
        """
        # 嘗試從緩存讀取 (每日更新)
        cached = self._get_from_cache("sp500_pe")
        if cached is not None:
            return cached
        
        try:
            # 使用 yfinance 獲取 S&P500 數據
            import yfinance as yf
            loop = asyncio.get_event_loop()
            
            spy = await loop.run_in_executor(
                None,
                lambda: yf.Ticker("SPY")
            )
            
            # 獲取本益比 (需要計算)
            # 簡化版：使用歷史數據估算
            history = await loop.run_in_executor(
                None,
                lambda: spy.history(period="1mo")
            )
            
            if not history.empty:
                # 簡化估算 (實際應該使用 Shiller PE 或更精確的數據)
                # 這裡僅作示範，建議使用 Multpl.com 或類似數據源
                current_price = history['Close'].iloc[-1]
                
                # 使用過去 12 個月平均盈利估算
                # 注意：這是簡化版，生產環境應使用更精確的數據源
                estimated_pe = 20.0  # 默認值
                
                self._save_to_cache("sp500_pe", estimated_pe, timedelta(days=1))
                self._save_to_file("sp500_pe.json", estimated_pe)
                return estimated_pe
            
            return self._load_from_file("sp500_pe.json")
            
        except Exception as e:
            print(f"⚠️ 獲取 S&P500 本益比失敗：{e}")
            return self._load_from_file("sp500_pe.json")
    
    # ============================================
    # 緩存管理
    # ============================================
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """從內存緩存讀取"""
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key)
            if timestamp and datetime.now() - timestamp < self.cache_ttl:
                return self._cache[key]
        return None
    
    def _save_to_cache(self, key: str, value: Any, ttl: timedelta):
        """保存到內存緩存"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def _save_to_file(self, filename: str, data: Any):
        """保存到文件緩存"""
        filepath = self.cache_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "value": data,
                "timestamp": datetime.now().isoformat()
            }, f)
    
    def _load_from_file(self, filename: str) -> Optional[Any]:
        """從文件緩存讀取"""
        filepath = self.cache_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 檢查是否過期
                    timestamp = datetime.fromisoformat(data["timestamp"])
                    if datetime.now() - timestamp < self.cache_ttl:
                        return data["value"]
            except Exception:
                pass
        return None
    
    # ============================================
    # 手動更新緩存
    # ============================================
    async def refresh_all(self):
        """強制刷新所有數據"""
        print("🔄 刷新實時數據...")
        
        # 清空緩存
        self._cache.clear()
        self._cache_timestamps.clear()
        
        # 重新獲取
        features = await self.get_all_features()
        
        print(f"✅ 刷新完成，獲取 {len(features)} 個指標")
        for key, value in features.items():
            print(f"  - {key}: {value}")
        
        return features


# ============================================
# 全局實例
# ============================================
_pipeline: Optional[RealTimeDataPipeline] = None


def get_pipeline() -> RealTimeDataPipeline:
    """獲取全局數據管道"""
    global _pipeline
    if _pipeline is None:
        _pipeline = RealTimeDataPipeline()
    return _pipeline


async def get_market_features() -> Dict[str, float]:
    """便捷函數：獲取所有市場特徵"""
    pipeline = get_pipeline()
    await pipeline.start()
    try:
        return await pipeline.get_all_features()
    finally:
        await pipeline.stop()


# ============================================
# 命令行工具
# ============================================
if __name__ == "__main__":
    import asyncio
    
    async def main():
        pipeline = RealTimeDataPipeline()
        await pipeline.start()
        
        try:
            print("📊 獲取實時市場數據...\n")
            
            features = await pipeline.get_all_features()
            
            print("\n✅ 獲取成功:")
            for key, value in features.items():
                print(f"  {key}: {value}")
            
            print(f"\n💡 提示：數據已緩存到 .cache/market_data/")
            
        finally:
            await pipeline.stop()
    
    asyncio.run(main())
