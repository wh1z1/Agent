"""
Agent 1: 趋势猎手 — 扫描全网热搜，发现潜力选品
"""
import random
from datetime import datetime
from models import *
from mock_data import TREND_POOL


class TrendHunterAgent:
    """趋势猎手 Agent：扫描小红书/抖音/亚马逊等平台，发现潜力爆款"""

    def __init__(self):
        self.name = "🔍 趋势猎手"
        self.status = "idle"

    async def scan_trends(self, top_n: int = 5) -> list[ProductPick]:
        """扫描全网趋势，返回 Top N 选品推荐"""
        self.status = "scanning"
        logs = []

        # 模拟扫描多个平台
        sources = [TrendSource.XIAOHONGSHU, TrendSource.DOUYIN,
                   TrendSource.AMAZON, TrendSource.GOOGLE_TRENDS, TrendSource.TIKTOK]

        for source in sources:
            logs.append(f"[{self.name}] 正在扫描 {source.value} ...")

        # 从趋势池中选取并评分
        picks = []
        for item in TREND_POOL:
            # 综合评分算法
            score = self._calculate_score(item)
            pick = ProductPick(
                id=f"pick_{random.randint(1000, 9999)}",
                name=item["keyword"],
                category=item["category"],
                trend=TrendItem(
                    id=f"trend_{random.randint(1000, 9999)}",
                    keyword=item["keyword"],
                    source=item["source"],
                    heat_score=item["heat"],
                    growth_rate=item["growth"],
                    competition_level=item["competition"],
                    reason=item["reason"],
                ),
                estimated_price_range=item["price_range"],
                profit_margin_estimate=item["margin"],
                risk_level=item["risk"],
                score=score,
            )
            picks.append(pick)

        # 按评分排序，取 Top N
        picks.sort(key=lambda x: x.score, reverse=True)
        top_picks = picks[:top_n]

        for pick in top_picks:
            logs.append(
                f"[{self.name}] ✅ 发现潜力品: {pick.name} "
                f"(评分:{pick.score} 热度:{pick.trend.heat_score} "
                f"增长:{pick.trend.growth_rate}%)"
            )

        self.status = "idle"
        return top_picks

    def _calculate_score(self, item: dict) -> float:
        """综合评分：热度 × 40% + 增长率 × 30% + 竞争度 × 20% + 利润率 × 10%"""
        heat_score = item["heat"] / 100 * 40

        # 增长率标准化（最高300%为满分）
        growth_norm = min(item["growth"] / 300, 1.0) * 30

        # 竞争度反向评分（low > medium > high）
        comp_map = {"low": 20, "medium": 12, "high": 5}
        comp_score = comp_map.get(item["competition"], 10)

        # 利润率估算
        margin_str = item["margin"].split("-")[1].replace("%", "")
        margin_score = float(margin_str) / 100 * 10

        total = heat_score + growth_norm + comp_score + margin_score
        return round(min(total, 100), 1)
