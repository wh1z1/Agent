"""
Agent 编排器 — 协调 5 个 Agent 的流水线执行
"""
import uuid
import asyncio
from datetime import datetime
from models import *
from agents.trend_hunter import TrendHunterAgent
from agents.supply_chain import SupplyChainAgent
from agents.content_factory import ContentFactoryAgent
from agents.listing import ListingAgent
from agents.data_dashboard import DataDashboardAgent


class PipelineOrchestrator:
    """编排器：协调5个Agent按流水线执行"""

    def __init__(self):
        self.trend_hunter = TrendHunterAgent()
        self.supply_chain = SupplyChainAgent()
        self.content_factory = ContentFactoryAgent()
        self.listing_agent = ListingAgent()
        self.data_dashboard = DataDashboardAgent()
        self.current_run: PipelineRun | None = None

    def _log(self, msg: str):
        if self.current_run:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.current_run.logs.append(f"[{timestamp}] {msg}")

    async def run_full_pipeline(self, top_n: int = 3) -> PipelineRun:
        """执行完整的选品→上架流水线"""
        run = PipelineRun(id=f"run_{uuid.uuid4().hex[:8]}")
        run.status = TaskStatus.RUNNING
        run.current_step = "趋势分析"
        self.current_run = run

        try:
            # Step 1: 趋势猎手 — 发现潜力选品
            self._log("🔍 Step 1/5: 趋势猎手启动 — 扫描全网热搜...")
            run.trend_picks = await self.trend_hunter.scan_trends(top_n=top_n)
            self._log(f"✅ 发现 {len(run.trend_picks)} 个潜力选品")

            # Step 2: 供应链 — 为每个选品找供应商
            run.current_step = "供应链匹配"
            self._log("🏭 Step 2/5: 供应链 Agent 启动 — 寻找最优供应商...")
            for pick in run.trend_picks:
                quote = await self.supply_chain.find_suppliers(pick)
                run.supply_quotes.append(quote)
                best = next(
                    (s for s in quote.suppliers if s.id == quote.best_supplier_id),
                    quote.suppliers[0]
                )
                self._log(f"  → {pick.name}: 最优供应商 {best.name} (¥{best.price})")

            # Step 3: 内容工厂 — 生成营销素材
            run.current_step = "内容生成"
            self._log("✍️ Step 3/5: 内容工厂启动 — 生成全套营销素材...")
            for i, pick in enumerate(run.trend_picks):
                quote = run.supply_quotes[i]
                content = await self.content_factory.generate_content(pick, quote)
                run.contents.append(content)
                self._log(f"  → {pick.name}: 生成{len(content.titles)}套标题 + 详情页 + 视频脚本")

            # Step 4: 上架运营 — 多平台发布
            run.current_step = "商品上架"
            self._log("🚀 Step 4/5: 上架运营 Agent 启动 — 多平台发布...")
            for i, pick in enumerate(run.trend_picks):
                quote = run.supply_quotes[i]
                content = run.contents[i]
                listings = await self.listing_agent.publish_to_platforms(pick, quote, content)
                run.listings.extend(listings)
                platforms = [l.platform.value for l in listings]
                self._log(f"  → {pick.name}: 已发布到 {', '.join(platforms)}")

            # Step 5: 数据驾驶舱 — 初始数据监控
            run.current_step = "数据监控"
            self._log("📊 Step 5/5: 数据驾驶舱启动 — 初始化监控...")
            report = await self.data_dashboard.generate_daily_report(run.trend_picks)
            self._log(f"  → 今日总营收: ¥{report.total_revenue}, 订单: {report.total_orders}")
            if report.alerts:
                for alert in report.alerts:
                    self._log(f"  → {alert}")
            if report.auto_actions_taken:
                self._log(f"  → 自动执行了 {len(report.auto_actions_taken)} 个优化动作")

            run.status = TaskStatus.COMPLETED
            run.completed_at = datetime.now()
            run.current_step = "完成"
            self._log("🎉 全部流程执行完毕！")

        except Exception as e:
            run.status = TaskStatus.FAILED
            self._log(f"❌ 执行出错: {str(e)}")

        return run

    async def run_single_step(self, step: str, **kwargs) -> dict:
        """单独执行某个步骤"""
        if step == "trend":
            picks = await self.trend_hunter.scan_trends(top_n=kwargs.get("top_n", 5))
            return {"picks": [p.model_dump() for p in picks]}

        elif step == "supply":
            product = ProductPick(**kwargs["product"])
            quote = await self.supply_chain.find_suppliers(product)
            return {"quote": quote.model_dump()}

        elif step == "content":
            product = ProductPick(**kwargs["product"])
            quote = SupplyQuote(**kwargs["quote"])
            content = await self.content_factory.generate_content(product, quote)
            return {"content": content.model_dump()}

        elif step == "listing":
            product = ProductPick(**kwargs["product"])
            quote = SupplyQuote(**kwargs["quote"])
            content = ProductContent(**kwargs["content"])
            listings = await self.listing_agent.publish_to_platforms(product, quote, content)
            return {"listings": [l.model_dump() for l in listings]}

        elif step == "dashboard":
            products = [ProductPick(**p) for p in kwargs["products"]]
            report = await self.data_dashboard.generate_daily_report(products)
            return {"report": report.model_dump()}

        return {"error": f"Unknown step: {step}"}
