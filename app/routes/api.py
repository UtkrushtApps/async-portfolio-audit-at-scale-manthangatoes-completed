from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import Portfolio, Trade, MarketData, AuditLog
from app.schemas.schemas import TradeSummary, TradeOut, AuditLogOut, PortfolioSummary
from sqlalchemy import func, distinct
import datetime
router = APIRouter()

from sqlalchemy import func, distinct

@router.get("/portfolio/{portfolio_id}/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(portfolio_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.coalesce(func.sum(Trade.amount), 0).label("total_amount"),
            func.array_agg(distinct(Trade.ticker)).label("tickers")
        ).where(Trade.portfolio_id == portfolio_id)
    )
    row = result.one()
    return PortfolioSummary(
        portfolio_id=portfolio_id,
        total_trades=row.total_trades,
        total_amount=row.total_amount,
        tickers=row.tickers or []
    )


@router.post("/portfolio/{portfolio_id}/trade", response_model=TradeOut)
async def make_trade(portfolio_id: int, trade: TradeSummary, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    t = Trade(
        portfolio_id=portfolio_id,
        ticker=trade.ticker,
        side=trade.side,
        amount=trade.amount,
        price=trade.price,
        trade_time=datetime.datetime.utcnow(),
        status="executed"
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    background_tasks.add_task(audit_trade_event, t.id, 'TRADE_EXECUTED', db)
    return TradeOut(id=t.id, ticker=t.ticker, portfolio_id=t.portfolio_id, side=t.side, amount=t.amount, price=t.price, trade_time=str(t.trade_time), status=t.status)

@router.get("/audit/{trade_id}", response_model=list[AuditLogOut])
async def get_audit_logs(trade_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(AuditLog).where(AuditLog.trade_id == trade_id).order_by(AuditLog.log_timestamp.desc()))
    logs = q.scalars().all()
    return [AuditLogOut(id=l.id, event_type=l.event_type, log_timestamp=str(l.log_timestamp), event_data=l.event_data) for l in logs]

async def audit_trade_event(trade_id: int, event_type: str, db: AsyncSession):
    a = AuditLog(trade_id=trade_id, event_type=event_type, event_data={"msg": "Executed trade"}, log_timestamp=datetime.datetime.utcnow())
    db.add(a)
    await db.commit()