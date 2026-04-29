"""
AI 选品官 — FastAPI 主入口
"""
import sys
import os

# 确保 backend 目录在 Python path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from orchestrator import PipelineOrchestrator
from models import *

app = FastAPI(title="AI 选品官", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# 全局编排器
orchestrator = PipelineOrchestrator()


# ── 页面路由 ──────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(frontend_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ── API 路由 ──────────────────────────────

@app.get("/api/status")
async def get_status():
    """系统状态"""
    return {
        "name": "AI 选品官",
        "version": "1.0.0",
        "agents": {
            "trend_hunter": orchestrator.trend_hunter.status,
            "supply_chain": orchestrator.supply_chain.status,
            "content_factory": orchestrator.content_factory.status,
            "listing": orchestrator.listing_agent.status,
            "data_dashboard": orchestrator.data_dashboard.status,
        },
        "last_run": orchestrator.current_run.id if orchestrator.current_run else None,
    }


@app.post("/api/pipeline/run")
async def run_pipeline(config: Optional[dict] = None):
    """执行完整流水线"""
    top_n = 3
    if config and "top_n" in config:
        top_n = config["top_n"]
    run = await orchestrator.run_full_pipeline(top_n=top_n)
    return run.model_dump()


@app.get("/api/pipeline/status")
async def pipeline_status():
    """获取当前流水线状态"""
    if not orchestrator.current_run:
        return {"status": "no_run", "message": "尚未执行过流水线"}
    run = orchestrator.current_run
    return {
        "id": run.id,
        "status": run.status,
        "current_step": run.current_step,
        "log_count": len(run.logs),
        "trend_picks_count": len(run.trend_picks),
        "listings_count": len(run.listings),
    }


@app.get("/api/pipeline/logs")
async def pipeline_logs():
    """获取流水线日志"""
    if not orchestrator.current_run:
        return {"logs": []}
    return {"logs": orchestrator.current_run.logs}


@app.get("/api/trends")
async def get_trends():
    """获取趋势选品"""
    if not orchestrator.current_run or not orchestrator.current_run.trend_picks:
        picks = await orchestrator.trend_hunter.scan_trends(top_n=5)
        return {"picks": [p.model_dump() for p in picks]}
    return {"picks": [p.model_dump() for p in orchestrator.current_run.trend_picks]}


@app.get("/api/suppliers/{product_id}")
async def get_suppliers(product_id: str):
    """获取供应商报价"""
    if not orchestrator.current_run:
        raise HTTPException(status_code=404, detail="请先执行流水线")
    for quote in orchestrator.current_run.supply_quotes:
        if quote.product_id == product_id:
            return quote.model_dump()
    raise HTTPException(status_code=404, detail="未找到该产品的供应商数据")


@app.get("/api/content/{product_id}")
async def get_content(product_id: str):
    """获取营销内容"""
    if not orchestrator.current_run:
        raise HTTPException(status_code=404, detail="请先执行流水线")
    for content in orchestrator.current_run.contents:
        if content.product_id == product_id:
            return content.model_dump()
    raise HTTPException(status_code=404, detail="未找到该产品的内容数据")


@app.get("/api/listings")
async def get_listings():
    """获取所有上架信息"""
    if not orchestrator.current_run:
        return {"listings": []}
    return {"listings": [l.model_dump() for l in orchestrator.current_run.listings]}


@app.get("/api/dashboard/{product_id}")
async def get_product_dashboard(product_id: str, days: int = 7):
    """获取商品数据面板"""
    if not orchestrator.current_run:
        raise HTTPException(status_code=404, detail="请先执行流水线")

    product = next(
        (p for p in orchestrator.current_run.trend_picks if p.id == product_id), None
    )
    if not product:
        raise HTTPException(status_code=404, detail="未找到该产品")

    metrics = await orchestrator.data_dashboard.get_product_metrics(
        product_id, product.name, days
    )
    return {
        "product": product.model_dump(),
        "metrics": [m.model_dump() for m in metrics],
    }


@app.get("/api/report")
async def get_daily_report():
    """获取每日运营报告"""
    if not orchestrator.current_run or not orchestrator.current_run.trend_picks:
        return {"message": "请先执行流水线"}
    report = await orchestrator.data_dashboard.generate_daily_report(
        orchestrator.current_run.trend_picks
    )
    return report.model_dump()


@app.post("/api/step/{step_name}")
async def run_single_step(step_name: str, body: dict = None):
    """单独执行某个Agent步骤"""
    kwargs = body or {}
    result = await orchestrator.run_single_step(step_name, **kwargs)
    return result


# ── 启动 ──────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 50)
    print("🤖 AI 选品官 — 启动中...")
    print("=" * 50)
    print("📊 仪表盘: http://localhost:8000")
    print("📖 API 文档: http://localhost:8000/docs")
    print("=" * 50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
