"""
模拟数据层 — 模拟小红书/抖音/1688/淘宝等数据源
实际部署时替换为真实 API 调用
"""
import random
from datetime import datetime, timedelta
from models import *


# ── 模拟趋势数据 ──────────────────────────────
TREND_POOL = [
    {
        "keyword": "磁吸充电宝",
        "category": "3C数码",
        "source": TrendSource.XIAOHONGSHU,
        "heat": 87, "growth": 156, "competition": "medium",
        "reason": "小红书近7天笔记增长156%，iPhone用户刚需，复购率高",
        "price_range": "49-129元", "margin": "45-60%", "risk": "low"
    },
    {
        "keyword": "露营折叠椅",
        "category": "户外运动",
        "source": TrendSource.DOUYIN,
        "heat": 82, "growth": 98, "competition": "low",
        "reason": "抖音 #露营 话题 120亿播放，轻量款搜索量暴涨",
        "price_range": "39-89元", "margin": "50-65%", "risk": "low"
    },
    {
        "keyword": "桌面氛围灯",
        "category": "家居",
        "source": TrendSource.XIAOHONGSHU,
        "heat": 79, "growth": 210, "competition": "medium",
        "reason": "Z世代租房改造需求旺盛，RGB氛围灯成宿舍标配",
        "price_range": "19-69元", "margin": "60-75%", "risk": "low"
    },
    {
        "keyword": "宠物自动喂食器",
        "category": "宠物",
        "source": TrendSource.TIKTOK,
        "heat": 91, "growth": 178, "competition": "high",
        "reason": "养宠人群持续扩大，出差/旅行场景强需求",
        "price_range": "89-299元", "margin": "35-50%", "risk": "medium"
    },
    {
        "keyword": "便携筋膜枪",
        "category": "健康",
        "source": TrendSource.AMAZON,
        "heat": 75, "growth": 67, "competition": "high",
        "reason": "健身人群标配，mini款在亚马逊BSR持续上升",
        "price_range": "69-199元", "margin": "40-55%", "risk": "medium"
    },
    {
        "keyword": "车载香薰",
        "category": "汽车配件",
        "source": TrendSource.DOUYIN,
        "heat": 73, "growth": 134, "competition": "low",
        "reason": "新车车主刚需，抖音汽车频道高频推荐品",
        "price_range": "19-59元", "margin": "65-80%", "risk": "low"
    },
    {
        "keyword": "可降解手机壳",
        "category": "3C配件",
        "source": TrendSource.XIAOHONGSHU,
        "heat": 68, "growth": 245, "competition": "low",
        "reason": "环保概念兴起，小红书\"绿色生活\"标签下增速最快品类",
        "price_range": "29-69元", "margin": "55-70%", "risk": "low"
    },
    {
        "keyword": "智能体重秤",
        "category": "健康",
        "source": TrendSource.GOOGLE_TRENDS,
        "heat": 71, "growth": 45, "competition": "medium",
        "reason": "年初减脂季+智能健康趋势，体脂秤搜索量稳步上升",
        "price_range": "39-129元", "margin": "45-60%", "risk": "low"
    },
    {
        "keyword": "迷你投影仪",
        "category": "3C数码",
        "source": TrendSource.DOUYIN,
        "heat": 85, "growth": 189, "competition": "medium",
        "reason": "租房年轻人替代电视首选，抖音种草视频爆款频出",
        "price_range": "199-699元", "margin": "30-45%", "risk": "medium"
    },
    {
        "keyword": "防晒面罩",
        "category": "服饰",
        "source": TrendSource.XIAOHONGSHU,
        "heat": 88, "growth": 312, "competition": "medium",
        "reason": "物理防晒升级，\"脸基尼\"成今夏最火单品",
        "price_range": "15-49元", "margin": "60-75%", "risk": "low"
    },
]


# ── 模拟供应商数据 ──────────────────────────────
SUPPLIER_TEMPLATES = {
    "磁吸充电宝": [
        {"name": "深圳闪充科技有限公司", "price": 28.5, "moq": 100, "rating": 4.7, "resp": 2, "loc": "深圳"},
        {"name": "东莞力神电池厂", "price": 25.0, "moq": 500, "rating": 4.5, "resp": 4, "loc": "东莞"},
        {"name": "惠州数码配件厂", "price": 32.0, "moq": 50, "rating": 4.8, "resp": 1, "loc": "惠州"},
    ],
    "露营折叠椅": [
        {"name": "永康户外用品厂", "price": 22.0, "moq": 200, "rating": 4.6, "resp": 3, "loc": "金华"},
        {"name": "宁波野趣户外", "price": 18.5, "moq": 500, "rating": 4.3, "resp": 6, "loc": "宁波"},
        {"name": "台州折叠家具厂", "price": 25.0, "moq": 100, "rating": 4.9, "resp": 1, "loc": "台州"},
    ],
    "桌面氛围灯": [
        {"name": "中山灯饰源头厂", "price": 8.5, "moq": 300, "rating": 4.4, "resp": 3, "loc": "中山"},
        {"name": "义乌光电科技", "price": 6.0, "moq": 1000, "rating": 4.2, "resp": 5, "loc": "义乌"},
        {"name": "深圳智能照明", "price": 12.0, "moq": 100, "rating": 4.7, "resp": 2, "loc": "深圳"},
    ],
    "宠物自动喂食器": [
        {"name": "佛山宠物智能工厂", "price": 55.0, "moq": 100, "rating": 4.6, "resp": 3, "loc": "佛山"},
        {"name": "深圳宠物科技", "price": 48.0, "moq": 300, "rating": 4.4, "resp": 4, "loc": "深圳"},
        {"name": "东莞电器制品厂", "price": 62.0, "moq": 50, "rating": 4.8, "resp": 1, "loc": "东莞"},
    ],
    "便携筋膜枪": [
        {"name": "宁波健身器材厂", "price": 45.0, "moq": 200, "rating": 4.5, "resp": 3, "loc": "宁波"},
        {"name": "深圳健康科技", "price": 38.0, "moq": 500, "rating": 4.3, "resp": 5, "loc": "深圳"},
        {"name": "东莞按摩器材厂", "price": 52.0, "moq": 100, "rating": 4.7, "resp": 2, "loc": "东莞"},
    ],
}


def get_default_suppliers(keyword: str) -> list[dict]:
    """为没有预设数据的品类生成默认供应商"""
    return [
        {"name": f"义乌{keyword}源头厂", "price": random.uniform(10, 50), "moq": 200,
         "rating": round(random.uniform(4.0, 4.8), 1), "resp": random.randint(2, 6), "loc": "义乌"},
        {"name": f"深圳{keyword}科技公司", "price": random.uniform(8, 45), "moq": 500,
         "rating": round(random.uniform(4.2, 4.9), 1), "resp": random.randint(1, 4), "loc": "深圳"},
        {"name": f"东莞{keyword}制品厂", "price": random.uniform(12, 55), "moq": 100,
         "rating": round(random.uniform(4.3, 4.7), 1), "resp": random.randint(1, 3), "loc": "东莞"},
    ]


# ── 模拟内容生成 ──────────────────────────────
def generate_mock_content(product_name: str, category: str) -> dict:
    """模拟 AI 生成的营销内容"""
    templates = {
        "titles": [
            f"🔥2026爆款！{product_name} 颜值实力双在线",
            f"被问了800遍的{product_name}终于上架了！",
            f"后悔没早买！{product_name}用了一周真实体验",
            f"同款{product_name}别买贵了！源头工厂直发",
            f"✨宿舍/租房必备！{product_name}提升幸福感",
        ],
        "bullet_points": [
            f"✅ {product_name}核心卖点1：品质升级，用料扎实",
            f"✅ {product_name}核心卖点2：设计简约，百搭好看",
            f"✅ {product_name}核心卖点3：操作简单，小白友好",
            f"✅ {product_name}核心卖点4：性价比高，工厂直供",
            f"✅ {product_name}核心卖点5：售后无忧，7天无理由",
        ],
        "description": f"""✨ {product_name} — {category}新宠

你是不是也遇到过这样的烦恼？
❌ 买过很多同类产品，质量参差不齐
❌ 价格虚高，花了冤枉钱
❌ 设计丑，拿不出手

这款{product_name}帮你一步到位👇

🎯 【为什么选我们】
• 源头工厂直供，砍掉中间商差价
• 100+道工序品控，质量有保障
• 50000+用户好评验证

💡 【使用场景】
家用 / 办公 / 送礼 / 出差旅行 全场景覆盖

📦 【下单即享】
• 48小时内发货
• 运费险全覆盖
• 不满意随时退

👇 现在下单享受限时特惠，错过恢复原价！""",
        "video_script": f"""【30秒口播脚本 — {product_name}】

(0-3s) 开场hook：
"姐妹们！这个{product_name}我真的要吹爆！"

(3-8s) 痛点引入：
"之前买过好几个，不是质量差就是不好看，钱白花了。"

(8-18s) 产品展示：
"直到遇到这款！你看这个质感，这个设计，绝了！"
（特写产品细节、使用场景）

(18-25s) 信任背书：
"我自己用了一个月了，5万多人买过好评率98%！"

(25-30s) 促单：
"现在下单还有优惠，链接在左下角，冲！"
""",
        "image_prompts": [
            f"Product photo of {product_name}, white background, studio lighting, 4K, professional e-commerce style",
            f"{product_name} in lifestyle setting, cozy room, warm lighting, instagram aesthetic",
            f"Close-up detail shot of {product_name}, showing texture and quality, macro photography",
        ],
        "seo_keywords": [
            product_name, f"{category}推荐", f"{product_name}哪个牌子好",
            f"{product_name}性价比", f"2026{product_name}排行", f"{product_name}测评",
        ],
    }
    return templates


# ── 模拟销售数据 ──────────────────────────────
def generate_mock_metrics(product_name: str, days: int = 7) -> list[dict]:
    """生成模拟销售数据"""
    metrics = []
    base_impressions = random.randint(800, 3000)
    base_ctr = random.uniform(0.02, 0.08)
    base_cvr = random.uniform(0.01, 0.05)
    price = random.uniform(29, 199)

    for i in range(days):
        date = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        # 模拟自然波动
        day_factor = 1 + random.uniform(-0.3, 0.5)
        # 周末流量更高
        weekday = (datetime.now() - timedelta(days=days - 1 - i)).weekday()
        weekend_factor = 1.3 if weekday >= 5 else 1.0

        impressions = int(base_impressions * day_factor * weekend_factor)
        clicks = int(impressions * base_ctr * (1 + random.uniform(-0.2, 0.2)))
        orders = int(clicks * base_cvr * (1 + random.uniform(-0.3, 0.3)))
        revenue = round(orders * price, 2)
        cost = round(revenue * random.uniform(0.3, 0.6), 2)

        metrics.append({
            "product_id": "",
            "date": date,
            "impressions": impressions,
            "clicks": clicks,
            "orders": orders,
            "revenue": revenue,
            "cost": cost,
            "roi": round((revenue - cost) / cost * 100, 1) if cost > 0 else 0,
            "conversion_rate": round(orders / clicks * 100, 2) if clicks > 0 else 0,
            "return_rate": round(random.uniform(1, 8), 1),
            "avg_rating": round(random.uniform(4.2, 5.0), 1),
            "review_count": random.randint(10, 500),
        })
    return metrics


# ── 平台规则 ──────────────────────────────
PLATFORM_RULES = {
    Platform.TAOBAO: {
        "name": "淘宝",
        "title_max_len": 60,
        "commission_rate": 0.05,
        "min_price": 1.0,
        "features": ["直通车", "超级推荐", "淘宝客"],
    },
    Platform.PINDUODUO: {
        "name": "拼多多",
        "title_max_len": 60,
        "commission_rate": 0.03,
        "min_price": 0.1,
        "features": ["多多搜索", "多多场景", "万人团"],
    },
    Platform.DOUYIN_SHOP: {
        "name": "抖音小店",
        "title_max_len": 30,
        "commission_rate": 0.05,
        "min_price": 1.0,
        "features": ["精选联盟", "巨量千川", "直播间挂车"],
    },
    Platform.TEMU: {
        "name": "Temu",
        "title_max_len": 100,
        "commission_rate": 0.15,
        "min_price": 0.5,
        "features": ["全托管", "半托管"],
    },
}
