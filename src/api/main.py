import base64
import secrets
import pandas as pd
from typing import Union
from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO
from src.utils.read_excel import read_upload_excel
from src.monthly_return_distribution import monthly_return_distribution
from src.quarterly_return_distribution import quarterly_return_distribution
from src.market_crisis_return_distribution import market_crisis_return_distribution
from src.cash_management import cash_management_table
from src.portfolio_value import portfolio_value_table_from_equity
from src.utils.redis_cache import set_anytype_cache, get_anytype_cache
import pickle
router = APIRouter()


@router.get("/result/{id}/trades")
async def get_trades_result(id: str):
    try:
        cached_bytes = await get_anytype_cache(f"{id}:trades",)
        if cached_bytes:
            retrieved = base64.b64decode(cached_bytes)
            cached_response = pickle.loads(retrieved)
            return cached_response
        else:
            print("Cache miss")
            raise HTTPException(
                status_code=500, detail='No Data for this session')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{id}/stock_returns")
async def get_stock_returns(id: str):
    try:
        cached_bytes = await get_anytype_cache(f"{id}:trades",)
        if cached_bytes:
            retrieved = base64.b64decode(cached_bytes)
            cached_response = pickle.loads(retrieved)

            trades = cached_response['data']['trades']
            df = pd.DataFrame(trades)

            summary = (
                df.groupby('Ticker', as_index=False)
                .agg(
                    no_of_trades=('Ticker', 'count'),
                    overall_pnl_percent=('P&L %', 'sum'),
                    overall_pnl_amount=('P&L Amount', 'sum')
                )
            )

            return {
                "session_key": cached_response['session_key'],
                "filename": cached_response['filename'],
                "data": summary.to_dict(orient="records")
            }
        else:
            print("Cache miss")
            raise HTTPException(
                status_code=500, detail='No Data for this session')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{id}/trades/{ticker}")
async def get_ticker_trades(id: str, ticker: str):
    try:
        cached_bytes = await get_anytype_cache(f"{id}:trades",)
        if cached_bytes:
            retrieved = base64.b64decode(cached_bytes)
            cached_response = pickle.loads(retrieved)

            trades = cached_response['data']['trades']
            df = pd.DataFrame(trades)

            filtered_df = df.loc[df['Ticker'] == ticker]
            data = filtered_df.to_dict(orient="records")
            return {
                "session_key": cached_response['session_key'],
                "filename": cached_response['filename'],
                "ticker": ticker,
                "count": len(data),
                "data": data
            }
        else:
            print("Cache miss")
            raise HTTPException(
                status_code=500, detail='No Data for this session')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{id}")
async def get_result(id: str):
    try:
        cached_bytes = await get_anytype_cache(id)
        if cached_bytes:
            retrieved = base64.b64decode(cached_bytes)
            cached_response = pickle.loads(retrieved)
            return cached_response
        else:
            print("Cache miss")
            raise HTTPException(
                status_code=500, detail='No Data for this session')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_xlsx(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=400, detail="Only .xlsx files are allowed")

    try:
        # Read file into memory
        session_key = secrets.token_hex(16)
        contents = await file.read()
        all_trades, _, equity_curve = read_upload_excel(
            BytesIO(contents))
        original_equity_curve = equity_curve.copy()

        _, monthly_return_bucket_summary, monthly_return = monthly_return_distribution(
            df=original_equity_curve)

        _, quarterly_return_bucket_summary, quarterly_return = quarterly_return_distribution(
            df=original_equity_curve)

        _, market_crisis_return = market_crisis_return_distribution(
            df=original_equity_curve)

        portfolio_value = portfolio_value_table_from_equity(
            df=original_equity_curve)

        cash_management = cash_management_table(df=original_equity_curve)

        response = {
            "session_key": session_key,
            "filename": file.filename,
            "data": {
                "equity_curve": equity_curve.to_dict(orient="records"),
                "portfolio_value": portfolio_value.to_dict(orient="records"),
                "cash_management": cash_management.to_dict(orient="records"),
                "market_crisis_return": market_crisis_return,
                "quarterly_return": quarterly_return,
                "monthly_return": monthly_return,
            }
        }

        encoded = base64.b64encode(pickle.dumps(response)).decode('utf-8')
        await set_anytype_cache(session_key, encoded, expire_seconds=7200)

        trades_response = {
            "session_key": session_key,
            "filename": file.filename,
            "data": {
                "trades": all_trades.fillna(0).to_dict(orient="records")
            }
        }

        trades_encoded = base64.b64encode(
            pickle.dumps(trades_response)).decode('utf-8')

        await set_anytype_cache(f"{session_key}:trades", trades_encoded, expire_seconds=7200)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
