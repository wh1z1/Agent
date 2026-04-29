"""
AI 选品官 — 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TrendSource(str, Enum):
    XIAOHONGSHU = "xiaohongshu"
    DOUYIN = "douyin"
    AMAZON = "amazon"
    GOOGLE_TRENDS = "google_trends"
    TIKTOK = "tiktok"


class Platform(str, Enum):
    TAOBAO = "taobao"
    PINDUODUO = "pinduoduo"
    DOUYIN_SHOP = "douyin_shop"
    TEMU = "temu"
    SHEIN = "shein"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ── 趋势猎手 ──────────────────────────────
class TrendItem(BaseModel):
    id: str
    keyword: str
    source: TrendSource
    heat_score: float = Field(ge=0, le=100, description="热度评分 0-100")
    growth_rate: float = Field(description="增长率 %")
    competition_level: str = Field(description="low/medium/high")
    reason: str = Field(description="推荐理由")
    discovered_at: datetime = Field(default_factory=datetime.now)


class ProductPick(BaseModel):
    id: str
    name: str
    category: str
    trend: TrendItem
    estimated_price_range: str
    profit_margin_estimate: str
    risk_level: str  # low/medium/high
    score: float = Field(ge=0, le=100, description="综合评分")
    status: TaskStatus = TaskStatus.PENDING


# ── 供应链 ──────────────────────────────
class Supplier(BaseModel):
    id: str
    name: str
    platform: str = "1688"
    price: float
    moq: int = Field(description="最小起订量")
    rating: float = Field(ge=0, le=5)
    response_time_hours: float
    location: str
    verified: bool = False


class SupplyQuote(BaseModel):
    product_id: str
    suppliers: list[Supplier]
    best_supplier_id: str
    negotiation_notes: str
    total_cost_estimate: float


# ── 内容工厂 ──────────────────────────────
class ProductContent(BaseModel):
    product_id: str
    titles: list[str] = Field(description="5套标题方案")
    description: str = Field(description="详情页文案")
    bullet_points: list[str] = Field(description="卖点列表")
    video_script_30s: str = Field(description="30秒口播脚本")
    image_prompts: list[str] = Field(description="主图生成提示词")
    seo_keywords: list[str]


# ── 上架运营 ──────────────────────────────
class ListingConfig(BaseModel):
    product_id: str
    platform: Platform
    title: str
    price: float
    coupon_config: Optional[dict] = None
    promotion_config: Optional[dict] = None
    status: TaskStatus = TaskStatus.PENDING
    listing_url: Optional[str] = None


# ── 数据驾驶舱 ──────────────────────────────
class DailyMetrics(BaseModel):
    product_id: str
    date: str
    impressions: int = 0
    clicks: int = 0
    orders: int = 0
    revenue: float = 0.0
    cost: float = 0.0
    roi: float = 0.0
    conversion_rate: float = 0.0
    return_rate: float = 0.0
    avg_rating: float = 0.0
    review_count: int = 0


class AutoAction(BaseModel):
    product_id: str
    action_type: str  # "change_image", "adjust_price", "update_detail", "pause_ad", "restock"
    reason: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.now)
    result: Optional[str] = None


class DailyReport(BaseModel):
    date: str
    total_products: int
    total_revenue: float
    total_orders: int
    avg_roi: float
    top_product: Optional[str] = None
    alerts: list[str] = []
    auto_actions_taken: list[AutoAction] = []


# ── 流水线 ──────────────────────────────
class PipelineRun(BaseModel):
    id: str
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    current_step: str = ""
    trend_picks: list[ProductPick] = []
    supply_quotes: list[SupplyQuote] = []
    contents: list[ProductContent] = []
    listings: list[ListingConfig] = []
    metrics: list[DailyMetrics] = []
    logs: list[str] = []
