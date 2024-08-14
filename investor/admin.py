from django.contrib import admin
from .models import UserProfile, UserAccount, Transaction_ids, Deposit, Withdrawal, WithdrawalRequest, Item, Purchase, MpesaPayment, MpesaRequest
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(UserAccount)
admin.site.register(Transaction_ids)
admin.site.register(Deposit)
admin.site.register(Withdrawal)
admin.site.register(WithdrawalRequest)
admin.site.register(Item)
admin.site.register(Purchase)
# admin.site.register(Callback)
admin.site.register(MpesaPayment)
admin.site.register(MpesaRequest)

