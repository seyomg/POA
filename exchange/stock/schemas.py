from enum import Enum
from typing import Literal
from pydantic import BaseModel

korea_stocks = ("KRX")
us_stocks = ("NASDAQ", "NYSE", "AMEX")


class BaseUrls(str, Enum):
    base_url = "https://openapi.koreainvestment.com:9443"
    paper_base_url = "https://openapivts.koreainvestment.com:29443"


class BaseHeaders(BaseModel):
    authorization: str
    appkey: str
    appsecret: str
    custtype: str = "P"
    # tr_id: str = Literal[TransactionId.korea_buy, TransactionId.korea_sell, TransactionId.korea_paper_buy, TransactionId.korea_paper_sell,
    #  TransactionId.korea_paper_cancel, TransactionId.usa_buy, TransactionId.usa_sell, TransactionId.usa_paper_buy, TransactionId.usa_paper_sell]

#Edited: 국선 endpoint 추가
class Endpoints(str, Enum):
    korea_order_base = "/uapi/domestic-stock/v1"
    korea_order = f"{korea_order_base}/trading/order-cash"
    korea_order_buyable = f"{korea_order_base}/trading/inquire-psbl-order"

    #추가
    korea_futures_order_base = "/uapi/domestic-futureoption/v1"
    korea_futures_order = f"{korea_futures_order_base}/trading/order"
    korea_futures_order_buyable = f"{korea_futures_order_base}trading/inquire-psbl-order"

    usa_order_base = "/uapi/overseas-stock/v1"
    usa_order = f"{usa_order_base}/trading/order"
    usa_order_buyable = f"{usa_order_base}/trading/inquire-psamount"
    usa_current_price = f"/uapi/overseas-price/v1/quotations/price"

    korea_ticker = "/uapi/domestic-stock/v1/quotations/inquire-price"
    usa_ticker = "/uapi/overseas-price/v1/quotations/price"

#Edited: 국선 TrId추가
class TransactionId(str, Enum):

    korea_buy = "TTTC0802U"
    korea_sell = "TTTC0801U"

    korea_paper_buy = "VTTC0802U"
    korea_paper_sell = "VTTC0801U"
    korea_paper_cancel = "VTTC0803U"

    #주간
    korea_futures_buy_and_sell = "TTTO1101U"

    usa_buy = "JTTT1002U"
    usa_sell = "JTTT1006U"

    usa_paper_buy = "VTTT1002U"
    usa_paper_sell = "VTTT1001U"

    korea_ticker = "FHKST01010100"
    #Edited: 국선시세조회 tr_id
    korea_futures_ticker = "FHMIF10000000"
    usa_ticker = "HHDFS00000300"

#Edited: 시세조회 인자는 주식, 국선 동일 but 국선 Description 추가
class KoreaTickerQuery(BaseModel):
    FID_COND_MRKT_DIV_CODE: Literal["J", "F"]
    FID_INPUT_ISCD: str


class UsaTickerQuery(BaseModel):
    AUTH: str = ""
    EXCD: Literal["NYS", "NAS", "AMS"]
    SYMB: str                           # 종목코드


class ExchangeCode(str, Enum):
    NYSE = "NYSE"
    NASDAQ = "NASD"
    AMEX = "AMEX"


class QueryExchangeCode(str, Enum):
    NYSE = "NYS"
    NASDAQ = "NAS"
    AMEX = "AMS"


class KoreaOrderType(str, Enum):
    market = "01"   # 시장가
    limit = "00"    # 지정가

#Edited: 국선 주문유형 추가
class KoreaFuturesOrderType(str, Enum):
    market = "02"   # 시장가
    limit = "01"    # 지정가


class UsaOrderType(str, Enum):
    limit = "00"    # 지정가


class OrderSide(str, Enum):
    buy = "buy"
    sell = "sell"


class TokenInfo(BaseModel):
    access_token: str
    access_token_token_expired: str


class KoreaTickerHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_ticker.value

#Edited: 추가됨
class KoreaFuturesTickerHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_futures_ticker.value


class UsaTickerHeaders(BaseHeaders):
    tr_id: str = TransactionId.usa_ticker.value


class KoreaBuyOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_buy.value


class KoreaSellOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_sell.value


class KoreaPaperBuyOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_paper_buy.value


class KoreaPaperSellOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_paper_sell.value

#Edited: 추가됨
class KoreaFuturesBuySellOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.korea_futures_buy_and_sell.value


class UsaBuyOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.usa_buy.value


class UsaSellOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.usa_sell.value


class UsaPaperBuyOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.usa_paper_buy.value


class UsaPaperSellOrderHeaders(BaseHeaders):
    tr_id: str = TransactionId.usa_paper_sell.value


class AccountInfo(BaseModel):
    CANO: str           # 계좌번호 앞 8자리
    ACNT_PRDT_CD: str   # 계좌번호 뒤 2자리


# class BaseBody(BaseModel):


class OrderBody(AccountInfo):
    PDNO: str           # 종목코드 6자리
    ORD_QTY: str        # 주문수량


class KoreaOrderBody(OrderBody):
    ORD_DVSN: Literal[f"{KoreaOrderType.market}", f"{KoreaOrderType.limit}"]
    ORD_UNPR: str       # 주문가격


class KoreaMarketOrderBody(KoreaOrderBody):
    ORD_DVSN: str = KoreaOrderType.market.value
    ORD_UNPR: str = "0"

#Edited: 국선 추가
class KoreaFuturesOrderBody(AccountInfo):
    ORD_PRCS_DVSN_CD: "02"
    SLL_BUY_DVSN_CD: Literal["01", "02"]     # 01: 매도, 02매수
    SHTN_PDNO: str
    ORD_QTY: str
    UNIT_PRICE: str = "0"
    NMPR_TYPE_CD: Literal[f"{KoreaFuturesOrderType.market}", f"{KoreaFuturesOrderType.limit}"]
    KRX_NMPR_CNDT_CD: Literal["0", "3", "4"]    # 0: 없음, 3:IOC, 4:FOK
    CTAC_TLNO: str
    FUOP_ITEM_DVSN_CD: str
    ORD_DVSN_CD: Literal[f"{KoreaFuturesOrderType.market}", f"{KoreaFuturesOrderType.limit}"]


class UsaOrderBody(OrderBody):
    ORD_DVSN: str = UsaOrderType.limit.value  # 주문구분
    OVRS_ORD_UNPR: str  # 주문가격
    OVRS_EXCG_CD: Literal[ExchangeCode.NYSE, ExchangeCode.NASDAQ, ExchangeCode.AMEX]   # 거래소코드  NASD : 나스닥, NYSE: 뉴욕, AMEX: 아멕스
    ORD_SVR_DVSN_CD: str = "0"


# class OrderType(str, Enum):
#     limit = "limit"
#     market = "market"


# class OrderBase(BaseModel):
#     ticker: str
#     type: Literal[OrderType.limit, OrderType.market]
#     side: Literal[OrderSide.buy, OrderSide.sell]
#     amount: int
#     price: float
#     exchange_code: Literal[ExchangeCode.NYSE, ExchangeCode.NASDAQ, ExchangeCode.AMEX]
#     mintick: float
