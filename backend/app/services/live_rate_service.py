from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import urllib.request

from sqlalchemy.orm import Session

from app.models.gold_rate import GoldRate
from app.models.metal_type import MetalType
from app.models.purity import Purity
from app.models.silver_rate import SilverRate
from app.models.system_setting import SystemSetting

TROY_OUNCE_GRAMS = 31.1034768
CACHE_TTL_SECONDS = 45
MARKET_CACHE_KEY = "live_market_rates_cache"
CONFIG_KEY = "live_rates_config"

DEFAULT_RATES: Dict[str, float] = {
    "gold24k": 79100.0,
    "gold22k": 72500.0,
    "gold20k": 65900.0,
    "gold18k": 59300.0,
    "gold14k": 46100.0,
    "silver": 90000.0,
}

_MEM_CACHE: Dict[str, Any] = {"ts": 0.0, "data": None}


def _http_get_json(url: str, timeout: float = 6.0) -> Optional[Dict[str, Any]]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_gold_api_usd(symbol: str) -> Optional[float]:
    try:
        data = _http_get_json(f"https://api.gold-api.com/price/{symbol}")
        price = float(data.get("price") or 0)
        return price if price > 0 else None
    except Exception:
        return None


def _fetch_yahoo_price(ticker: str) -> Optional[float]:
    try:
        data = _http_get_json(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        )
        meta = (data.get("chart", {}).get("result") or [{}])[0].get("meta", {})
        price = float(meta.get("regularMarketPrice") or 0)
        return price if price > 0 else None
    except Exception:
        return None


def _fetch_usd_inr() -> Optional[float]:
    rate = _fetch_yahoo_price("USDINR=X")
    if rate and rate > 10:
        return rate
    try:
        data = _http_get_json("https://open.er-api.com/v6/latest/USD")
        inr = float((data.get("rates") or {}).get("INR") or 0)
        return inr if inr > 10 else None
    except Exception:
        return None


def _compute_derived_gold_rates(gold24k_10g: float) -> Dict[str, float]:
    base = round(float(gold24k_10g))
    return {
        "gold24k": float(base),
        "gold22k": float(round(base * 0.916)),
        "gold20k": float(round(base * 0.833)),
        "gold18k": float(round(base * 0.750)),
        "gold14k": float(round(base * 0.585)),
    }


def _read_setting_json(db: Session, key: str, default: Any) -> Any:
    row = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()
    if not row or not row.setting_value:
        return default
    try:
        return json.loads(row.setting_value)
    except Exception:
        return default


def _write_setting_json(db: Session, key: str, value: Any, description: str) -> None:
    payload = json.dumps(value)
    row = db.query(SystemSetting).filter(SystemSetting.setting_key == key).first()
    if row:
        row.setting_value = payload
    else:
        db.add(SystemSetting(setting_key=key, setting_value=payload, description=description))
    db.commit()


def _load_config(db: Session) -> Dict[str, Any]:
    cfg = _read_setting_json(db, CONFIG_KEY, {})
    if not isinstance(cfg, dict):
        cfg = {}
    active = dict(DEFAULT_RATES)
    if isinstance(cfg.get("active_rates"), dict):
        for k in DEFAULT_RATES:
            val = cfg["active_rates"].get(k)
            if val is not None and float(val) > 0:
                active[k] = float(val)
    custom_rates = cfg.get("custom_rates") if isinstance(cfg.get("custom_rates"), list) else []
    return {
        "auto_sync_live": bool(cfg.get("auto_sync_live", True)),
        "active_rates": active,
        "custom_rates": custom_rates,
        "updated_at": cfg.get("updated_at"),
    }


def _fetch_live_spot_inr() -> Optional[Dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_xau = pool.submit(_fetch_gold_api_usd, "XAU")
        f_xag = pool.submit(_fetch_gold_api_usd, "XAG")
        f_fx = pool.submit(_fetch_usd_inr)

        xau_usd = f_xau.result()
        xag_usd = f_xag.result()
        usd_inr = f_fx.result()

    source_parts: List[str] = []
    if xau_usd is None:
        xau_usd = _fetch_yahoo_price("GC=F")
        if xau_usd:
            source_parts.append("Yahoo GC=F")
    else:
        source_parts.append("GoldAPI XAU")

    if xag_usd is None:
        xag_usd = _fetch_yahoo_price("SI=F")
        if xag_usd:
            source_parts.append("Yahoo SI=F")
    else:
        source_parts.append("GoldAPI XAG")

    if not (xau_usd and xag_usd and usd_inr):
        return None

    gold24k_10g = round((xau_usd * usd_inr / TROY_OUNCE_GRAMS) * 10.0)
    silver_kg = round((xag_usd * usd_inr / TROY_OUNCE_GRAMS) * 1000.0)
    rates = {**_compute_derived_gold_rates(gold24k_10g), "silver": float(silver_kg)}

    return {
        **rates,
        "xau_usd": round(xau_usd, 2),
        "xag_usd": round(xag_usd, 3),
        "usd_inr": round(usd_inr, 3),
        "source": " + ".join(source_parts) + " (INR)",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _sync_db_rate_tables(db: Session, rates: Dict[str, float]) -> None:
    """Keep legacy GoldRate/SilverRate rows updated for latest purity lookup & dashboard compatibility."""
    gold_map = {
        "24K": rates.get("gold24k"),
        "22K": rates.get("gold22k"),
        "20K": rates.get("gold20k"),
        "18K": rates.get("gold18k"),
        "14K": rates.get("gold14k"),
    }
    gold_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold").all()
    silver_purities = db.query(Purity).join(MetalType).filter(MetalType.name == "Silver").all()

    changed = False
    for p in gold_purities:
        val = gold_map.get(p.karat_name)
        if not val:
            continue
        latest = db.query(GoldRate).filter(GoldRate.purity_id == p.id).order_by(GoldRate.effective_datetime.desc()).first()
        if not latest or abs(float(latest.rate_per_gram) - float(val)) >= 1.0:
            db.add(GoldRate(purity_id=p.id, rate_per_gram=float(val)))
            changed = True

    silver_kg = float(rates.get("silver") or 0)
    if silver_kg > 0:
        for p in silver_purities:
            target = float(round(silver_kg * 0.925)) if "925" in (p.karat_name or "") else silver_kg
            if (p.karat_name or "").lower() == "custom":
                continue
            latest = db.query(SilverRate).filter(SilverRate.purity_id == p.id).order_by(SilverRate.effective_datetime.desc()).first()
            if not latest or abs(float(latest.rate_per_gram) - target) >= 1.0:
                db.add(SilverRate(purity_id=p.id, rate_per_gram=target))
                changed = True

    if changed:
        db.commit()


def get_live_rates_status(db: Session, force_refresh: bool = False) -> Dict[str, Any]:
    now = time.time()
    market_data: Optional[Dict[str, Any]] = None
    is_offline_fallback = False

    if not force_refresh and _MEM_CACHE["data"] and (now - _MEM_CACHE["ts"]) < CACHE_TTL_SECONDS:
        market_data = _MEM_CACHE["data"]
    else:
        live = _fetch_live_spot_inr()
        if live:
            market_data = live
            _MEM_CACHE["ts"] = now
            _MEM_CACHE["data"] = live
            _write_setting_json(db, MARKET_CACHE_KEY, live, "Last fetched live bullion market rates")
        else:
            is_offline_fallback = True
            cached = _read_setting_json(db, MARKET_CACHE_KEY, None)
            if isinstance(cached, dict) and cached.get("gold24k"):
                market_data = cached
            elif _MEM_CACHE["data"]:
                market_data = _MEM_CACHE["data"]

    cfg = _load_config(db)

    if not market_data:
        market_data = {
            **cfg["active_rates"],
            "source": "Offline / Stored Rate",
            "fetched_at": cfg.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        }
        is_offline_fallback = True

    active_rates = dict(cfg["active_rates"])
    if cfg["auto_sync_live"] and not is_offline_fallback:
        for k in DEFAULT_RATES:
            if market_data.get(k):
                active_rates[k] = float(market_data[k])
        _sync_db_rate_tables(db, active_rates)

    return {
        "auto_sync_live": cfg["auto_sync_live"],
        "is_offline_fallback": is_offline_fallback,
        "market_rates": {k: float(market_data.get(k, DEFAULT_RATES[k])) for k in DEFAULT_RATES},
        "market_meta": {
            "xau_usd": market_data.get("xau_usd"),
            "xag_usd": market_data.get("xag_usd"),
            "usd_inr": market_data.get("usd_inr"),
            "source": market_data.get("source", "Live Market API"),
            "fetched_at": market_data.get("fetched_at"),
        },
        "active_rates": active_rates,
        "custom_rates": cfg["custom_rates"],
        "updated_at": market_data.get("fetched_at") if cfg["auto_sync_live"] else (cfg.get("updated_at") or market_data.get("fetched_at")),
    }


def save_rates_config(
    db: Session,
    *,
    auto_sync_live: Optional[bool] = None,
    active_rates: Optional[Dict[str, float]] = None,
    custom_rates: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    cfg = _load_config(db)

    if auto_sync_live is not None:
        cfg["auto_sync_live"] = bool(auto_sync_live)

    if active_rates is not None:
        merged = dict(cfg["active_rates"])
        for k in DEFAULT_RATES:
            if k in active_rates and active_rates[k] is not None and float(active_rates[k]) > 0:
                merged[k] = float(active_rates[k])
        cfg["active_rates"] = merged
        _sync_db_rate_tables(db, merged)

    if custom_rates is not None:
        cleaned: List[Dict[str, Any]] = []
        for idx, item in enumerate(custom_rates):
            name = str(item.get("name") or "").strip()
            rate_val = float(item.get("rate") or 0)
            if not name or rate_val <= 0:
                continue
            metal = "Silver" if str(item.get("metal_type") or "").lower() == "silver" else "Gold"
            unit = "/ kg" if metal == "Silver" else "/ 10g"
            purity_pct = float(item.get("purity_percent") or (99.9 if metal == "Silver" else 91.6))
            cleaned.append({
                "id": str(item.get("id") or f"custom-{int(time.time() * 1000)}-{idx}"),
                "name": name,
                "metal_type": metal,
                "purity_percent": purity_pct,
                "rate": rate_val,
                "unit": unit,
            })
        cfg["custom_rates"] = cleaned

    cfg["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_setting_json(db, CONFIG_KEY, cfg, "Active live/custom metal rates configuration")
    return get_live_rates_status(db, force_refresh=False)
