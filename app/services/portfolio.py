from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Portfolio, Transaction
from app.schemas import Holding, PortfolioAnalytics
from app.services.coingecko import CoinGeckoClient


async def portfolio_analytics(
    session: AsyncSession, portfolio: Portfolio, market_client: CoinGeckoClient
) -> PortfolioAnalytics:
    transactions = list(
        (
            await session.scalars(
                select(Transaction).where(Transaction.portfolio_id == portfolio.id)
            )
        ).all()
    )
    positions: dict[str, dict[str, Decimal | str]] = defaultdict(
        lambda: {"quantity": Decimal("0"), "cost": Decimal("0"), "symbol": ""}
    )
    for transaction in transactions:
        position = positions[transaction.coin_id]
        direction = Decimal("1") if transaction.transaction_type == "buy" else Decimal("-1")
        position["quantity"] += direction * transaction.quantity  # type: ignore[operator]
        position["cost"] += direction * (
            transaction.quantity * transaction.price + transaction.fees
        )  # type: ignore[operator]
        position["symbol"] = transaction.symbol.upper()

    prices: dict[str, Decimal] = {}
    if positions:
        markets = await market_client.markets(portfolio.base_currency, per_page=250)
        prices = {
            item["id"]: Decimal(str(item["current_price"]))
            for item in markets
            if item.get("current_price")
        }

    holdings: list[Holding] = []
    total_cost = Decimal("0")
    total_value = Decimal("0")
    has_all_prices = True
    for coin_id, position in positions.items():
        quantity = position["quantity"]  # type: ignore[assignment]
        if quantity <= 0:  # type: ignore[operator]
            continue
        cost = position["cost"]  # type: ignore[assignment]
        total_cost += cost  # type: ignore[operator]
        price = prices.get(coin_id)
        value = quantity * price if price is not None else None  # type: ignore[operator]
        if value is None:
            has_all_prices = False
        else:
            total_value += value
        holdings.append(
            Holding(
                coin_id=coin_id,
                symbol=str(position["symbol"]),
                quantity=quantity,
                cost_basis=cost,
                market_price=price,
                market_value=value,
                unrealized_pnl=value - cost if value is not None else None,
            )
        )
    return PortfolioAnalytics(
        portfolio_id=UUID(str(portfolio.id)),
        total_cost_basis=total_cost,
        total_market_value=total_value if has_all_prices else None,
        unrealized_pnl=total_value - total_cost if has_all_prices else None,
        holdings=holdings,
    )
