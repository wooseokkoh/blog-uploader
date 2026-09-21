/* 퀀트 시그널 대시보드 — signals.json 을 읽어 렌더링한다. */
'use strict';

const REGIME_STYLE = {
  RISK_ON:  { color: 'var(--ok)',     label: '위험선호' },
  NEUTRAL:  { color: 'var(--warn)',   label: '중립' },
  RISK_OFF: { color: 'var(--danger)', label: '위험회피' },
};

const ACTION_CLASS = {
  ACCUMULATE: 'b-buy',
  HOLD: 'b-hold',
  REDUCE: 'b-reduce',
  EXIT: 'b-exit',
};

const AXIS_LABEL = { trend: '지수 추세', volatility: '변동성', credit: '신용' };

const $ = (id) => document.getElementById(id);
const num = (v, d = 2) =>
  v === null || v === undefined || Number.isNaN(v) ? '—' : Number(v).toLocaleString('ko-KR', {
    minimumFractionDigits: d, maximumFractionDigits: d,
  });

let payload = null;
let filter = 'buy';

async function load() {
  try {
    const res = await fetch('data/signals.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    payload = await res.json();
    render();
  } catch (err) {
    $('stamp').textContent = '';
    $('status').innerHTML =
      `<span class="err">시그널을 불러오지 못했습니다 (${err.message}).</span><br>` +
      `<code>python -m engine.cli --source synthetic --out web/data</code> 로 데이터를 먼저 생성하세요.`;
  }
}

function render() {
  renderStamp();
  $('regime-card').hidden = false;
  renderRegime();
  $('filters').hidden = false;
  $('disclaimer').textContent = payload.disclaimer || '';
  renderList();
}

function isDemo() {
  return String(payload.market || '').endsWith('_DEMO');
}

function renderStamp() {
  const d = new Date(payload.generated_at);
  const when = Number.isNaN(d.getTime())
    ? payload.generated_at
    : d.toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' });
  $('stamp').textContent = `${payload.market} · ${when}`;
}

function renderRegime() {
  const r = payload.regime;
  const style = REGIME_STYLE[r.state] || { color: 'var(--muted)', label: r.state };
  $('regime-dot').style.background = style.color;
  $('regime-name').textContent = payload.regime_label || style.label;
  $('regime-score').textContent = `${Math.round(r.score * 100)}점 / 100`;

  $('regime-axes').innerHTML = Object.entries(r.components || {})
    .map(([key, val]) => {
      const cls = val === null ? 'na' : val ? 'on' : 'off';
      const mark = val === null ? '판정불가' : val ? '양호' : '불리';
      return `<span class="axis ${cls}">${AXIS_LABEL[key] || key} · ${mark}</span>`;
    })
    .join('');

  const banner = $('regime-banner');
  if (isDemo()) {
    banner.hidden = false;
    banner.innerHTML =
      '<strong>합성 데이터(데모)입니다.</strong> 실제 시세가 아니며 투자 판단에 쓸 수 없습니다.';
    banner.style.background = 'var(--danger)';
    banner.style.color = '#fff';
  } else if (r.state === 'RISK_OFF') {
    banner.hidden = false;
    banner.textContent = '위험회피 구간입니다. 점수가 높은 종목도 신규 진입 신호를 내지 않습니다.';
  } else {
    banner.hidden = true;
  }
}

function renderList() {
  const all = payload.signals || [];
  const shown = filter === 'buy' ? all.filter((s) => s.action === 'ACCUMULATE') : all;

  $('list').innerHTML = shown.map(card).join('');
  $('status').textContent = shown.length
    ? `${shown.length}건 표시 (전체 ${all.length}건 중)`
    : filter === 'buy'
      ? '현재 분할 매수 신호가 없습니다.'
      : '신호가 없습니다.';
}

function card(s) {
  const cls = ACTION_CLASS[s.action] || 'b-hold';
  const factors = Object.entries(s.factors || {})
    .map(([k, v]) => `<span>${k} ${Math.round(v)}</span>`)
    .join('');

  return `<section class="card">
    <div class="sig-head">
      <span class="sym">${s.symbol}</span>
      <span class="badge ${cls}">${s.action_label || s.action}</span>
    </div>
    <div class="score-row">
      <div class="meter"><span style="width:${Math.max(0, Math.min(100, s.score))}%"></span></div>
      <span class="score-val">${num(s.score, 0)}</span>
    </div>
    <p class="reason">${s.reason || ''}</p>
    <p class="reason">종가 ${num(s.last_close)} · 기준일 ${s.as_of}</p>
    ${s.entry_plan ? plan(s) : ''}
    <div class="factors">${factors}</div>
  </section>`;
}

function plan(s) {
  const rows = s.entry_plan.tranches
    .map((t, i) => `<tr>
        <td>${i + 1}차 · ${t.note}</td>
        <td>${num(t.price)}</td>
        <td>${Math.round(t.weight * 100)}%</td>
      </tr>`)
    .join('');

  return `<table>
      <thead><tr><th>${s.entry_plan.method}</th><th>매수가</th><th>배분</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <dl class="kv">
      <div><dt>평균 진입가</dt><dd>${num(s.entry_plan.avg_entry)}</dd></div>
      <div><dt>손절가</dt><dd class="stop">${num(s.risk.stop_loss)}</dd></div>
      <div><dt>계좌 비중</dt><dd>${num(s.risk.position_size_pct, 1)}%</dd></div>
      <div><dt>최대 손실</dt><dd>${num(s.risk.max_loss_pct, 1)}%</dd></div>
    </dl>
    <p class="reason">유효 ${s.entry_plan.valid_until}까지 · ${s.entry_plan.invalidate_if}</p>`;
}

$('filters').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-filter]');
  if (!btn) return;
  filter = btn.dataset.filter;
  for (const b of $('filters').querySelectorAll('button')) {
    b.setAttribute('aria-pressed', String(b === btn));
  }
  renderList();
});

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

load();
