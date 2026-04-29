"""
Agent 3: 内容工厂 — 自动生成标题/文案/主图/视频脚本
"""
from models import *
from mock_data import generate_mock_content


class ContentFactoryAgent:
    """内容工厂 Agent：为选品生成全套营销素材"""

    def __init__(self):
        self.name = "✍️ 内容工厂"
        self.status = "idle"

    async def generate_content(self, product: ProductPick, quote: SupplyQuote) -> ProductContent:
        """生成完整的商品内容素材包"""
        self.status = "generating"

        mock = generate_mock_content(product.name, product.category)

        content = ProductContent(
            product_id=product.id,
            titles=mock["titles"],
            description=mock["description"],
            bullet_points=mock["bullet_points"],
            video_script_30s=mock["video_script"],
            image_prompts=mock["image_prompts"],
            seo_keywords=mock["seo_keywords"],
        )

        self.status = "idle"
        return content
