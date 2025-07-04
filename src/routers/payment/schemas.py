from pydantic import BaseModel


class WithdrawRequestModel(BaseModel):
    trx_wallet: str
    usdt_amount: float
