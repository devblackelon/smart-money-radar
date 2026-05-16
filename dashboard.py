# ============================================================
#  SMART MONEY RADAR — Live Web Dashboard
#  Tabs: Live Radar | Leaderboard | Smart Wallets |
#        Token Search | Wallet Tracker | How It Works
# ============================================================

import json
import os
import time as pytime
from flask import Flask, render_template_string, request, jsonify
import requests as req

app = Flask(__name__)
RESULTS_FILE = "results.json"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Money Radar</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:       #080c10;
      --surface:  #0e1520;
      --surface2: #131d2b;
      --border:   #1e2d40;
      --accent:   #00e5aa;
      --blue:     #3b82f6;
      --warn:     #f59e0b;
      --purple:   #a855f7;
      --red:      #ef4444;
      --text:     #e8edf2;
      --muted:    #6b7f96;
      --dim:      #3a4f66;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      line-height: 1.6;
    }

    /* HEADER */
    header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 24px 48px;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(135deg, #0b1520, #0e1a28);
    }
    .logo { display:flex; align-items:center; gap:14px; }
    .logo-icon {
      width:44px; height:44px;
      background: linear-gradient(135deg, var(--accent), #00b386);
      border-radius:12px; display:flex; align-items:center; justify-content:center;
      font-size:22px;
    }
    .logo h1 {
      font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800;
      color:#fff; letter-spacing:-0.02em;
    }
    .logo p { font-size:0.78rem; color:var(--muted); margin-top:1px; }
    .header-right { text-align:right; }
    .header-right .info { font-size:0.78rem; color:var(--muted); line-height:1.9; }
    .header-right .info span { color:var(--accent); font-family:'DM Mono',monospace; }
    .live-badge {
      display:inline-flex; align-items:center; gap:6px;
      background:#00e5aa18; border:1px solid #00e5aa44;
      color:var(--accent); font-size:0.7rem; font-weight:600;
      padding:3px 10px; border-radius:20px; margin-top:6px; letter-spacing:0.05em;
    }
    .live-dot { width:6px; height:6px; background:var(--accent); border-radius:50%; animation:pulse 1.5s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

    /* STATS BAR */
    .stats-bar {
      display:grid; grid-template-columns:repeat(5,1fr);
      gap:1px; background:var(--border); border-bottom:1px solid var(--border);
    }
    .stat { background:var(--surface); padding:22px 28px; position:relative; overflow:hidden; }
    .stat::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; }
    .stat.s1::before { background:var(--blue); }
    .stat.s2::before { background:var(--accent); }
    .stat.s3::before { background:var(--purple); }
    .stat.s4::before { background:var(--warn); }
    .stat.s5::before { background:var(--red); }
    .stat-value { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; line-height:1; margin-bottom:4px; }
    .stat.s1 .stat-value { color:var(--blue); }
    .stat.s2 .stat-value { color:var(--accent); }
    .stat.s3 .stat-value { color:var(--purple); }
    .stat.s4 .stat-value { color:var(--warn); }
    .stat.s5 .stat-value { color:var(--red); }
    .stat-label { font-size:0.68rem; font-weight:600; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase; }

    /* TABS */
    .tabs {
      display:flex; gap:0;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 48px;
      overflow-x: auto;
    }
    .tab {
      padding: 14px 20px;
      font-size: 0.82rem; font-weight: 600;
      color: var(--muted); cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: color 0.2s, border-color 0.2s;
      background: none; border-top:none; border-left:none; border-right:none;
      font-family: 'DM Sans', sans-serif;
      white-space: nowrap;
    }
    .tab:hover { color: var(--text); }
    .tab.active { color: var(--accent); border-bottom-color: var(--accent); }

    /* PANELS */
    .panel { display:none; }
    .panel.active { display:block; }

    /* SECTION */
    .section { padding:32px 48px; }
    .section-header { display:flex; align-items:center; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
    .section-header h2 { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#fff; }
    .badge { background:var(--surface2); border:1px solid var(--border); color:var(--muted); font-size:0.7rem; font-weight:600; padding:3px 9px; border-radius:20px; font-family:'DM Mono',monospace; }
    .divider { height:1px; background:var(--border); margin:0 48px; }

    /* FILTER BUTTONS */
    .filter-btn {
      background:var(--surface2); border:1px solid var(--border);
      color:var(--muted); font-size:0.75rem; font-weight:600;
      padding:5px 14px; border-radius:20px; cursor:pointer;
      font-family:'DM Sans',sans-serif; transition:all 0.2s;
    }
    .filter-btn:hover { border-color:var(--dim); color:var(--text); }
    .filter-btn.active { background:var(--accent); border-color:var(--accent); color:#000; }
    .filter-btn.f-mid.active  { background:var(--warn); border-color:var(--warn); color:#000; }
    .filter-btn.f-low.active  { background:var(--red);  border-color:var(--red);  color:#fff; }

    /* TOKEN CARDS */
    .token-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }
    .token-card {
      background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:20px;
      position:relative; overflow:hidden; transition:border-color 0.2s, transform 0.15s;
    }
    .token-card:hover { border-color:var(--dim); transform:translateY(-1px); }
    .token-card.alpha { border-color:#00e5aa33; background:linear-gradient(135deg,#0e1f18,#0e1520); }
    .token-card.alpha::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,var(--accent),#00b386); }
    .token-card.watch { border-color:#f59e0b22; }
    .card-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px; }
    .token-symbol { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#fff; }
    .token-name { font-size:0.75rem; color:var(--muted); margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:160px; }
    .score-pill { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; padding:5px 12px; border-radius:8px; }
    .score-pill.high { background:#00e5aa18; color:var(--accent); border:1px solid #00e5aa33; }
    .score-pill.mid  { background:#f59e0b18; color:var(--warn);   border:1px solid #f59e0b33; }
    .score-pill.low  { background:#ef444418; color:var(--red); border:1px solid #ef444433; }
    .score-bar { height:4px; background:var(--surface2); border-radius:4px; overflow:hidden; margin-bottom:14px; }
    .score-fill { height:100%; border-radius:4px; }
    .score-fill.high { background:linear-gradient(90deg,var(--accent),#00ffaa); }
    .score-fill.mid  { background:linear-gradient(90deg,var(--warn),#fbbf24); }
    .score-fill.low  { background:var(--red); }
    .breakdown { display:grid; grid-template-columns:repeat(4,1fr); gap:6px; margin-bottom:12px; }
    .bd-item { background:var(--surface2); border-radius:8px; padding:8px 4px; text-align:center; }
    .bd-val { font-family:'DM Mono',monospace; font-size:0.95rem; color:var(--text); }
    .bd-val.good { color:var(--accent); }
    .bd-val.mid  { color:var(--warn); }
    .bd-val.bad  { color:var(--red); }
    .bd-lbl { font-size:0.6rem; color:var(--muted); margin-top:1px; text-transform:uppercase; letter-spacing:0.05em; }
    .sm-tags { display:flex; flex-wrap:wrap; gap:5px; margin-bottom:10px; }
    .sm-tag { background:#00e5aa10; border:1px solid #00e5aa30; color:var(--accent); font-family:'DM Mono',monospace; font-size:0.63rem; padding:3px 8px; border-radius:5px; }
    .card-footer { display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border); padding-top:10px; gap:8px; }
    .meta { font-size:0.72rem; color:var(--muted); }
    .meta span { color:var(--text); font-family:'DM Mono',monospace; }
    .card-time { font-size:0.67rem; color:var(--dim); font-family:'DM Mono',monospace; }
    .chart-btn {
      background:none; border:1px solid var(--border); color:var(--muted);
      font-size:0.68rem; padding:4px 10px; border-radius:6px; cursor:pointer;
      font-family:'DM Sans',sans-serif; transition:all 0.2s; white-space:nowrap;
    }
    .chart-btn:hover { border-color:var(--blue); color:var(--blue); }

    /* LEADERBOARD */
    .lb-table { width:100%; border-collapse:collapse; }
    .lb-table th { background:var(--surface2); font-size:0.7rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; padding:12px 16px; text-align:left; border-bottom:1px solid var(--border); }
    .lb-table td { padding:14px 16px; font-size:0.83rem; border-bottom:1px solid #0d1520; vertical-align:middle; }
    .lb-table tr:last-child td { border-bottom:none; }
    .lb-table tr:hover td { background:#0e152055; }
    .rank-medal { font-size:1.3rem; }
    .rank-num { font-family:'Syne',sans-serif; font-weight:800; font-size:1rem; color:var(--dim); }
    .lb-addr { font-family:'DM Mono',monospace; font-size:0.75rem; color:var(--accent); word-break:break-all; }
    .lb-hits { font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem; color:var(--purple); }
    .lb-tokens { display:flex; flex-wrap:wrap; gap:4px; }
    .lb-token { background:var(--surface2); border:1px solid var(--border); color:var(--text); font-size:0.68rem; padding:2px 7px; border-radius:4px; font-family:'DM Mono',monospace; }
    .lb-track-btn {
      background:none; border:1px solid var(--border); color:var(--muted);
      font-size:0.7rem; padding:5px 12px; border-radius:6px; cursor:pointer;
      font-family:'DM Sans',sans-serif; transition:all 0.2s; white-space:nowrap;
    }
    .lb-track-btn:hover { border-color:var(--accent); color:var(--accent); }

    /* TOKEN SEARCH */
    .search-box {
      display:flex; gap:12px; margin-bottom:24px;
      background:var(--surface); border:1px solid var(--border);
      border-radius:12px; padding:8px 8px 8px 16px;
      align-items:center;
    }
    .search-box input {
      flex:1; background:none; border:none; outline:none;
      color:var(--text); font-family:'DM Mono',monospace; font-size:0.85rem;
    }
    .search-box input::placeholder { color:var(--dim); }
    .search-btn {
      background:var(--accent); color:#000; font-weight:700; font-size:0.82rem;
      border:none; padding:10px 20px; border-radius:8px; cursor:pointer;
      font-family:'Syne',sans-serif; transition:opacity 0.2s; white-space:nowrap;
    }
    .search-btn:hover { opacity:0.85; }
    .token-detail { display:none; }
    .token-detail.visible { display:block; }
    .detail-card {
      background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:28px; margin-bottom:20px;
    }
    .detail-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px; flex-wrap:wrap; gap:12px; }
    .detail-sym { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#fff; }
    .detail-name { font-size:0.85rem; color:var(--muted); margin-top:4px; }
    .detail-addr { font-family:'DM Mono',monospace; font-size:0.68rem; color:var(--muted); margin-top:6px; }
    .birdeye-btn {
      display:inline-flex; align-items:center; gap:6px;
      background:var(--surface2); border:1px solid var(--border);
      color:var(--text); font-size:0.78rem; padding:8px 14px; border-radius:8px;
      text-decoration:none; transition:border-color 0.2s; cursor:pointer;
      font-family:'DM Sans',sans-serif;
    }
    .birdeye-btn:hover { border-color:var(--accent); color:var(--accent); }
    .detail-stats { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:10px; margin-bottom:20px; }
    .detail-stat { background:var(--surface2); border-radius:10px; padding:14px; }
    .detail-stat-val { font-family:'DM Mono',monospace; font-size:1rem; color:var(--text); }
    .detail-stat-lbl { font-size:0.68rem; color:var(--muted); margin-top:3px; text-transform:uppercase; letter-spacing:0.06em; }
    .sm-detected { background:#00e5aa15; border:1px solid #00e5aa33; border-left:3px solid var(--accent); border-radius:8px; padding:12px 16px; font-size:0.82rem; color:#9ecfbf; margin-bottom:16px; }

    /* CHART MODAL */
    .modal-overlay { display:none; position:fixed; top:0;left:0;right:0;bottom:0; background:#000000cc; z-index:1000; align-items:center; justify-content:center; }
    .modal-overlay.open { display:flex; }
    .modal { background:var(--surface); border:1px solid var(--border); border-radius:16px; width:92%; max-width:1000px; height:82vh; display:flex; flex-direction:column; overflow:hidden; }
    .modal-header { display:flex; justify-content:space-between; align-items:center; padding:16px 24px; border-bottom:1px solid var(--border); }
    .modal-title { font-family:'Syne',sans-serif; font-weight:700; color:#fff; font-size:1rem; }
    .modal-close { background:none; border:none; color:var(--muted); font-size:1.5rem; cursor:pointer; padding:2px 8px; transition:color 0.2s; }
    .modal-close:hover { color:#fff; }
    .modal-body { flex:1; }
    .modal-body iframe { width:100%; height:100%; border:none; }

    /* WALLET TRACKER */
    .wallet-result { display:none; }
    .wallet-result.visible { display:block; }
    .wallet-header {
      background:var(--surface); border:1px solid var(--border); border-radius:12px;
      padding:20px 24px; margin-bottom:20px;
      display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;
    }
    .wallet-addr { font-family:'DM Mono',monospace; font-size:0.85rem; color:var(--accent); word-break:break-all; }
    .wallet-stats { display:flex; gap:20px; }
    .wstat { text-align:right; }
    .wstat .wval { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:#fff; }
    .wstat .wlbl { font-size:0.68rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; }
    .tx-table { width:100%; border-collapse:collapse; }
    .tx-table th { background:var(--surface2); font-size:0.7rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; padding:10px 14px; text-align:left; border-bottom:1px solid var(--border); }
    .tx-table td { padding:12px 14px; font-size:0.82rem; border-bottom:1px solid #0e1520; vertical-align:middle; }
    .tx-table tr:last-child td { border-bottom:none; }
    .tx-table tr:hover td { background:#0e152066; }
    .tx-sym { font-family:'Syne',sans-serif; font-weight:700; color:#fff; }
    .tx-addr { font-family:'DM Mono',monospace; font-size:0.72rem; color:var(--muted); }
    .tx-type-buy  { color:var(--accent); font-weight:600; font-size:0.75rem; }
    .loading { text-align:center; padding:40px; color:var(--muted); font-size:0.85rem; }
    .error-msg { background:#ef444415; border:1px solid #ef444433; color:#f87171; border-radius:8px; padding:14px 18px; font-size:0.83rem; }
    .not-sm-notice { background:#a855f715; border:1px solid #a855f733; border-left:3px solid var(--purple); border-radius:8px; padding:12px 16px; margin-bottom:16px; font-size:0.82rem; color:#c4a0e8; }

    /* SMART MONEY WALLETS */
    .wallet-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:14px; margin-bottom:32px; }
    .wallet-card {
      background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:20px;
      display:flex; flex-direction:column; gap:12px;
    }
    .wallet-card-top { display:flex; justify-content:space-between; align-items:flex-start; }
    .wallet-full { font-family:'DM Mono',monospace; font-size:0.72rem; color:var(--accent); word-break:break-all; flex:1; margin-right:10px; }
    .hit-badge {
      background:var(--purple); color:#fff; font-family:'Syne',sans-serif;
      font-size:0.85rem; font-weight:800;
      min-width:36px; height:36px; border-radius:8px;
      display:flex; align-items:center; justify-content:center; flex-shrink:0;
    }
    .wallet-tokens { display:flex; flex-wrap:wrap; gap:5px; }
    .wtoken-tag { background:var(--surface2); border:1px solid var(--border); color:var(--text); font-size:0.7rem; padding:3px 8px; border-radius:5px; font-family:'DM Mono',monospace; }
    .wallet-track-btn {
      background:none; border:1px solid var(--border); color:var(--muted);
      font-size:0.72rem; font-weight:600; padding:6px 12px; border-radius:7px;
      cursor:pointer; font-family:'DM Sans',sans-serif; transition:all 0.2s; align-self:flex-start;
    }
    .wallet-track-btn:hover { border-color:var(--accent); color:var(--accent); }

    /* HOW IT WORKS */
    .how-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; margin-bottom:32px; }
    .how-card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:22px; position:relative; overflow:hidden; }
    .how-card::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; }
    .how-card.c1::before { background:var(--purple); }
    .how-card.c2::before { background:var(--accent); }
    .how-card.c3::before { background:var(--blue); }
    .how-card.c4::before { background:var(--warn); }
    .how-card.c5::before { background:var(--red); }
    .how-icon { font-size:1.8rem; margin-bottom:10px; }
    .how-card h3 { font-family:'Syne',sans-serif; font-size:0.95rem; font-weight:700; color:#fff; margin-bottom:6px; }
    .how-card p { font-size:0.8rem; color:var(--muted); line-height:1.7; }
    .score-table { width:100%; border-collapse:collapse; }
    .score-table th { background:var(--surface2); font-size:0.72rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; padding:10px 14px; text-align:left; border-bottom:1px solid var(--border); }
    .score-table td { padding:12px 14px; font-size:0.83rem; border-bottom:1px solid var(--border); vertical-align:top; }
    .score-table tr:last-child td { border-bottom:none; }
    .score-table tr:hover td { background:#0e1520aa; }
    .score-name { font-family:'Syne',sans-serif; font-weight:700; color:#fff; }
    .score-pts { font-family:'DM Mono',monospace; font-weight:500; color:var(--accent); }

    .empty { text-align:center; padding:60px; color:var(--muted); }
    .empty h3 { font-family:'Syne',sans-serif; font-size:1rem; margin-bottom:6px; color:var(--dim); }

    footer { border-top:1px solid var(--border); padding:18px 48px; display:flex; justify-content:space-between; align-items:center; }
    footer .left { font-size:0.75rem; color:var(--muted); }
    footer .left strong { color:var(--text); }
    footer .tag { font-size:0.72rem; color:var(--accent); font-family:'DM Mono',monospace; }
  </style>
</head>
<body>

<!-- Header -->
<header>
  <div class="logo">
    <div class="logo-icon">🦅</div>
    <div>
      <h1>Smart Money Radar</h1>
      <p>Real-time Solana token intelligence · Birdeye Data API</p>
    </div>
  </div>
  <div class="header-right">
    <div class="info">
      Updated: <span>{{ data.last_updated }}</span><br>
      API Calls: <span>{{ data.total_api_calls }}</span> &nbsp;·&nbsp; Tokens Scanned: <span>{{ data.tokens_scanned }}</span>
    </div>
    <div class="live-badge"><span class="live-dot"></span>&nbsp; LIVE &nbsp;·&nbsp; Next refresh in <span id="countdown" style="font-family:'DM Mono',monospace;">3:00</span></div>
  </div>
</header>

<!-- Stats Bar -->
<div class="stats-bar">
  <div class="stat s1"><div class="stat-value">{{ data.total_api_calls }}</div><div class="stat-label">Total API Calls</div></div>
  <div class="stat s2"><div class="stat-value">{{ data.tokens_scanned }}</div><div class="stat-label">Tokens Scanned</div></div>
  <div class="stat s3"><div class="stat-value">{{ data.alpha_signals | length }}</div><div class="stat-label">Alpha Signals</div></div>
  <div class="stat s4"><div class="stat-value">{{ smart_wallets | length }}</div><div class="stat-label">Wallets Tracked</div></div>
  <div class="stat s5"><div class="stat-value">{{ data.all_tokens | selectattr('score','ge',40) | list | length }}</div><div class="stat-label">Watch Signals</div></div>
</div>

<!-- Tabs -->
<div class="tabs">
  <button class="tab active" onclick="showTab('radar', this)">📡 Live Radar</button>
  <button class="tab" onclick="showTab('leaderboard', this)">🏆 Leaderboard</button>
  <button class="tab" onclick="showTab('wallets', this)">🧠 Smart Wallets</button>
  <button class="tab" onclick="showTab('search', this)">🔎 Token Search</button>
  <button class="tab" onclick="showTab('tracker', this)">👁️ Wallet Tracker</button>
  <button class="tab" onclick="showTab('how', this)">❓ How It Works</button>
</div>


<!-- ══════════════ TAB 1: LIVE RADAR ══════════════ -->
<div id="tab-radar" class="panel active">

  {% if data.alpha_signals %}
  <div class="section">
    <div class="section-header">
      <h2>🚨 Alpha Signals — Smart Money Detected</h2>
      <span class="badge">{{ data.alpha_signals | length }}</span>
    </div>
    <div class="token-grid">
      {% for token in data.alpha_signals | reverse %}
      <div class="token-card alpha">
        <div class="card-top">
          <div><div class="token-symbol">${{ token.symbol }}</div><div class="token-name">{{ token.name }}</div></div>
          <div class="score-pill high">{{ token.score }}/100</div>
        </div>
        <div class="score-bar"><div class="score-fill high" style="width:{{ token.score }}%"></div></div>
        <div class="breakdown">
          <div class="bd-item"><div class="bd-val {% if token.breakdown.smart_money >= 24 %}good{% elif token.breakdown.smart_money >= 10 %}mid{% else %}bad{% endif %}">{{ token.breakdown.smart_money }}</div><div class="bd-lbl">Smart$</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.security >= 20 %}good{% elif token.breakdown.security >= 10 %}mid{% else %}bad{% endif %}">{{ token.breakdown.security }}</div><div class="bd-lbl">Safety</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.momentum >= 13 %}good{% elif token.breakdown.momentum >= 6 %}mid{% else %}bad{% endif %}">{{ token.breakdown.momentum }}</div><div class="bd-lbl">Momentum</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.holder_distribution >= 7 %}good{% elif token.breakdown.holder_distribution >= 4 %}mid{% else %}bad{% endif %}">{{ token.breakdown.holder_distribution }}</div><div class="bd-lbl">Holders</div></div>
        </div>
        {% if token.smart_buyers %}<div class="sm-tags">{% for w in token.smart_buyers %}<span class="sm-tag">🧠 {{ w }}</span>{% endfor %}</div>{% endif %}
        <div class="card-footer">
          <div class="meta">Price: <span>${{ "%.8f" | format(token.price | float) }}</span> · Liq: <span>${{ "{:,.0f}".format(token.liquidity | float) }}</span></div>
          <button class="chart-btn" onclick="openChart('{{ token.address }}', '{{ token.symbol }}')">📈 Chart</button>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  <div class="divider"></div>
  {% endif %}

  <div class="section">
    <div class="section-header">
      <h2>All Scanned Tokens</h2>
      <span class="badge">{{ data.all_tokens | length }}</span>
      <div style="display:flex;gap:8px;margin-left:auto;">
        <button class="filter-btn active" onclick="filterTokens('all', this)">All</button>
        <button class="filter-btn f-high" onclick="filterTokens('high', this)">🟢 Alpha</button>
        <button class="filter-btn f-mid"  onclick="filterTokens('mid',  this)">🟡 Watch</button>
        <button class="filter-btn f-low"  onclick="filterTokens('low',  this)">🔴 Low</button>
      </div>
    </div>
    {% if not data.all_tokens %}
    <div class="empty"><h3>Waiting for data...</h3><p>Make sure radar.py is running in another terminal.</p></div>
    {% else %}
    <div class="token-grid" id="token-all-grid">
      {% for token in data.all_tokens | reverse %}
      {% if token.score >= threshold %}{% set tier="alpha" %}{% set pill="high" %}{% set fill="high" %}
      {% elif token.score >= 40 %}{% set tier="watch" %}{% set pill="mid" %}{% set fill="mid" %}
      {% else %}{% set tier="" %}{% set pill="low" %}{% set fill="low" %}{% endif %}
      <div class="token-card {{ tier }}">
        <div class="card-top">
          <div><div class="token-symbol">${{ token.symbol }}</div><div class="token-name">{{ token.name }}</div></div>
          <div class="score-pill {{ pill }}">{{ token.score }}/100</div>
        </div>
        <div class="score-bar"><div class="score-fill {{ fill }}" style="width:{{ token.score }}%"></div></div>
        <div class="breakdown">
          <div class="bd-item"><div class="bd-val {% if token.breakdown.smart_money >= 24 %}good{% elif token.breakdown.smart_money >= 10 %}mid{% else %}bad{% endif %}">{{ token.breakdown.smart_money }}</div><div class="bd-lbl">Smart$</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.security >= 20 %}good{% elif token.breakdown.security >= 10 %}mid{% else %}bad{% endif %}">{{ token.breakdown.security }}</div><div class="bd-lbl">Safety</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.momentum >= 13 %}good{% elif token.breakdown.momentum >= 6 %}mid{% else %}bad{% endif %}">{{ token.breakdown.momentum }}</div><div class="bd-lbl">Momentum</div></div>
          <div class="bd-item"><div class="bd-val {% if token.breakdown.holder_distribution >= 7 %}good{% elif token.breakdown.holder_distribution >= 4 %}mid{% else %}bad{% endif %}">{{ token.breakdown.holder_distribution }}</div><div class="bd-lbl">Holders</div></div>
        </div>
        {% if token.smart_buyers %}<div class="sm-tags">{% for w in token.smart_buyers %}<span class="sm-tag">🧠 {{ w }}</span>{% endfor %}</div>{% endif %}
        <div class="card-footer">
          <div class="meta">Price: <span>${{ "%.8f" | format(token.price | float) }}</span> · Liq: <span>${{ "{:,.0f}".format(token.liquidity | float) }}</span></div>
          <button class="chart-btn" onclick="openChart('{{ token.address }}', '{{ token.symbol }}')">📈 Chart</button>
        </div>
      </div>
      {% endfor %}
    </div>
    {% endif %}
  </div>
</div>


<!-- ══════════════ TAB 2: LEADERBOARD ══════════════ -->
<div id="tab-leaderboard" class="panel">
  <div class="section">
    <div class="section-header">
      <h2>🏆 Smart Money Wallet Leaderboard</h2>
      <span class="badge">{{ smart_wallets | length }} wallets</span>
    </div>
    <p style="font-size:0.82rem;color:var(--muted);margin-bottom:24px;max-width:640px;">
      Ranked by how many trending tokens each wallet bought <strong style="color:var(--text)">before they blew up</strong>.
      The higher the rank, the more consistently this wallet gets in early. These are the wallets the radar watches most closely.
    </p>
    {% if smart_wallets %}
    <table class="lb-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Wallet Address</th>
          <th>Early Hits</th>
          <th>Tokens Caught Early</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {% for w in smart_wallets %}
        <tr>
          <td>
            {% if loop.index == 1 %}<span class="rank-medal">🥇</span>
            {% elif loop.index == 2 %}<span class="rank-medal">🥈</span>
            {% elif loop.index == 3 %}<span class="rank-medal">🥉</span>
            {% else %}<span class="rank-num">#{{ loop.index }}</span>{% endif %}
          </td>
          <td><span class="lb-addr">{{ w.address }}</span></td>
          <td><span class="lb-hits">{{ w.hits }}×</span></td>
          <td>
            <div class="lb-tokens">
              {% set seen = [] %}
              {% for t in w.tokens %}{% if t not in seen %}{% if seen.append(t) %}{% endif %}<span class="lb-token">${{ t }}</span>{% endif %}{% endfor %}
            </div>
          </td>
          <td>
            <button class="lb-track-btn" onclick="trackWallet('{{ w.address }}')">👁️ Track</button>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty"><h3>No wallets yet</h3><p>Keep radar.py running — wallets are identified on startup.</p></div>
    {% endif %}
  </div>
</div>


<!-- ══════════════ TAB 3: SMART WALLETS ══════════════ -->
<div id="tab-wallets" class="panel">
  <div class="section">
    <div class="section-header">
      <h2>🧠 Tracked Smart Money Wallets</h2>
      <span class="badge">{{ smart_wallets | length }}</span>
    </div>
    <p style="font-size:0.83rem;color:var(--muted);margin-bottom:24px;max-width:620px;">
      These wallets were identified by analyzing the earliest buyers of trending Solana tokens.
      Any wallet that appeared early across <strong style="color:var(--text)">2 or more</strong> trending tokens
      is flagged as smart money and actively monitored.
    </p>
    {% if smart_wallets %}
    <div class="wallet-grid">
      {% for wallet in smart_wallets %}
      <div class="wallet-card">
        <div class="wallet-card-top">
          <div class="wallet-full">{{ wallet.address }}</div>
          <div class="hit-badge">{{ wallet.hits }}×</div>
        </div>
        <div>
          <div style="font-size:0.7rem;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.08em;">Early bought these trending tokens:</div>
          <div class="wallet-tokens">
            {% set seen = [] %}
            {% for t in wallet.tokens %}{% if t not in seen %}{% if seen.append(t) %}{% endif %}<span class="wtoken-tag">${{ t }}</span>{% endif %}{% endfor %}
          </div>
        </div>
        <button class="wallet-track-btn" onclick="trackWallet('{{ wallet.address }}')">🔍 Track this wallet</button>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="empty"><h3>No wallets identified yet</h3><p>Keep radar.py running — wallets are built on startup.</p></div>
    {% endif %}
  </div>
</div>


<!-- ══════════════ TAB 4: TOKEN SEARCH ══════════════ -->
<div id="tab-search" class="panel">
  <div class="section">
    <div class="section-header"><h2>🔎 Token Search</h2></div>
    <p style="font-size:0.82rem;color:var(--muted);margin-bottom:20px;max-width:580px;">
      Look up any Solana token by its contract address. Get live price, volume, market cap, liquidity,
      and see if any smart money wallets are involved. Then open its full price chart in one click.
    </p>
    <div class="search-box">
      <input type="text" id="token-input" placeholder="Paste token contract address (e.g. So11111111111111111111111111111111111111112)" />
      <button class="search-btn" onclick="searchToken()">Search →</button>
    </div>
    <div id="token-loading" class="loading" style="display:none;">⏳ Fetching token data from Birdeye...</div>
    <div id="token-error" class="error-msg" style="display:none;"></div>
    <div id="token-detail" class="token-detail">
      <div class="detail-card">
        <div class="detail-header">
          <div>
            <div class="detail-sym" id="d-symbol"></div>
            <div class="detail-name" id="d-name"></div>
            <div class="detail-addr" id="d-addr"></div>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="birdeye-btn" id="d-chart-btn" onclick="">📈 Open Chart</button>
            <a class="birdeye-btn" id="d-birdeye-link" href="#" target="_blank">🦅 View on Birdeye ↗</a>
          </div>
        </div>
        <div id="d-sm-notice" class="sm-detected" style="display:none;">
          🧠 <strong>Smart Money Detected</strong> — one or more tracked wallets have been active with this token.
        </div>
        <div class="detail-stats">
          <div class="detail-stat"><div class="detail-stat-val" id="d-price">—</div><div class="detail-stat-lbl">Price (USD)</div></div>
          <div class="detail-stat"><div class="detail-stat-val" id="d-mc">—</div><div class="detail-stat-lbl">Market Cap</div></div>
          <div class="detail-stat"><div class="detail-stat-val" id="d-liq">—</div><div class="detail-stat-lbl">Liquidity</div></div>
          <div class="detail-stat"><div class="detail-stat-val" id="d-vol">—</div><div class="detail-stat-lbl">24h Volume</div></div>
          <div class="detail-stat"><div class="detail-stat-val" id="d-change">—</div><div class="detail-stat-lbl">24h Change</div></div>
          <div class="detail-stat"><div class="detail-stat-val" id="d-holders">—</div><div class="detail-stat-lbl">Holders</div></div>
        </div>
      </div>
    </div>
  </div>
</div>


<!-- ══════════════ TAB 5: WALLET TRACKER ══════════════ -->
<div id="tab-tracker" class="panel">
  <div class="section">
    <div class="section-header"><h2>👁️ Wallet Activity Tracker</h2></div>
    <p style="font-size:0.83rem;color:var(--muted);margin-bottom:20px;max-width:600px;">
      Enter any Solana wallet address to see its smart money profile — which trending tokens it bought early and how many times it's been detected as an early buyer.
      Click "Track this wallet" from the Leaderboard or Smart Wallets tab to auto-fill.
    </p>
    <div class="search-box">
      <input type="text" id="wallet-input" placeholder="Enter Solana wallet address..." />
      <button class="search-btn" onclick="lookupWallet()">Track Wallet →</button>
    </div>
    <div id="wallet-result" class="wallet-result">
      <div id="wallet-loading" class="loading" style="display:none;">⏳ Looking up wallet...</div>
      <div id="wallet-error" class="error-msg" style="display:none;"></div>
      <div id="wallet-data" style="display:none;">
        <div id="not-sm-notice" class="not-sm-notice" style="display:none;">
          ⚠️ This wallet is <strong>not in our smart money list</strong> — it hasn't been detected as an early buyer across multiple trending tokens.
        </div>
        <div class="wallet-header">
          <div>
            <div style="font-size:0.72rem;color:var(--muted);margin-bottom:4px;">TRACKING WALLET</div>
            <div class="wallet-addr" id="wallet-display"></div>
          </div>
          <div class="wallet-stats">
            <div class="wstat"><div class="wval" id="tx-count">—</div><div class="wlbl">Early Hits</div></div>
            <div class="wstat"><div class="wval" id="token-count">—</div><div class="wlbl">Tokens</div></div>
          </div>
        </div>
        <table class="tx-table">
          <thead><tr><th>Token</th><th>Type</th><th>Times Detected</th><th>Classification</th><th>Context</th></tr></thead>
          <tbody id="tx-body"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>


<!-- ══════════════ TAB 6: HOW IT WORKS ══════════════ -->
<div id="tab-how" class="panel">
  <div class="section">
    <div class="section-header"><h2>❓ How Smart Money Radar Works</h2></div>
    <div class="how-grid">
      <div class="how-card c1"><div class="how-icon">📈</div><h3>Step 1 — Find Trending Tokens</h3><p>On startup, the radar pulls the top trending tokens on Solana using Birdeye's <code>/defi/token_trending</code> endpoint. These are tokens that are already gaining momentum.</p></div>
      <div class="how-card c2"><div class="how-icon">🔍</div><h3>Step 2 — Identify Smart Money</h3><p>For each trending token, we look at the very <strong>earliest buyers</strong>. Any wallet that appeared early across 2 or more trending tokens is flagged as "smart money" and added to our watchlist.</p></div>
      <div class="how-card c3"><div class="how-icon">🆕</div><h3>Step 3 — Monitor Continuously</h3><p>Every 3 minutes, the radar re-scans trending tokens and checks each one for smart money wallet activity using Birdeye's transaction API.</p></div>
      <div class="how-card c4"><div class="how-icon">🧮</div><h3>Step 4 — Score Every Token</h3><p>Each token gets a composite score 0–100 across 4 signals. Tokens scoring 60+ trigger an <strong>Alpha Signal</strong> and a Telegram notification.</p></div>
      <div class="how-card c5"><div class="how-icon">🚨</div><h3>Step 5 — Alert Before It Trends</h3><p>Alpha tokens appear highlighted in green on the Live Radar. The goal: you see it <em>before</em> it becomes public knowledge — giving you a first-mover edge.</p></div>
    </div>
    <div class="divider" style="margin:0 0 28px 0;"></div>
    <div class="section-header"><h2>🧮 What Each Score Means</h2></div>
    <table class="score-table">
      <thead><tr><th>Signal</th><th>Max Points</th><th>What it measures</th><th>How it's calculated</th></tr></thead>
      <tbody>
        <tr><td><span class="score-name">🧠 Smart$</span></td><td><span class="score-pts">40 pts</span></td><td>Are proven early-winner wallets buying this token?</td><td>+20 per smart money wallet detected. Bonus for wallets with high hit counts across multiple trending tokens.</td></tr>
        <tr><td><span class="score-name">🛡️ Safety</span></td><td><span class="score-pts">30 pts</span></td><td>Is the token safe from rugs and scams?</td><td>Starts at 30. Deductions for freeze authority, mint authority, whale concentration. Defaults to 15 (neutral) on the free API plan.</td></tr>
        <tr><td><span class="score-name">⚡ Momentum</span></td><td><span class="score-pts">20 pts</span></td><td>Is price and volume growing?</td><td>Up to 10 pts for price change (>50% = full marks), up to 10 pts for 24h volume (>$100k = full marks).</td></tr>
        <tr><td><span class="score-name">👥 Holders</span></td><td><span class="score-pts">10 pts</span></td><td>Are tokens spread across many wallets or dominated by whales?</td><td>10 pts if top 10 holders own less than 30%. Scales to 1 pt if they own 70%+. High concentration = higher rug risk.</td></tr>
      </tbody>
    </table>
    <div style="margin-top:20px;background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:8px;padding:16px 20px;">
      <div style="font-family:'Syne',sans-serif;font-weight:700;color:#fff;margin-bottom:8px;">Score Bands</div>
      <div style="font-size:0.83rem;color:var(--muted);line-height:2.2;">
        🟢 <strong style="color:var(--accent)">60–100</strong> — Alpha Signal. Smart money detected. High priority.<br>
        🟡 <strong style="color:var(--warn)">40–59</strong> — Watch. Something interesting but not fully confirmed.<br>
        🔴 <strong style="color:var(--red)">0–39</strong> — Low signal. No smart money interest detected.
      </div>
    </div>
  </div>
</div>


<!-- CHART MODAL -->
<div class="modal-overlay" id="chart-modal">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-title" id="modal-title">Token Chart</div>
      <button class="modal-close" onclick="closeChart()">✕</button>
    </div>
    <div class="modal-body">
      <iframe id="chart-iframe" src="" allowfullscreen></iframe>
    </div>
  </div>
</div>


<footer>
  <div class="left">Built for <strong>Birdeye Data BIP Competition</strong> · Sprint 4 · May 2026</div>
  <div class="tag">#BirdeyeAPI · @birdeye_data</div>
</footer>

<script>
  // ── Tab switching ──────────────────────────────────
  function showTab(name, el) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    el.classList.add('active');
  }

  // ── Token filter ───────────────────────────────────
  function filterTokens(tier, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#token-all-grid .token-card').forEach(card => {
      if (tier === 'all') { card.style.display = ''; return; }
      if (tier === 'high') { card.style.display = card.classList.contains('alpha') ? '' : 'none'; return; }
      if (tier === 'mid')  { card.style.display = card.classList.contains('watch') ? '' : 'none'; return; }
      if (tier === 'low')  { card.style.display = (!card.classList.contains('alpha') && !card.classList.contains('watch')) ? '' : 'none'; }
    });
  }

  // ── Chart modal ────────────────────────────────────
  function openChart(address, symbol) {
    document.getElementById('modal-title').textContent = '$' + symbol + ' — Live Price Chart';
    document.getElementById('chart-iframe').src = 'https://birdeye.so/token/' + address + '?chain=solana';
    document.getElementById('chart-modal').classList.add('open');
  }
  function closeChart() {
    document.getElementById('chart-modal').classList.remove('open');
    document.getElementById('chart-iframe').src = '';
  }
  // Close modal on overlay click
  document.getElementById('chart-modal').addEventListener('click', function(e) {
    if (e.target === this) closeChart();
  });

  // ── Token Search ───────────────────────────────────
  let currentSearchAddr = '';
  function fmt(n) {
    n = parseFloat(n) || 0;
    if (n >= 1e9) return (n/1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n/1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
    return n.toFixed(2);
  }

  async function searchToken() {
    const addr = document.getElementById('token-input').value.trim();
    if (!addr) return;
    currentSearchAddr = addr;

    const loading = document.getElementById('token-loading');
    const error   = document.getElementById('token-error');
    const detail  = document.getElementById('token-detail');

    loading.style.display = 'block';
    error.style.display   = 'none';
    detail.classList.remove('visible');

    try {
      const res  = await fetch('/api/token?address=' + encodeURIComponent(addr));
      const json = await res.json();
      loading.style.display = 'none';

      if (json.error) { error.style.display = 'block'; error.textContent = '⚠️ ' + json.error; return; }

      const d = json.data;
      const symbol = d.symbol || '???';

      document.getElementById('d-symbol').textContent = '$' + symbol;
      document.getElementById('d-name').textContent   = d.name || '';
      document.getElementById('d-addr').textContent   = addr;
      document.getElementById('d-price').textContent  = '$' + parseFloat(d.price||0).toFixed(8);
      document.getElementById('d-mc').textContent     = '$' + fmt(d.mc||0);
      document.getElementById('d-liq').textContent    = '$' + fmt(d.liquidity||0);
      document.getElementById('d-vol').textContent    = '$' + fmt(d.v24hUSD||0);
      document.getElementById('d-holders').textContent = fmt(d.holder||0);

      const chg   = parseFloat(d.priceChange24hPercent||0);
      const chgEl = document.getElementById('d-change');
      chgEl.textContent  = (chg >= 0 ? '+' : '') + chg.toFixed(2) + '%';
      chgEl.style.color  = chg >= 0 ? 'var(--accent)' : 'var(--red)';

      document.getElementById('d-birdeye-link').href  = 'https://birdeye.so/token/' + addr + '?chain=solana';
      document.getElementById('d-chart-btn').onclick  = () => openChart(addr, symbol);
      document.getElementById('d-sm-notice').style.display = json.is_smart_money ? 'block' : 'none';

      detail.classList.add('visible');
    } catch(e) {
      loading.style.display = 'none';
      error.style.display   = 'block';
      error.textContent     = '⚠️ Failed to fetch token data. Check the address and try again.';
    }
  }

  // ── Wallet Tracker ─────────────────────────────────
  function trackWallet(addr) {
    document.getElementById('wallet-input').value = addr;
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t  => t.classList.remove('active'));
    document.getElementById('tab-tracker').classList.add('active');
    document.querySelectorAll('.tab')[4].classList.add('active');
    lookupWallet();
  }

  async function lookupWallet() {
    const addr = document.getElementById('wallet-input').value.trim();
    if (!addr) return;

    const result  = document.getElementById('wallet-result');
    const loading = document.getElementById('wallet-loading');
    const error   = document.getElementById('wallet-error');
    const dataDiv = document.getElementById('wallet-data');
    const notice  = document.getElementById('not-sm-notice');

    result.classList.add('visible');
    loading.style.display = 'block';
    error.style.display   = 'none';
    dataDiv.style.display = 'none';

    try {
      const res  = await fetch('/api/wallet?address=' + encodeURIComponent(addr));
      const json = await res.json();
      loading.style.display = 'none';

      if (json.error) { error.style.display = 'block'; error.textContent = '⚠️ ' + json.error; return; }

      document.getElementById('wallet-display').textContent = addr;
      const tbody = document.getElementById('tx-body');
      tbody.innerHTML = '';

      if (json.known) {
        notice.style.display = 'none';
        document.getElementById('tx-count').textContent   = json.hits + '×';
        document.getElementById('token-count').textContent = [...new Set(json.tokens)].length;

        const uniqueTokens = [...new Set(json.tokens)];
        uniqueTokens.forEach(token => {
          const count = json.tokens.filter(t => t === token).length;
          tbody.innerHTML += `
            <tr>
              <td><div class="tx-sym">$${token}</div><div class="tx-addr">Trending Solana token</div></td>
              <td><span class="tx-type-buy">▲ EARLY BUY</span></td>
              <td style="font-family:'DM Mono',monospace;">${count}× detected</td>
              <td style="color:var(--accent);font-weight:600;">✅ Smart Money</td>
              <td style="color:var(--muted);font-size:0.72rem;">Bought before trending</td>
            </tr>`;
        });
      } else {
        notice.style.display = 'block';
        document.getElementById('tx-count').textContent    = '0';
        document.getElementById('token-count').textContent = '0';
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--muted);">No smart money activity found for this wallet.</td></tr>`;
      }
      dataDiv.style.display = 'block';
    } catch(e) {
      loading.style.display = 'none';
      error.style.display   = 'block';
      error.textContent     = '⚠️ Failed to lookup wallet. Try again.';
    }
  }

  // ── Countdown synced to backend ────────────────────
  const nextScanAt = {{ next_scan_at }};
  const safeNext = nextScanAt > Date.now()/1000 ? nextScanAt : Date.now()/1000 + 180;
  function updateCountdown() {
    const remaining = Math.max(0, Math.floor(safeNext - Date.now() / 1000));
    const mins = Math.floor(remaining / 60);
    const secs = remaining % 60;
    const el = document.getElementById('countdown');
    if (el) el.textContent = mins + ':' + String(secs).padStart(2, '0');
    if (remaining <= 0) { setTimeout(() => window.location.reload(), 3000); return; }
    else setTimeout(updateCountdown, 1000);
  }
  updateCountdown();

  // Enter key support
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('wallet-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') lookupWallet(); });
    document.getElementById('token-input')?.addEventListener('keydown',  e => { if (e.key === 'Enter') searchToken(); });
  });
</script>
</body>
</html>
"""

@app.route("/")
def index():
    if not os.path.exists(RESULTS_FILE):
        data = {
            "last_updated": "Not yet — run radar.py first",
            "total_api_calls": 0,
            "tokens_scanned": 0,
            "alpha_signals": [],
            "all_tokens": []
        }
    else:
        with open(RESULTS_FILE) as f:
            data = json.load(f)

    smart_wallets = []
    if os.path.exists("wallet_stats.json"):
        with open("wallet_stats.json") as f:
            ws = json.load(f)
        for addr, info in ws.items():
            if info["hits"] >= 2:
                smart_wallets.append({
                    "address": addr,
                    "hits": info["hits"],
                    "tokens": info["tokens"]
                })
        smart_wallets.sort(key=lambda x: x["hits"], reverse=True)

    from config import ALERT_THRESHOLD
    next_scan_at = data.get("next_scan_at", pytime.time() + 180)
    return render_template_string(
        HTML, data=data, threshold=ALERT_THRESHOLD,
        smart_wallets=smart_wallets, next_scan_at=next_scan_at
    )


@app.route("/api/wallet")
def wallet_api():
    address = request.args.get("address", "").strip()
    if not address:
        return jsonify({"error": "No address provided"})
    if not os.path.exists("wallet_stats.json"):
        return jsonify({"error": "Wallet data not loaded yet. Make sure radar.py has run."})
    with open("wallet_stats.json") as f:
        ws = json.load(f)
    if address not in ws:
        return jsonify({
            "known": False,
            "address": address,
            "message": "Not in smart money list.",
            "transactions": []
        })
    info = ws[address]
    return jsonify({
        "known": True,
        "address": address,
        "hits": info["hits"],
        "tokens": info["tokens"],
        "transactions": []
    })


@app.route("/api/token")
def token_api():
    address = request.args.get("address", "").strip()
    if not address:
        return jsonify({"error": "No address provided"})
    try:
        from config import API_KEY
        headers = {"X-API-KEY": API_KEY, "accept": "application/json", "x-chain": "solana"}
        r = req.get(
            "https://public-api.birdeye.so/defi/token_overview",
            headers=headers, params={"address": address}, timeout=10
        )
        if r.status_code != 200:
            return jsonify({"error": f"Birdeye returned {r.status_code}: {r.text[:100]}"})
        d = r.json().get("data", {})

        # Check if any tracked smart money wallet has bought this token
        is_sm = False
        if os.path.exists("wallet_stats.json"):
            with open("wallet_stats.json") as f:
                ws = json.load(f)
            symbol = d.get("symbol", "")
            for info in ws.values():
                if symbol and symbol in info.get("tokens", []):
                    is_sm = True
                    break

        return jsonify({"data": d, "is_smart_money": is_sm})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("🌐 Dashboard running at: http://localhost:5000")
    print("   Make sure radar.py is running in another terminal\n")
    app.run(debug=False, port=5000)