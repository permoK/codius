from django.db import models
import uuid
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .utils import generate_uuid

# Create your models here.
class UserProfile(AbstractUser):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=12, unique=True, null=False, blank=False, default=True)
    registration_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.BigIntegerField()
    date_joined = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=50, blank=True)
    recommended_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommended",
        verbose_name="recommended by",
        help_text="The user who recommended this user.",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="user_profiles",
        verbose_name="groups",
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="user_profiles",
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )

    def __str__(self):
        return f"{self.username} - {self.code}"

    def save(self, *args, **kwargs):
        # Check if the user already has a code
        if self.code == "" or self.registration_number == "":
            # Generate a new code for the user
            code = generate_uuid()
            registration_number = generate_uuid()
            self.code = code
            self.registration_number = registration_number
        super().save(*args, **kwargs)

        # Check if the user already has a UserAccount instance
        if not hasattr(self, 'UserAccount'):
            # Create a new Wallet instance for the user
            UserAccount.objects.create(user=self, username=self.username, amount_paid=0, balance=0)
        
        # list of recommended profiles
        def get_recommended_profiles(self):
            qs = UserProfile.objects.all()
            my_recommended_profiles = []
            for profile in qs:
                if profile.recommended_by == self.user:
                    my_recommended_profiles.append(profile)
            return my_recommended_profiles


class UserAccount(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='UserAccount') 
    username = models.CharField(max_length=12, unique=True, null=False, blank=False, default=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transactions_id = models.CharField(max_length=12)
    date = models.DateTimeField(auto_now_add=True)
    bonus_given = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} - Amount Paid: {self.amount_paid}, Balance: {self.balance}"

# # transactions
class Transaction_ids(models.Model):
    user = models.CharField(max_length=50)
    transactions_id = models.CharField(max_length=12)
    name = models.CharField(max_length=12, null=False, blank=False)
    amount_deposited = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f" {self.user}, Transactions ID: {self.transactions_id}, Date: {self.date}"

# # deposits
class Deposit(models.Model):
    username = models.CharField(max_length=12, null=False, blank=False)
    name = models.CharField(max_length=12, null=False, blank=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.IntegerField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    transactions_id = models.CharField(max_length=12, null=False, blank=False)
    def __str__(self):
        return f"{self.username} - Amount: {self.amount_paid}, Date: {self.date}"

#  withdrawals
class Withdrawal(models.Model):
    username = models.CharField(max_length=12, null=False, blank=False)
    phone_number = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=12, null=False, blank=False)
    withdrawn = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.username} - Amount: {self.withdrawn}, Date: {self.date}"

# amount withrawn
class WithdrawalRequest(models.Model):
    username = models.CharField(max_length=12, null=False, blank=False)
    phone_number = models.IntegerField(null=False, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    confirmation_name = models.CharField(max_length=12, null=False, blank=False)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.username} - Amount: {self.amount}, Date: {self.date}"


class Item(models.Model):
    name = models.CharField(max_length=12, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    title = models.CharField(max_length=12, null=False, blank=False)
    description = models.TextField()
    image = models.ImageField(upload_to='assets/', null=True, blank=True)
    release_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    release_date = models.DateTimeField(auto_now_add=True)

    def update_user_balance(self):
        from datetime import timedelta
        users = UserAccount.objects.filter(transactions_id=self.id)
        for user in users:
            # Check if the last balance update was more than 1 day ago
            last_update = user.date
            if not last_update or timezone.now() - last_update >= timedelta(minutes=1):
                user.balance += self.release_amount
                user.date = timezone.now()
                user.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Call the update_user_balance method when the item is saved
        self.update_user_balance()

    @property
    def is_released(self):
        return timezone.now() >= self.release_date

    def __str__(self):
        return f"Asset Name: {self.name}, Asset Value: {self.price}, Release Amount: {self.release_amount}, Release Date: {self.release_date}"

class Purchase(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    release_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    title = models.CharField(max_length=12, null=False, blank=False, default=True)
    description = models.TextField()
    image = models.FileField(upload_to='assets/', null=True, blank=True)
    purchase_date = models.DateTimeField(default=timezone.now)
    released = models.BooleanField(default=False)
    profit_released_date = models.DateTimeField(null=True, blank=True)

    def release_profit(self):
        if not self.released:
            user_account = UserAccount.objects.get(user=self.user)
            user_account.balance += self.profit
            user_account.save()

            self.released = True
            self.profit_released_date = timezone.now()
            self.save()
    def __str__(self):
        return f"{self.user.username} purchased {self.item.name} on {self.purchase_date}"


class Callback(models.Model):
    result = models.CharField()
    date = models.DateTimeField(default=timezone.now)


############ Mpesa Request ###############################
class MpesaRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    description = models.TextField()
    merchant = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"


###################### STKpush callback ########################

class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

################### mpesa payments ############################
class MpesaPayment(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_finished = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)
    trans_id = models.CharField(max_length=30, blank=True, null=True)
    order_id = models.CharField(max_length=200, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    merchant = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'
        indexes = [
            models.Index(fields=['created_at']),
        ]

        
    def __str__(self):
        return self.description
####################### End Payment ######################################

############################ End Payments model #####################################
