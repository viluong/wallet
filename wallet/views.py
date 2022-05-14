from django.http import Http404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from wallet.models import Wallet
from wallet.serializers import CustomerSerializer, EnableWalletSerializer, DisableWalletSerializer, DepositSerializer, \
    WithdrawalSerializer, enabled_validator
from wallet.utils import response_success, response_fail


class InitAccountView(APIView):

    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return response_success(serializer.data, status=status.HTTP_201_CREATED)
        return response_fail(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletView(APIView):

    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def get_object(self, customer_xid):
        try:
            return Wallet.objects.get(customer_id=customer_xid)
        except Wallet.DoesNotExist:
            raise Http404

    def post(self, request):
        wallet = self.get_object(request.user.customer_xid)
        serializer = EnableWalletSerializer(wallet, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return response_success(serializer.data, status=status.HTTP_200_OK)
        return response_fail(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        wallet = self.get_object(request.user.customer_xid)
        serializer = EnableWalletSerializer(wallet)
        enabled_validator(wallet)
        return response_success(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        wallet = self.get_object(request.user.customer_xid)
        enabled_validator(wallet)
        serializer = DisableWalletSerializer(wallet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response_success(serializer.data, status=status.HTTP_200_OK)

        return response_fail(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletDepositView(APIView):
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer_xid=request.user.customer_xid)

            return response_success(serializer.data, status=status.HTTP_200_OK)
        return response_fail(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletWithdrawalView(APIView):
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer_xid=request.user.customer_xid)

            return response_success(serializer.data, status=status.HTTP_200_OK)
        return response_fail(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
