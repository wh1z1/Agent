"""
Agent 2: 供应链 Agent — 1688找厂、比价、自动询价
"""
import random
from models import *
from mock_data import SUPPLIER_TEMPLATES, get_default_suppliers


class SupplyChainAgent:
    """供应链 Agent：自动在1688/义乌购找源头工厂，比价、询价、谈判"""

    def __init__(self):
        self.name = "🏭 供应链"
        self.status = "idle"

    async def find_suppliers(self, product: ProductPick) -> SupplyQuote:
        """为指定产品寻找最优供应商"""
        self.status = "searching"
        logs = []

        # 获取供应商数据
        raw_suppliers = SUPPLIER_TEMPLATES.get(
            product.name, get_default_suppliers(product.name)
        )

        # 构建 Supplier 对象
        suppliers = []
        for i, s in enumerate(raw_suppliers):
            supplier = Supplier(
                id=f"supplier_{random.randint(1000, 9999)}",
                name=s["name"],
                platform="1688",
                price=s["price"],
                moq=s["moq"],
                rating=s["rating"],
                response_time_hours=s["resp"],
                location=s["loc"],
                verified=random.random() > 0.3,
            )
            suppliers.append(supplier)

        # 模拟自动谈判 — 价格降低 5-15%
        for s in suppliers:
            discount = random.uniform(0.05, 0.15)
            original_price = s.price
            s.price = round(s.price * (1 - discount), 2)
            logs.append(
                f"[{self.name}] 💬 与 {s.name} 谈判: "
                f"¥{original_price} → ¥{s.price} (降{discount*100:.0f}%)"
            )

        # 综合评分选最优：价格 50% + 评分 25% + 响应速度 15% + MOQ 10%
        best = self._select_best(suppliers)

        logs.append(f"[{self.name}] 🏆 最优供应商: {best.name} (¥{best.price}, 评分{best.rating})")

        quote = SupplyQuote(
            product_id=product.id,
            suppliers=suppliers,
            best_supplier_id=best.id,
            negotiation_notes=f"共询价{len(suppliers)}家，最优选择{best.name}，"
                              f"MOQ={best.moq}，48h内可发货",
            total_cost_estimate=round(best.price * best.moq, 2),
        )

        self.status = "idle"
        return quote

    def _select_best(self, suppliers: list[Supplier]) -> Supplier:
        """综合评分选出最优供应商"""
        def score(s: Supplier) -> float:
            price_score = (1 - s.price / max(x.price for x in suppliers)) * 50
            rating_score = s.rating / 5 * 25
            resp_score = (1 - s.response_time_hours / 12) * 15
            moq_score = (1 - s.moq / max(x.moq for x in suppliers)) * 10
            return price_score + rating_score + resp_score + moq_score

        return max(suppliers, key=score)
