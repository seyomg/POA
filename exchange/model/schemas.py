from pydantic import BaseModel, BaseSettings, validator, root_validator
from typing import Literal
import os
from pathlib import Path
from enum import Enum
from devtools import debug
#Edited: 국선티커 월물변경
from datetime import datetime
import calendar
import pytz

CRYPTO_LITERAL = Literal["BINANCE", "UPBIT", "BYBIT", "BITGET", "OKX"]


STOCK_LITERAL = Literal[
    "KRX",
    "NASDAQ",
    "NYSE",
    "AMEX",
]


EXCHANGE_LITERAL = Literal[
    "BINANCE",
    "UPBIT",
    "BYBIT",
    "BITGET",
    "OKX",
    "KRX",
    "NASDAQ",
    "NYSE",
    "AMEX",
]

QUOTE_LITERAL = Literal["USDT", "USDT.P", "USDTPERP", "BUSD", "BUSD.P", "BUSDPERP", "KRW", "USD", "USD.P"]

SIDE_LITERAL = Literal["buy", "sell", "entry/buy", "entry/sell", "close/buy", "close/sell"]


def find_env_file():
    current_path = os.path.abspath(__file__)
    while True:
        parent_path = os.path.dirname(current_path)
        env_path = os.path.join(parent_path, ".env")
        dev_env_path = os.path.join(parent_path, ".env.dev")
        if os.path.isfile(dev_env_path):
            return dev_env_path
        elif os.path.isfile(env_path):
            return env_path
        if parent_path == current_path:
            break
        current_path = parent_path
    return None


env_path = find_env_file()


CRYPTO_EXCHANGES = ("BINANCE", "UPBIT", "BYBIT", "BITGET", "OKX")

STOCK_EXCHANGES = (
    "KRX",
    "NASDAQ",
    "NYSE",
    "AMEX",
)

COST_BASED_ORDER_EXCHANGES = ("UPBIT", "BYBIT", "BITGET")

NO_ORDER_AMOUNT_OUTPUT_EXCHANGES = (
    "BITGET",
    "KRX",
    "NASDAQ",
    "NYSE",
    "AMEX",
)

# "BITGET", "KRX", "NASDAQ", "AMEX", "NYSE")
#Edited: 국선 티커 추가(트뷰티커)
korea_futures_ticker = ("MINIFKOSPI200", "KOSPI200FUT", "F_KOSDAQ150")

crypto_futures_code = ("PERP", ".P")

# Literal[
#     "KRW", "USDT", "USDTPERP", "BUSD", "BUSDPERP", "USDT.P", "USD", "BUSD.P"
# ]


class Settings(BaseSettings):
    PASSWORD: str
    WHITELIST: list[str] | None = None
    PORT: int | None = None
    DISCORD_WEBHOOK_URL: str | None = None
    UPBIT_KEY: str | None = None
    UPBIT_SECRET: str | None = None
    BINANCE_KEY: str | None = None
    BINANCE_SECRET: str | None = None
    BYBIT_KEY: str | None = None
    BYBIT_SECRET: str | None = None
    BITGET_KEY: str | None = None
    BITGET_SECRET: str | None = None
    BITGET_PASSPHRASE: str | None = None
    OKX_KEY: str | None = None
    OKX_SECRET: str | None = None
    OKX_PASSPHRASE: str | None = None
    KIS1_ACCOUNT_NUMBER: str | None = None
    KIS1_ACCOUNT_CODE: str | None = None
    KIS1_KEY: str | None = None
    KIS1_SECRET: str | None = None
    KIS2_ACCOUNT_NUMBER: str | None = None
    KIS2_ACCOUNT_CODE: str | None = None
    KIS2_KEY: str | None = None
    KIS2_SECRET: str | None = None
    KIS3_ACCOUNT_NUMBER: str | None = None
    KIS3_ACCOUNT_CODE: str | None = None
    KIS3_KEY: str | None = None
    KIS3_SECRET: str | None = None
    KIS4_ACCOUNT_NUMBER: str | None = None
    KIS4_ACCOUNT_CODE: str | None = None
    KIS4_KEY: str | None = None
    KIS4_SECRET: str | None = None
    DB_ID: str = "poa@admin.com"
    DB_PASSWORD: str = "poabot!@#$"

    class Config:
        env_file = env_path  # ".env"
        env_file_encoding = "utf-8"

#Edited: is_korea_futures 조건 추가
def get_extra_order_info(order_info):
    extra_order_info = {
        "is_futures": None,
        "is_crypto": None,
        "is_stock": None,
        "is_korea_futures": None,
        "is_spot": None,
        "is_entry": None,
        "is_close": None,
        "is_buy": None,
        "is_sell": None,
    }
    if order_info["exchange"] in CRYPTO_EXCHANGES:
        extra_order_info["is_crypto"] = True
        if any([order_info["quote"].endswith(code) for code in crypto_futures_code]):
            extra_order_info["is_futures"] = True
        else:
            extra_order_info["is_spot"] = True

    #Edited: 국선 조건 추가
    elif order_info["exchange"] in STOCK_EXCHANGES:
        extra_order_info["is_stock"] = True
        if order_info["base"] in korea_futures_ticker:
            extra_order_info["is_korea_futures"] = True

    if order_info["side"] in ("entry/buy", "entry/sell"):
        extra_order_info["is_entry"] = True
        _side = order_info["side"].split("/")[-1]
        if _side == "buy":
            extra_order_info["is_buy"] = True
        elif _side == "sell":
            extra_order_info["is_sell"] = True
    elif order_info["side"] in ("close/buy", "close/sell"):
        extra_order_info["is_close"] = True
        _side = order_info["side"].split("/")[-1]
        if _side == "buy":
            extra_order_info["is_buy"] = True
        elif _side == "sell":
            extra_order_info["is_sell"] = True
    elif order_info["side"] == "buy":
        extra_order_info["is_buy"] = True
    elif order_info["side"] == "sell":
        extra_order_info["is_sell"] = True

    return extra_order_info


def parse_side(side: str):
    if side.startswith("entry/") or side.startswith("close/"):
        return side.split("/")[-1]
    else:
        return side


def parse_quote(quote: str):
    if quote.endswith(".P"):
        return quote.replace(".P", "")
    else:
        return quote
    
#Edited: 3.12 두번째목요일 수정중
def find_second_thursday(year, month):                                                      
    month_calendar = calendar.monthcalendar(year, month)
    thursdays = [week[calendar.THURSDAY] for week in month_calendar if week[calendar.THURSDAY] != 0]
    return thursdays[1]  # 두 번째 목요일


#Edited: 국선 조건 추가
class OrderRequest(BaseModel):
    exchange: EXCHANGE_LITERAL
    base: str
    quote: QUOTE_LITERAL
    # QUOTE
    type: Literal["market", "limit"] = "market"
    side: SIDE_LITERAL
    amount: float | None = None
    price: float | None = None
    cost: float | None = None
    percent: float | None = None
    amount_by_percent: float | None = None
    leverage: int | None = None
    stop_price: float | None = None
    profit_price: float | None = None
    order_name: str = "주문"
    kis_number: int | None = 1
    hedge: str | None = None
    unified_symbol: str | None = None
    is_crypto: bool | None = None
    is_stock: bool | None = None
    is_korea_futures: bool | None = None
    is_spot: bool | None = None
    is_futures: bool | None = None
    is_coinm: bool | None = None
    is_entry: bool | None = None
    is_close: bool | None = None
    is_buy: bool | None = None
    is_sell: bool | None = None
    is_contract: bool | None = None
    contract_size: float | None = None
    margin_mode: str | None = None

    class Config:
        use_enum_values = True

    @root_validator(pre=True)
    def root_validate(cls, values):
        # "NaN" to None
        for key, value in values.items():
            if value in ("NaN", ""):
                values[key] = None

        values |= get_extra_order_info(values)

        values["side"] = parse_side(values["side"])
        values["quote"] = parse_quote(values["quote"])
        base = values["base"]
        quote = values["quote"]
        unified_symbol = f"{base}/{quote}"
        exchange = values["exchange"]
        if values["is_futures"]:
            if quote == "USD":
                unified_symbol = f"{base}/{quote}:{base}"
                values["is_coinm"] = True
            else:
                unified_symbol = f"{base}/{quote}:{quote}"

        if not values["is_stock"]:
            values["unified_symbol"] = unified_symbol

        #Edited:국선조건 추가, 국선일 경우 base에 KRX거래소 티커 부여
        if values["exchange"] in STOCK_EXCHANGES:
            values["is_stock"] = True
            if values["base"] in korea_futures_ticker:
                values["is_korea_futures"] = True
                korea_timezone = pytz.timezone('Asia/Seoul')
                now = datetime.now(korea_timezone)                    #Edited: 3.12 두번째목요일 수정중
                # 분기월 계산 (3, 6, 9, 12월)
                quarters = [3, 6, 9, 12]
                current_quarter_last_month = next(q for q in quarters if q >= now.month)
                second_thursday_current_qlm = find_second_thursday(now.year, current_quarter_last_month)
                second_thursday_this_month = find_second_thursday(now.year, now.month)
                next_quarter_last_month = next((q for q in quarters if q > now.month), quarters[0])
                # 월 형식 맞추기
                if now.month == current_quarter_last_month and now.day >= second_thursday_current_qlm-1:      #Edited: 3.15. 두번째 목요일(2차수정)
                    month_code = f"{next_quarter_last_month:02d}"
                else:
                    month_code = f"{current_quarter_last_month:02d}"    #Edited: 3.14 두번째목요일(1차수정)
                if values["base"] == "KOSPI200FUT":                    
                    values["base"] = f"101V{month_code}"
                elif values["base"] == "F_KOSDAQ150":
                    values["base"] = f"106V{month_code}"
                elif values["base"] == "MINIFKOSPI200":
                    #Edited: 두번째 목요일 조건 추가
                    if now.day >= second_thursday_this_month-1:
                        month_code = now.month + 1 if now.month < 12 else 1
                    else:
                        month_code = now.month
                    # 월 형식 맞추기
                    month_code = f"{month_code:02d}"
                    values["base"] = f"105V{month_code}"
        # debug("after", values)
        return values


class OrderBase(OrderRequest):
    password: str

    @validator("password")
    def password_validate(cls, v):
        setting = Settings()
        if v != setting.PASSWORD:
            raise ValueError("비밀번호가 틀렸습니다")
        return v


class MarketOrder(OrderBase):
    price: float | None = None
    type: Literal["market"] = "market"

#Edited: 국선조건 추가
class PriceRequest(BaseModel):
    exchange: EXCHANGE_LITERAL
    base: str
    quote: QUOTE_LITERAL
    is_crypto: bool | None = None
    is_stock: bool | None = None
    is_futures: bool | None = None
    is_korea_futures: bool | None = None

    @root_validator(pre=True)
    def root_validate(cls, values):
        # "NaN" to None
        for key, value in values.items():
            if value in ("NaN", ""):
                values[key] = None

        values |= get_extra_order_info(values)

        return values


# class PositionRequest(BaseModel):
#     exchange: EXCHANGE_LITERAL
#     base: str
#     quote: QUOTE_LITERAL


class Position(BaseModel):
    exchange: EXCHANGE_LITERAL
    base: str
    quote: QUOTE_LITERAL
    side: Literal["long", "short"]
    amount: float
    entry_price: float
    roe: float


class HedgeData(BaseModel):
    password: str
    exchange: Literal["BINANCE"]
    base: str
    quote: QUOTE_LITERAL = "USDT.P"
    amount: float | None = None
    leverage: int | None = None
    hedge: str

    @validator("password")
    def password_validate(cls, v):
        setting = Settings()
        if v != setting.PASSWORD:
            raise ValueError("비밀번호가 틀렸습니다")
        return v

    @root_validator(pre=True)
    def root_validate(cls, values):
        for key, value in values.items():
            if key in ("exchange", "base", "quote", "hedge"):
                values[key] = value.upper()
        return values
