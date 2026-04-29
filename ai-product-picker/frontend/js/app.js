/**
 * AI 选品官 — 前端逻辑
 */

const API = '';
let currentData = {
    run: null,
    trends: [],
    listings: [],
    report: null,
};

// ── 流水线执行 ──────────────────────────────

async function runPipeline() {
    const btn = document.getElementById('btnRun');
    const topN = parseInt(document.getElementById('topN').value);

    btn.disabled = true;
    btn.classList.add('running');
    btn.innerHTML = '⏳ 执行中...';

    document.getElementById('pipelineSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('logBody').innerHTML = '';
    resetSteps();

    const statusDot = document.getElementById('systemStatus');
    const statusText = document.getElementById('statusText');
    statusDot.className = 'status-dot running';
    statusText.textContent = '执行中...';

    try {
        // 启动流水线
        const response = await fetch(`${API}/api/pipeline/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ top_n: topN }),
        });

        const data = await response.json();
        currentData.run = data;

        // 显示日志
        renderLogs(data.logs || []);

        // 标记步骤完成
        for (let i = 1; i <= 5; i++) {
            markStepDone(i);
        }

        // 加载结果数据
        await loadAllData();

        statusDot.className = 'status-dot';
        statusText.textContent = '完成';

    } catch (err) {
        console.error(err);
        statusDot.className = 'status-dot error';
        statusText.textContent = '出错';
        addLog('❌ 执行出错: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.classList.remove('running');
        btn.innerHTML = '🚀 开始执行';
    }
}

// ── 日志系统 ──────────────────────────────

function renderLogs(logs) {
    const body = document.getElementById('logBody');
    body.innerHTML = '';
    logs.forEach((log, i) => {
        setTimeout(() => {
            addLog(log);
        }, i * 80);
    });
}

function addLog(text, type = '') {
    const body = document.getElementById('logBody');
    const entry = document.createElement('div');
    entry.className = 'log-entry' + (type ? ` ${type}` : '');
    entry.textContent = text;
    body.appendChild(entry);
    body.scrollTop = body.scrollHeight;

    const count = document.getElementById('logCount');
    count.textContent = `${body.children.length} 条`;
}

// ── 步骤状态 ──────────────────────────────

function resetSteps() {
    for (let i = 1; i <= 5; i++) {
        const el = document.getElementById(`step${i}`);
        el.className = 'step';
    }
}

function markStepActive(n) {
    const el = document.getElementById(`step${n}`);
    el.className = 'step active';
}

function markStepDone(n) {
    const el = document.getElementById(`step${n}`);
    el.className = 'step done';
}

// ── 数据加载 ──────────────────────────────

async function loadAllData() {
    try {
        const [trendsRes, listingsRes, reportRes] = await Promise.all([
            fetch(`${API}/api/trends`).then(r => r.json()),
            fetch(`${API}/api/listings`).then(r => r.json()),
            fetch(`${API}/api/report`).then(r => r.json()),
        ]);

        currentData.trends = trendsRes.picks || [];
        currentData.listings = listingsRes.listings || [];
        currentData.report = reportRes;

        document.getElementById('resultsSection').style.display = 'block';
        switchTab('trends');
    } catch (err) {
        console.error('加载数据失败:', err);
    }
}

// ── Tab 切换 ──────────────────────────────

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    const content = document.getElementById('tabContent');

    switch (tabName) {
        case 'trends': renderTrends(content); break;
        case 'supply': renderSupply(content); break;
        case 'content': renderContent(content); break;
        case 'listings': renderListings(content); break;
        case 'dashboard': renderDashboard(content); break;
        case 'report': renderReport(content); break;
    }
}

// ── 趋势选品 Tab ──────────────────────────────

function renderTrends(container) {
    if (!currentData.trends.length) {
        container.innerHTML = emptyState('🔍', '暂无趋势数据，请先执行流水线');
        return;
    }

    const cards = currentData.trends.map(pick => {
        const heatClass = pick.trend.heat_score >= 85 ? 'badge-hot' :
                         pick.trend.heat_score >= 70 ? 'badge-warm' : 'badge-new';
        const heatLabel = pick.trend.heat_score >= 85 ? '🔥 爆款' :
                         pick.trend.heat_score >= 70 ? '🌡️ 上升' : '🌱 新星';

        return `
        <div class="trend-card">
            <div class="trend-card-header">
                <h4>${pick.name}</h4>
                <span class="trend-badge ${heatClass}">${heatLabel}</span>
            </div>
            <div class="trend-meta">
                <span>📂 ${pick.category}</span>
                <span>🌡️ 热度 ${pick.trend.heat_score}</span>
                <span>📈 +${pick.trend.growth_rate}%</span>
                <span>💰 ${pick.estimated_price_range}</span>
            </div>
            <div class="trend-reason">${pick.trend.reason}</div>
            <div class="score-bar">
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:${pick.score}%"></div>
                </div>
                <div class="score-value">${pick.score}</div>
            </div>
        </div>`;
    }).join('');

    container.innerHTML = `<div class="trend-grid">${cards}</div>`;
}

// ── 供应链 Tab ──────────────────────────────

async function renderSupply(container) {
    if (!currentData.run || !currentData.run.supply_quotes.length) {
        container.innerHTML = emptyState('🏭', '暂无供应链数据');
        return;
    }

    let html = '';
    for (const quote of currentData.run.supply_quotes) {
        const product = currentData.trends.find(t => t.id === quote.product_id);
        const productName = product ? product.name : '未知产品';

        const rows = quote.suppliers.map(s => {
            const isBest = s.id === quote.best_supplier_id;
            return `
            <tr class="${isBest ? 'supplier-best' : ''}">
                <td>${s.name}</td>
                <td>¥${s.price.toFixed(2)}</td>
                <td>${s.moq}</td>
                <td>⭐ ${s.rating}</td>
                <td>${s.response_time_hours}h</td>
                <td>${s.location}</td>
                <td>
                    ${isBest ? '<span class="tag tag-best">最优</span>' : ''}
                    ${s.verified ? '<span class="tag tag-verified">已验厂</span>' : ''}
                </td>
            </tr>`;
        }).join('');

        html += `
        <h4 style="margin:20px 0 12px;">📦 ${productName}</h4>
        <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;">
            ${quote.negotiation_notes}
        </p>
        <table class="supplier-table">
            <thead>
                <tr>
                    <th>供应商</th><th>报价</th><th>MOQ</th>
                    <th>评分</th><th>响应</th><th>产地</th><th>状态</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>`;
    }

    container.innerHTML = html;
}

// ── 内容素材 Tab ──────────────────────────────

async function renderContent(container) {
    if (!currentData.run || !currentData.run.contents.length) {
        container.innerHTML = emptyState('✍️', '暂无内容数据');
        return;
    }

    let html = '';
    for (const content of currentData.run.contents) {
        const product = currentData.trends.find(t => t.id === content.product_id);
        const productName = product ? product.name : '未知产品';

        const titles = content.titles.map((t, i) =>
            `<div class="title-option"><span class="num">${i + 1}</span>${t}</div>`
        ).join('');

        html += `
        <h3 style="margin-bottom:20px;">📦 ${productName}</h3>

        <div class="content-section">
            <h4>📝 标题方案（5套 A/B 测试）</h4>
            ${titles}
        </div>

        <div class="content-section">
            <h4>📄 详情页文案</h4>
            <div class="content-card"><pre>${content.description}</pre></div>
        </div>

        <div class="content-section">
            <h4>🎯 卖点</h4>
            ${content.bullet_points.map(bp =>
                `<div class="content-card">${bp}</div>`
            ).join('')}
        </div>

        <div class="content-section">
            <h4>🎬 30秒口播脚本</h4>
            <div class="content-card"><pre>${content.video_script_30s}</pre></div>
        </div>

        <div class="content-section">
            <h4>🔑 SEO 关键词</h4>
            <div style="display:flex;flex-wrap:wrap;gap:6px;">
                ${content.seo_keywords.map(kw =>
                    `<span class="tag" style="background:var(--border);color:var(--text-dim);">${kw}</span>`
                ).join('')}
            </div>
        </div>
        <hr style="border:none;border-top:1px solid var(--border);margin:24px 0;">`;
    }

    container.innerHTML = html;
}

// ── 上架信息 Tab ──────────────────────────────

function renderListings(container) {
    if (!currentData.listings.length) {
        container.innerHTML = emptyState('🚀', '暂无上架数据');
        return;
    }

    const platformIcons = {
        taobao: { icon: '淘', class: 'platform-taobao', name: '淘宝' },
        pinduoduo: { icon: '拼', class: 'platform-pinduoduo', name: '拼多多' },
        douyin_shop: { icon: '抖', class: 'platform-douyin_shop', name: '抖音小店' },
        temu: { icon: 'T', class: 'platform-temu', name: 'Temu' },
    };

    const cards = currentData.listings.map(listing => {
        const p = platformIcons[listing.platform] || { icon: '?', class: '', name: listing.platform };
        const product = currentData.trends.find(t => t.id === listing.product_id);
        const productName = product ? product.name : '未知产品';

        return `
        <div class="listing-card">
            <div class="listing-platform">
                <div class="platform-icon ${p.class}">${p.icon}</div>
                <div>
                    <div style="font-weight:600;">${p.name}</div>
                    <div style="font-size:12px;color:var(--text-muted);">${productName}</div>
                </div>
            </div>
            <div class="listing-price">¥${listing.price.toFixed(2)}</div>
            <div class="listing-info">
                <div>📌 ${listing.title}</div>
                ${listing.coupon_config ? `<div>🎫 优惠券: 满${listing.coupon_config.threshold}减${listing.coupon_config.value}</div>` : ''}
                ${listing.promotion_config ? `<div>⏰ 限时${listing.promotion_config.duration_hours}h ${(listing.promotion_config.discount * 10).toFixed(1)}折</div>` : ''}
                <div>🔗 <a href="${listing.listing_url}" style="color:var(--accent);text-decoration:none;">${listing.listing_url}</a></div>
            </div>
        </div>`;
    }).join('');

    container.innerHTML = `<div class="listing-grid">${cards}</div>`;
}

// ── 数据面板 Tab ──────────────────────────────

async function renderDashboard(container) {
    if (!currentData.trends.length) {
        container.innerHTML = emptyState('📊', '暂无数据');
        return;
    }

    container.innerHTML = '<div class="loading"><div class="spinner"></div>加载数据中...</div>';

    try {
        // 获取第一个产品的数据
        const pick = currentData.trends[0];
        const res = await fetch(`${API}/api/dashboard/${pick.id}`);
        const data = await res.json();

        if (!data.metrics || !data.metrics.length) {
            container.innerHTML = emptyState('📊', '暂无监控数据');
            return;
        }

        const metrics = data.metrics;
        const totalRevenue = metrics.reduce((s, m) => s + m.revenue, 0);
        const totalOrders = metrics.reduce((s, m) => s + m.orders, 0);
        const totalClicks = metrics.reduce((s, m) => s + m.clicks, 0);
        const avgCvr = totalClicks > 0 ? (totalOrders / totalClicks * 100).toFixed(2) : 0;

        // 柱状图数据
        const maxRevenue = Math.max(...metrics.map(m => m.revenue));
        const bars = metrics.map(m => {
            const height = maxRevenue > 0 ? (m.revenue / maxRevenue * 180) : 0;
            return `
            <div class="bar-col">
                <div class="bar-value">¥${m.revenue.toFixed(0)}</div>
                <div class="bar" style="height:${height}px"></div>
                <div class="bar-label">${m.date.slice(5)}</div>
            </div>`;
        }).join('');

        container.innerHTML = `
        <h4 style="margin-bottom:16px;">📦 ${pick.name} — 近7日数据</h4>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">¥${totalRevenue.toFixed(0)}</div>
                <div class="metric-label">总营收</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${totalOrders}</div>
                <div class="metric-label">总订单</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${avgCvr}%</div>
                <div class="metric-label">转化率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">⭐ ${metrics[metrics.length-1].avg_rating}</div>
                <div class="metric-label">评分</div>
            </div>
        </div>
        <div class="chart-area">
            <h4>📈 每日营收趋势</h4>
            <div class="bar-chart">${bars}</div>
        </div>`;

    } catch (err) {
        container.innerHTML = emptyState('❌', '加载失败: ' + err.message);
    }
}

// ── 运营报告 Tab ──────────────────────────────

function renderReport(container) {
    if (!currentData.report || currentData.report.message) {
        container.innerHTML = emptyState('📋', '暂无报告');
        return;
    }

    const r = currentData.report;

    let alertsHtml = '';
    if (r.alerts && r.alerts.length) {
        const items = r.alerts.map(a => {
            const cls = a.includes('🔴') ? 'danger' : '';
            return `<div class="alert-item ${cls}">${a}</div>`;
        }).join('');
        alertsHtml = `<div class="alerts-section"><h4>⚠️ 告警 (${r.alerts.length})</h4>${items}</div>`;
    }

    let actionsHtml = '';
    if (r.auto_actions_taken && r.auto_actions_taken.length) {
        const items = r.auto_actions_taken.map(a => `
            <div class="auto-action">
                <span class="action-type">${a.action_type}</span>
                <div>
                    <div><strong>原因：</strong>${a.reason}</div>
                    <div style="color:var(--success);margin-top:4px;">✅ ${a.result}</div>
                </div>
            </div>
        `).join('');
        actionsHtml = `<div class="alerts-section"><h4>🤖 自动优化动作 (${r.auto_actions_taken.length})</h4>${items}</div>`;
    }

    container.innerHTML = `
    <div class="report-summary">
        <div class="report-card">
            <h3>📦 在售商品</h3>
            <div class="value" style="color:var(--accent);">${r.total_products}</div>
        </div>
        <div class="report-card">
            <h3>💰 今日营收</h3>
            <div class="value" style="color:var(--success);">¥${r.total_revenue.toFixed(0)}</div>
        </div>
        <div class="report-card">
            <h3>🛒 今日订单</h3>
            <div class="value" style="color:var(--warning);">${r.total_orders}</div>
        </div>
    </div>
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:14px;color:var(--text-muted);">📅 ${r.date}</span>
        &nbsp;&nbsp;
        <span style="font-size:14px;">📈 平均ROI: <strong style="color:var(--success);">${r.avg_roi}%</strong></span>
        &nbsp;&nbsp;
        <span style="font-size:14px;">🏆 最佳: <strong>${r.top_product}</strong></span>
    </div>
    ${alertsHtml}
    ${actionsHtml}`;
}

// ── 工具函数 ──────────────────────────────

function emptyState(icon, text) {
    return `
    <div class="empty-state">
        <div class="icon">${icon}</div>
        <p>${text}</p>
    </div>`;
}

// ── 初始化 ──────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 AI 选品官 — 已就绪');
});
