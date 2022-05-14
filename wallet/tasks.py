
from wallet.models import Wallet


def update_balance_after_deposit(wallet_id=None, amount=None):
    wallet = Wallet.objects.get(id=wallet_id)
    if wallet and amount:
        wallet.balance = wallet.balance + amount
        wallet.save()

    return True


def update_balance_after_withdrawal(wallet=None, transaction=None):
    if wallet and transaction:
        wallet.balance = wallet.balance - transaction.amount
        wallet.save()

    return True
