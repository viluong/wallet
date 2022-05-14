from django.urls import path, include

from wallet.views import InitAccountView, WalletView, WalletDepositView, WalletWithdrawalView

urlpatterns = [
    path('init', InitAccountView.as_view(), name="init_account"),
    path('wallet', WalletView.as_view(), name="enable_wallet"),
    path('wallet/deposits', WalletDepositView.as_view(), name="deposit_wallet"),
    path('wallet/withdrawals', WalletWithdrawalView.as_view(), name="deposit_wallet")
]
