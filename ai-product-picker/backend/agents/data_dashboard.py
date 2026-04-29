"""
Agent 5: 数据驾驶舱 — 实时监控 + 自动优化
"""
import random
from datetime import datetime
from models import *
from mock_data import generate_mock_metrics


class DataDashboardAgent:
    """数据驾驶舱 Agent：监控销售数据，自动发现问题并干预"""

    def __init__(self):
        self.name = "📊 数据驾驶舱"
        self.status = "idle"

    async def generate_daily_report(self, products: list[ProductPick]) -> DailyReport:
        """生成每日运营报告"""
        self.status = "analyzing"

        total_revenue = 0
        total_orders = 0
        all_metrics = []
        alerts = []
        auto_actions = []

        for product in products:
            metrics_data = generate_mock_metrics(product.name, days=1)
            if metrics_data:
                m = metrics_data[-1]
                m["product_id"] = product.id
                total_revenue += m["revenue"]
                total_orders += m["orders"]
                all_metrics.append(DailyMetrics(**m))

                # 自动诊断
                actions = self._diagnose_and_act(product, m)
                auto_actions.extend(actions)

                # 告警检测
                if m["conversion_rate"] < 1.0:
                    alerts.append(f"⚠️ {product.name} 转化率过低({m['conversion_rate']}%)")
                if m["return_rate"] > 5:
                    alerts.append(f"🔴 {product.name} 退货率过高({m['return_rate']}%)")
                if m["avg_rating"] < 4.0:
                    alerts.append(f"⭐ {product.name} 评分偏低({m['avg_rating']})")

        # 找出最佳商品
        if all_metrics:
            best = max(all_metrics, key=lambda x: x.revenue)
            best_product = next(
                (p for p in products if p.id == best.product_id), None
            )
            top_product_name = best_product.name if best_product else "N/A"
        else:
            top_product_name = "N/A"

        avg_roi = (
            sum(m.roi for m in all_metrics) / len(all_metrics)
            if all_metrics else 0
        )

        report = DailyReport(
            date=datetime.now().strftime("%Y-%m-%d"),
            total_products=len(products),
            total_revenue=round(total_revenue, 2),
            total_orders=total_orders,
            avg_roi=round(avg_roi, 1),
            top_product=top_product_name,
            alerts=alerts,
            auto_actions_taken=auto_actions,
        )

        self.status = "idle"
        return report

    async def get_product_metrics(self, product_id: str, product_name: str, days: int = 7) -> list[DailyMetrics]:
        """获取单个商品的历史数据"""
        metrics_data = generate_mock_metrics(product_name, days)
        result = []
        for m in metrics_data:
            m["product_id"] = product_id
            result.append(DailyMetrics(**m))
        return result

    def _diagnose_and_act(self, product: ProductPick, metrics: dict) -> list[AutoAction]:
        """自动诊断问题并执行干预"""
        actions = []

        # 转化率低 → 建议换主图
        if metrics["conversion_rate"] < 2.0:
            actions.append(AutoAction(
                product_id=product.id,
                action_type="change_image",
                reason=f"转化率仅{metrics['conversion_rate']}%，低于2%阈值",
                old_value="当前主图",
                new_value="AI重新生成主图（突出使用场景）",
                result="已提交新主图，预计2小时内生效",
            ))

        # 退货率高 → 调整详情页
        if metrics["return_rate"] > 5:
            actions.append(AutoAction(
                product_id=product.id,
                action_type="update_detail",
                reason=f"退货率{metrics['return_rate']}%，超过5%阈值",
                old_value="当前详情页",
                new_value="增加尺码表+实拍对比图+买家秀",
                result="详情页已更新",
            ))

        # 评分低 → 联系供应商
        if metrics["avg_rating"] < 4.3:
            actions.append(AutoAction(
                product_id=product.id,
                action_type="quality_alert",
                reason=f"评分{metrics['avg_rating']}，品质可能有问题",
                result="已通知供应商关注品质，下批货加检",
            ))

        return actions
