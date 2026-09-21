"""커맨드라인 진입점.

    python -m engine.cli --source yahoo --out web/data
    python -m engine.cli --source synthetic --limit 30   # 오프라인 검증
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import DEFAULT, Settings, RiskConfig, ScoreConfig
from .data.synthetic import SyntheticSource
from .data.universe import sp500, load_fallback
from .pipeline import run, write
from .scoring import ACCUMULATE


def _build_source(name: str, seed: int = 20260921, regime: str = "risk_on"):
    if name == "synthetic":
        return SyntheticSource(seed=seed, regime=regime)
    if name == "yahoo":
        from .data.us_equity import YahooSource

        return YahooSource()
    raise ValueError(f"알 수 없는 소스: {name}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="미국 주식 퀀트 시그널 생성")
    ap.add_argument("--source", default="yahoo", choices=["yahoo", "synthetic"])
    ap.add_argument("--out", default="web/data", help="출력 디렉터리")
    ap.add_argument("--limit", type=int, default=0, help="유니버스 상한 (0=전체)")
    ap.add_argument("--top-n", type=int, default=DEFAULT.top_n, help="출력할 상위 종목 수")
    ap.add_argument("--risk-pct", type=float, default=DEFAULT.risk.account_risk_pct,
                    help="1회 매매 감내 손실률(%%)")
    ap.add_argument("--offline-universe", action="store_true",
                    help="S&P500 목록을 원격 조회하지 않고 폴백 사용")
    ap.add_argument("--seed", type=int, default=20260921,
                    help="합성 데이터 시드 (--source synthetic 에서만 사용)")
    ap.add_argument("--demo-regime", default="risk_on",
                    choices=["risk_on", "risk_off", "random"],
                    help="합성 데이터의 시장 국면 (--source synthetic 에서만 사용)")
    ap.add_argument("--dry-run", action="store_true", help="파일로 쓰지 않고 요약만 출력")
    args = ap.parse_args(argv)

    if args.source == "synthetic":
        symbols = [f"S{i:02d}" for i in range(args.limit or 40)]
    else:
        symbols = load_fallback() if args.offline_universe else sp500()
        if args.limit:
            symbols = symbols[: args.limit]

    settings = Settings(
        regime=DEFAULT.regime,
        factors=DEFAULT.factors,
        risk=RiskConfig(account_risk_pct=args.risk_pct),
        score=ScoreConfig(),
        top_n=args.top_n,
    )

    # 합성 데이터는 반드시 DEMO 로 라벨링한다. 대시보드에서 실제 신호와
    # 구분되지 않으면 가짜 가격을 진짜로 오인할 수 있다.
    market = "US_EQUITY_DEMO" if args.source == "synthetic" else "US_EQUITY"

    print(f"[1/3] 유니버스 {len(symbols)}종목, 소스={args.source}, 마켓={market}")
    payload = run(
        _build_source(args.source, args.seed, args.demo_regime),
        symbols,
        settings,
        market=market,
    )

    r = payload["regime"]
    print(f"[2/3] 레짐: {payload['regime_label']} ({r['state']}, {r['score']:.2f}) {r['components']}")
    for note in r.get("notes", []):
        print(f"       ! {note}")

    u = payload["universe"]
    buys = [s for s in payload["signals"] if s["action"] == ACCUMULATE]
    print(f"[3/3] 데이터확보 {u['with_data']} → 유동성통과 {u['after_liquidity']} "
          f"→ 신호 {u['emitted']}건 (분할매수 {len(buys)}건)")

    for s in buys[:5]:
        t = s["entry_plan"]["tranches"][0]
        print(f"       {s['symbol']:<6} 점수 {s['score']:>5.1f}  1차매수 {t['price']}  "
              f"손절 {s['risk']['stop_loss']}  비중 {s['risk']['position_size_pct']}%")

    if args.dry_run:
        print("(dry-run: 파일 미기록)")
        return 0

    path = write(payload, Path(args.out))
    print(f"저장: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
