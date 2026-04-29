"""
Agent 4: 上架运营 — 多平台一键发布
"""
import random
from models import *
from mock_data import PLATFORM_RULES


class ListingAgent:
    """上架运营 Agent：自动适配各平台规则，一键发布"""

    def __init__(self):
        self.name = "🚀 上架运营"
        self.status = "idle"

    async def publish_to_platforms(
        self, product: ProductPick, quote: SupplyQuote,
        content: ProductContent, platforms: list[Platform] = None
    ) -> list[ListingConfig]:
        """将商品发布到多个平台"""
        self.status = "publishing"

        if platforms is None:
            platforms = [Platform.TAOBAO, Platform.PINDUODUO, Platform.DOUYIN_SHOP]

        listings = []
        best_supplier = next(
            (s for s in quote.suppliers if s.id == quote.best_supplier_id),
            quote.suppliers[0]
        )

        for platform in platforms:
            rules = PLATFORM_RULES.get(platform, {})

            # 定价策略：成本 × 加价倍率 + 平台佣金
            cost = best_supplier.price
            markup = random.uniform(1.8, 3.0)
            commission = rules.get("commission_rate", 0.05)
            price = round(cost * markup / (1 - commission), 2)

            # 标题适配平台长度限制
            max_len = rules.get("title_max_len", 60)
            title = content.titles[0][:max_len]

            # 优惠券配置
            coupon_value = round(price * random.uniform(0.05, 0.15), 2)

            listing = ListingConfig(
                product_id=product.id,
                platform=platform,
                title=title,
                price=price,
                coupon_config={
                    "type": "满减",
                    "threshold": round(price * 1.5, 2),
                    "value": coupon_value,
                },
                promotion_config={
                    "type": "限时折扣",
                    "discount": round(random.uniform(0.8, 0.95), 2),
                    "duration_hours": random.choice([24, 48, 72]),
                },
                status=TaskStatus.COMPLETED,
                listing_url=f"https://{platform.value}.com/item/{random.randint(100000, 999999)}",
            )
            listings.append(listing)

        self.status = "idle"
        return listings

    def calculate_pricing_strategy(
        self, cost: float, platform: Platform, competitor_price: float = None
    ) -> dict:
        """计算定价策略"""
        rules = PLATFORM_RULES.get(platform, {})
        commission = rules.get("commission_rate", 0.05)

        # 成本加成法
        cost_plus_price = round(cost * 2.5 / (1 - commission), 2)

        # 竞品对标法
        if competitor_price:
            competitive_price = round(competitor_price * 0.9, 2)  # 低于竞品10%
            recommended = round((cost_plus_price + competitive_price) / 2, 2)
        else:
            recommended = cost_plus_price

        return {
            "cost": cost,
            "recommended_price": recommended,
            "min_price": round(cost / (1 - commission) * 1.2, 2),
            "commission": commission,
            "estimated_margin": round((recommended - cost) / recommended * 100, 1),
        }
