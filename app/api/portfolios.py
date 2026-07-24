from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, SessionDep
from app.models import Portfolio, Transaction
from app.schemas import PortfolioAnalytics, PortfolioCreate, PortfolioOut, TransactionCreate
from app.services.portfolio import portfolio_analytics

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


async def user_portfolio(portfolio_id: UUID, user_id: UUID, session: SessionDep) -> Portfolio:
    portfolio = await session.scalar(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
    )
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.post("", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate, user: CurrentUser, session: SessionDep
) -> Portfolio:
    portfolio = Portfolio(
        user_id=user.id, name=payload.name, base_currency=payload.base_currency.lower()
    )
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    return portfolio


@router.get("", response_model=list[PortfolioOut])
async def list_portfolios(user: CurrentUser, session: SessionDep) -> list[Portfolio]:
    return list(
        (await session.scalars(select(Portfolio).where(Portfolio.user_id == user.id))).all()
    )


@router.post("/{portfolio_id}/transactions", status_code=status.HTTP_201_CREATED)
async def add_transaction(
    portfolio_id: UUID, payload: TransactionCreate, user: CurrentUser, session: SessionDep
) -> dict[str, str]:
    portfolio = await user_portfolio(portfolio_id, user.id, session)
    transaction = Transaction(portfolio_id=portfolio.id, **payload.model_dump())
    session.add(transaction)
    await session.commit()
    return {"id": str(transaction.id)}


@router.get("/{portfolio_id}/analytics", response_model=PortfolioAnalytics)
async def analytics(
    portfolio_id: UUID, request: Request, user: CurrentUser, session: SessionDep
) -> PortfolioAnalytics:
    portfolio = await user_portfolio(portfolio_id, user.id, session)
    return await portfolio_analytics(session, portfolio, request.app.state.market_client)
