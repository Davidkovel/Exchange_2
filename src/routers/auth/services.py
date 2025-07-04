from eth_account import Account


class WalletAddressService:
    @staticmethod
    async def generate_wallet_address():
        acct = Account.create()
        return {
            "address": acct.address,
            "private_key": acct.key.hex(),
        }
