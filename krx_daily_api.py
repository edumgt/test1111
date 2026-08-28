"""FastAPI service for KOSPI daily trading data from the KRX Data API."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


KRX_ENDPOINT = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
MAX_DAYS = 366
MAX_WORKERS = 5
KEY_FILE = Path(__file__).with_name(".key")
FRONTEND_DIR = Path(__file__).with_name("frontend")

app = FastAPI(
    title="KRX 유가증권 일별매매정보 API",
    description="KRX Data API에서 기간별 KOSPI 일별매매정보를 조회합니다.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class DateResult(BaseModel):
    bas_dd: str = Field(description="기준일자 (YYYYMMDD)")
    records: list[dict[str, Any]] = Field(description="해당 일자의 종목별 매매정보")


class DailyTradingResponse(BaseModel):
    from_date: str = Field(description="조회 시작일 (YYYYMMDD)")
    to_date: str = Field(description="조회 종료일 (YYYYMMDD)")
    trading_days: int = Field(description="데이터가 반환된 거래일 수")
    record_count: int = Field(description="반환된 전체 종목 레코드 수")
    data: list[DateResult]


def parse_date(value: str) -> date:
    """Accept YYYYMMDD and YYYY-MM-DD inputs."""
    normalized = value.replace("-", "")
    try:
        return datetime.strptime(normalized, "%Y%m%d").date()
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="날짜는 YYYYMMDD 또는 YYYY-MM-DD 형식이어야 합니다.",
        ) from exc


def format_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def get_krx_key() -> str:
    """Read the Codespaces-injected KRX_KEY first, then the local .key file."""
    key = os.getenv("KRX_KEY", "").strip()
    if key:
        return key

    try:
        for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("KRX-KEY="):
                key = line.partition("=")[2].strip()
                if key:
                    return key
    except FileNotFoundError:
        pass

    raise HTTPException(
        status_code=500,
        detail="KRX API 키가 없습니다. Codespaces secret KRX_KEY 환경변수 또는 .key의 KRX-KEY를 설정하세요.",
    )


def fetch_one_day(bas_dd: str, api_key: str) -> DateResult:
    query = urlencode({"basDd": bas_dd})
    request = Request(
        f"{KRX_ENDPOINT}?{query}",
        headers={"AUTH_KEY": api_key, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"KRX API HTTP 오류 ({bas_dd}): {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail=f"KRX API 연결 오류 ({bas_dd})") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"KRX API 응답 형식 오류 ({bas_dd})") from exc

    records = payload.get("OutBlock_1", [])
    if not isinstance(records, list):
        raise HTTPException(status_code=502, detail=f"KRX API 응답 구조 오류 ({bas_dd})")
    return DateResult(bas_dd=bas_dd, records=records)


def dates_between(from_date: date, to_date: date) -> list[str]:
    current = from_date
    dates: list[str] = []
    while current <= to_date:
        # Weekends do not have KRX trading data, so do not issue unnecessary requests.
        if current.weekday() < 5:
            dates.append(format_date(current))
        current += timedelta(days=1)
    return dates


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/v1/stocks/daily", response_model=DailyTradingResponse)
def get_daily_trading(
    from_: str = Query(..., alias="from", description="조회 시작일 (YYYYMMDD 또는 YYYY-MM-DD)"),
    to: str = Query(..., description="조회 종료일 (YYYYMMDD 또는 YYYY-MM-DD)"),
) -> DailyTradingResponse:
    start = parse_date(from_)
    end = parse_date(to)
    if start > end:
        raise HTTPException(status_code=422, detail="from은 to보다 늦을 수 없습니다.")
    if (end - start).days + 1 > MAX_DAYS:
        raise HTTPException(status_code=422, detail=f"조회 기간은 최대 {MAX_DAYS}일입니다.")

    api_key = get_krx_key()
    requested_dates = dates_between(start, end)
    results: dict[str, DateResult] = {}

    # A modest concurrency level keeps long period queries responsive without flooding KRX.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_one_day, bas_dd, api_key): bas_dd for bas_dd in requested_dates}
        for future in as_completed(futures):
            result = future.result()
            if result.records:
                results[result.bas_dd] = result

    data = [results[bas_dd] for bas_dd in sorted(results)]
    return DailyTradingResponse(
        from_date=format_date(start),
        to_date=format_date(end),
        trading_days=len(data),
        record_count=sum(len(item.records) for item in data),
        data=data,
    )
