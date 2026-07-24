from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    is_active: bool


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    base_currency: str = Field(default="usd", min_length=3, max_length=3)


class PortfolioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    base_currency: str


class TransactionCreate(BaseModel):
    coin_id: str = Field(pattern=r"^[a-z0-9-]{1,100}$")
    symbol: str = Field(min_length=1, max_length=20)
    transaction_type: str = Field(pattern=r"^(buy|sell)$")
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    occurred_at: datetime


class Holding(BaseModel):
    coin_id: str
    symbol: str
    quantity: Decimal
    cost_basis: Decimal
    market_price: Decimal | None
    market_value: Decimal | None
    unrealized_pnl: Decimal | None


class PortfolioAnalytics(BaseModel):
    portfolio_id: UUID
    total_cost_basis: Decimal
    total_market_value: Decimal | None
    unrealized_pnl: Decimal | None
    holdings: list[Holding]
