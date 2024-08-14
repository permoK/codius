# authapp/views.py
from django.shortcuts import render, redirect, reverse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
# from .forms import SignUpForm
from django.http import HttpResponse, request, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse

from django.views import View

import json
import requests
from requests.auth import HTTPBasicAuth
import base64

from decimal import Decimal

import uuid

# import models
from .models import UserProfile, UserAccount, Transaction_ids, Deposit, Withdrawal, WithdrawalRequest, Item, Purchase, Callback, MpesaRequest, MpesaPayment

# import forms
from .forms import CreateUserForm, UserProfileForm, loginForm, reset_passwordForm, deposit_form, withdraw_form, searchForm, StkpushForm, transactions_id_form, letterForm, user_deposit_form

from .utils import get_access_token

from django_daraja.mpesa.core import MpesaClient

########## global variable #######
# base_url = 'https://codius.up.railway.app/'
base_url = 'https://monadoll.tech'
key = 'nAbuuqCD0dMH3uhXSO5A2yY7rd1HACYE'
secret = '3ZnvWnVqFqPgvUXF'
####################################


# Create your views here.

#Admin
# @login_required(login_url='login')
@csrf_exempt
def adminLogin(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # authenticate user
            # user = authenticate(username=username, password=password)
            if username == 'permo' and password == 'permo123':
                # login(request, user)
                messages.success(request, 'You have successfully logged in')
                return redirect('adminDashboard')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('admin_login')
    else:
        form = loginForm()
    return render(request, 'admin/admin_login.html', {'form': form, 'messages': messages.get_messages(request)})

def adminDashboard(request):
    message = messages.get_messages(request)

    #calculate how many users in the database
    users = User.objects.all()
    user_count = len(users)

    #calculate total amount of money in the system
    total_amount = 0
    for user in UserProfile.objects.all():
        total_amount += user.UserAccount.balance
    total_amount = "{:,.2f}".format(total_amount)

    total_bonus = 0
    for user in UserProfile.objects.all():
        total_bonus += user.UserAccount.bonus
    total_bonus = "{:,.2f}".format(total_bonus)

    # calculate the total number deposits
    deposits = Deposit.objects.all().order_by('-date')
    deposits_count = len(deposits)

    # calculate the total number of withdrawals
    withdrawals = WithdrawalRequest.objects.all()
    withdrawals_count = len(withdrawals)

    #get the total number of users in UserProfiles
    user_profiles = UserProfile.objects.all()
    user_profiles_count = len(user_profiles)

    context = {'message':message, 'total_amount':total_amount , "total_bonus":total_bonus, 'customers':user_profiles_count , 'deposited':deposits_count ,'withdrawed':withdrawals_count, 'products': [100, 200, 30, 40, 500]}
    return render(request, 'admin/adminDashboard.html', context)

def admin_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    
    return redirect('admin_login')

def admin_users(request):
    return render(request, 'admin_users.html')

def admin_workplace(request):
    form = transactions_id_form()

    return render(request, 'admin/admin_workplace.html', {'form': form})

#*************users***************
def all_users(request):
    # fetch all users
    users = UserAccount.objects.all()
    profile = User.objects.all()
    return render(request, 'all_users.html', {'users': users, 'profile': profile})


def landing_page(request):
    return render(request,'user/landing_page.html')


@login_required(login_url='login')
def dashboard(request):
    recommended_users = []
    for prof in UserProfile.objects.all():
        if prof.recommended_by == request.user:
            recommended_users.append(prof)
        #count the number of recommended users
    recommended_users = len(recommended_users)
    bonus = "{:,.2f}".format(UserAccount.objects.get(username=request.user).bonus)
    balance = "{:,.2f}".format(UserAccount.objects.get(username=request.user).balance)
    total_balance = "{:,.2f}".format(UserAccount.objects.get(username=request.user).balance + UserAccount.objects.get(username=request.user).bonus)

    if UserProfile.objects.get(username=request.user.username):
        user_profile = UserProfile.objects.get(username=request.user.username)
    else:
        user_profile = None
    
    assets = Item.objects.all()

    # get number of purchased items
    purchased_items = Purchase.objects.filter(user=user_profile)
    purchased_items_count = len(purchased_items)
    # get total profit earned
    total_profit = 0
    for item in purchased_items:
        total_profit += item.profit
    total_profit = "{:,.2f}".format(total_profit)

    # get total withdraws money
    withdraws = Withdrawal.objects.filter(username=request.user.username)
    # add total money withdrawn
    withdraws_count = 0
    for withdraw in withdraws:
        withdraws_count += withdraw.withdrawn
    withdraws_count = "{:,.2f}".format(withdraws_count)

    context = {'recommended_users': recommended_users, 'referral_bonus': bonus, 'user': request.user, 'user_profile': user_profile, 'balance':total_balance, 'purchased_items': purchased_items_count  ,'withdraws': withdraws_count ,'total_profit':total_profit,'products': [100, 200, 30, 40, 500], 'assets': assets}

    return render(request, 'user/dashboard.html', context)

def users(request):
    return render(request, 'users.html')

def user_profile(request):
    return render(request, 'user_profile.html')



#authentications
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            if username == 'permo' and password == 'permo123':
                messages.success(request, 'You have successfully logged in')
                return redirect('adminDashboard')

            # authenticate user
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'You have successfully logged in')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login')
    else:
        form = loginForm()

    message = messages.get_messages(request)
    return render(request, 'auth/login.html', {'form': form, 'messages': message})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('login')

@csrf_exempt
def register(request, *args, **kwargs):
    code = str(kwargs.get('ref_code'))
    try:
        profile = UserProfile.objects.get(code=code)
        request.session['ref_profile'] = profile.id
    except:
        pass

    profile_id = request.session.get('ref_profile')
    print('profile_id', profile_id)

    
    form = CreateUserForm()
    profile_form = UserProfileForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            #save the user
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            if profile_id is not None:
                recommender_id = UserProfile.objects.get(id=profile_id)
                recommender_username = recommender_id.username
                #save the user
                user = form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

                # create user instance
                User_instance = User.objects.get(username=recommender_username)
                # create a recommendation instance
                profile_instance = UserProfile.objects.get(username=user.username)

                # set the user instance as the recommender
                profile_instance.recommended_by = User_instance
                # save the profile
                profile_instance.save()

                # clear the session
                del request.session['ref_profile']


            messages.success(request, 'Account created successfully.')
            return redirect('login')  # Redirect to your login page

    else:
        # form error
        form = CreateUserForm()
        profile_form = UserProfileForm()
        context = { "form":form, "profile_form":profile_form, "errors":form.errors, "errors":profile_form.errors}
    context = { "form":form, "profile_form":profile_form, "errors":form.errors, "profile_errors":profile_form.errors }

    return render(request, 'auth/register.html', context)

def reset_password(request):
    return render(request, 'auth/reset_password.html')

def reset_confirm(request):
    return render(request, 'reset_confirm.html')

def reset_complete(request):
    return render(request, 'reset_complete.html')

def reset_done(request):
    return render(request, 'reset_done.html')



# #########################transactions#########################

# save the transaction id
@csrf_exempt
def transactions_id(request):
    form = user_deposit_form()
    if request.method == 'POST':
        form = user_deposit_form(request.POST)
        if form.is_valid():
            transaction_id = form.cleaned_data['transactions_id']
            amount_paid = form.cleaned_data['amount_paid']
            name = form.cleaned_data['name']
            # check if the transaction id exists
            if UserAccount.objects.filter(transactions_id=transaction_id).exists():
                # return an error message to the user
                messages.error(request, 'Transaction ID already exists')
                return redirect('transactions_id')
            # check if the transaction id exists in Transaction_ids
            elif Transaction_ids.objects.filter(transactions_id=transaction_id).exists():
                # return an error message to the user
                messages.error(request, 'Transaction ID has already been used')
                return redirect('transactions_id')
            else:
                deposit = Deposit.objects.create(username=request.user.username,transactions_id=transaction_id, amount_paid=amount_paid, phone_number=request.user.profile.phone_number, name=name)
                deposit.save()
                # save the transaction id to the user account
                user_account = UserAccount.objects.get(username=request.user.username)
                user_account.transactions_id = transaction_id
                user_account.save()
                messages.success(request, 'Transaction ID saved successfully')
                return redirect('dashboard')
    else:
        form = user_deposit_form()

    return render(request, 'user/deposit.html', {'form': form})


# get the transaction id and display the deposit form
def transactions_history(request):
    # fetch all the transactions
    return render(request, 'transactions/transactions_history.html')

def deposited_amount(request):
    user = Deposit.objects.all().order_by('-date')
    return render(request, 'transactions/deposit.html', {'user': user})

def deposit_completed(request):
    transactions = Transaction_ids.objects.all().order_by('-date')
    return render(request, 'transactions/deposit_completed.html', {'transactions': transactions})
@csrf_exempt
def make_deposit(request, id):
    try:
        # get the user
        user = Deposit.objects.get(id=id)
        # get the transaction id
        transaction_id = user.transactions_id
        # get the amount deposited
        amount = user.amount_paid
        # get the user account
        
        # check whether the transaction exists in Transaction_ids
        if Transaction_ids.objects.filter(transactions_id=transaction_id).exists():
            # return an error message to the user
            messages.error(request, 'Transaction ID already has ever been used')
            return redirect('deposited_amount')

        user_account = UserAccount.objects.get(transactions_id=transaction_id)
        # add the amount deposited to the user's account
        user_account.amount_paid = amount
        # add the amount deposited to the user's account balance
        user_account.balance += amount
        # add a paid to the transaction id
        user_account.transactions_id += 'Paid'
        # save the user account
        user_account.save()
        # save the transaction id and the deposited amount to the Transaction_ids model
        transaction_id = Transaction_ids.objects.create(user=user_account.username, transactions_id=transaction_id, amount_deposited=amount, name=user.name)
        transaction_id.save()
        # update balance and bonus if the user has been recommended by another user
        if UserProfile.objects.get(username = user_account.username).recommended_by:
            # give a 25% bonus to the user who recommended this user after deposit
            recommended_by = UserProfile.objects.get(username=user_account.username)
            recommender = recommended_by.recommended_by
            recommender_account = UserAccount.objects.get(username=recommender)
            #check if he has some withdrawal transactions
            recommmender_withdrawals = Withdrawal.objects.filter(username=recommender)
            recommended_account = UserAccount.objects.get(username=user_account.username)
            # check if the recommender has ever deposited
            if recommender_account.balance > 0 or recommmender_withdrawals.exists():
                if recommender_account.bonus_given == False:
                    if recommended_account.bonus_given == False:
                        bonus = amount * 25
                        recommender_account.bonus += bonus / 100
                        # add the bonus to the recommender's account balance
                        recommended_account.bonus_given = True
                        # save the accounts
                        recommended_account.save()    
                        recommender_account.save()
                        messages.success(request, 'deposit successful + bonus awarded')
                        # delete the deposit after deposit
                        user.delete()
                        return redirect('deposited_amount')
                    else:
                        # delete the deposit after deposit
                        user.delete()
                        messages.success(request, 'deposit successful by ' + user.username)
                        return redirect('deposited_amount')
                else:
                    # delete the deposit after deposit
                    user.delete()
                    messages.success(request, 'deposit successful and no bonus by ' + user.username)
                    return redirect('deposited_amount')
            else:
                # delete the deposit after deposit
                user.delete()
                messages.success(request, 'deposit successful by ' + user.username)
                return redirect('deposited_amount')
        else:
            # delete the deposit after deposit
            user.delete()
            messages.success(request, 'deposit successful by ' + user.username)
            return redirect('deposited_amount')
    except Deposit.DoesNotExist:
        messages.error(request, 'deposit failed')
        return redirect('deposited_amount')
    except Deposit.MultipleObjectsReturned:
        messages.error(request, 'Two or more transaction id found')
        return redirect('deposited_amount')
    except UserAccount.DoesNotExist:
        messages.error(request, 'deposit failed')
        return redirect('deposited_amount')

def transactions_completed(request):
    return render(request, 'transactions_completed.html')


# deposit logic
@csrf_exempt
def deposit(request):
    transaction = request.session.get('transaction_id')
    form = deposit_form()
    context = {'form': form}
    if request.method == 'POST':
        try:
            form = deposit_form(request.POST)
            if form.is_valid():
                print('transaction id', transaction)
                deposit = form.cleaned_data['balance']
                balance = UserAccount.objects.get(transactions_id=transaction)
                print('balance', balance)
                balance.balance += deposit
                # save the balance
                balance.save()
                # get the username using the transaction id
                username = UserAccount.objects.get(transactions_id=transaction).username
                # check if the user has been recommended by another user
                if UserProfile.objects.get(username = username).recommended_by:
                        # give a 25% bonus to the user who recommended this user after deposit
                        recommended_by = UserProfile.objects.get(username=username)
                        recommender = recommended_by.recommended_by
                        recommender_account = UserAccount.objects.get(username=recommender)
                        recommended_account = UserAccount.objects.get(username=username)
                        # check if the recommender has ever deposited
                        if recommender_account.balance > 0:
                            if recommender_account.bonus_given == False:
                                if recommended_account.bonus_given == False:
                                    bonus = deposit * 25
                                    recommender_account.bonus += bonus / 100
                                    # add the bonus to the recommender's account balance
                                    recommender_account.balance += bonus / 100
                                    recommended_account.bonus_given = True
                                    # save the accounts
                                    recommended_account.save()    
                                    recommender_account.save()
                                  
                            else:
                                balance.save()
                                messages.success(request, 'deposit successful + bonus awarded')

                                # return redirect('workplace')
                else:
                    # save the balance
                    balance.save()
                    messages.success(request, 'deposit successful to ' + username)
                    # return redirect('workplace')
                 # save the transaction id and the deposited amount to the Transaction_ids model
                transaction_username = UserAccount.objects.get(transactions_id=transaction)
                transaction_id = Transaction_ids.objects.create(user=transaction_username.username, transactions_id=transaction, amount_deposited=deposit)
                transaction_id.save()
                # # edit the tranasaction id to show that the user has deposited
                transaction_username.transactions_id += 'Paid'
                transaction_username.save()

                return redirect('workplace')

        
        # show that the transaction id has been updated to show that the user has deposited
        except UserAccount.DoesNotExist:
            messages.success(request, 'deposit successful')
            return redirect('workplace')
        except UserAccount.MultipleObjectsReturned:
            messages.error(request, 'Two or more transaction id found')
            return redirect('workplace')    
    else:
        form = deposit_form()
        context = {'form': form}
    return render(request, 'admin/amount.html', context)

def make_withdraw(request, id):
    try:
        # get the current date
        current_date = timezone.now()
        if current_date.weekday() >= 5:
            messages.error(request, "Withdrawals are done on weekdays only")
            return redirect('amount_withdrawn')
        else:
            # get the user
            withdrawing_user = WithdrawalRequest.objects.get(id=id)
            # get the amount to withdraw
            amount = withdrawing_user.amount
            # get the user account
            user_account = UserAccount.objects.get(username=withdrawing_user.username)
            phone_number = UserProfile.objects.get(username=withdrawing_user.username).phone_number
            # check if the user has enough balance all together with bonus
            total_balance = user_account.balance + user_account.bonus
            if total_balance >= amount:
                # withdraw the amount
                user_account.balance -= amount
                if user_account.balance < 0:
                    # withdraw the amount
                    user_account.bonus += user_account.balance
                    user_account.balance = 0
                # save the user account
                user_account.save()
                # save the amount withdrawn
                withdraw = Withdrawal.objects.create(username=withdrawing_user.username, withdrawn=amount, phone_number=phone_number, name=withdrawing_user.confirmation_name, status=True)
                withdraw.save()
                messages.success(request, 'withdrawal successful')
                # delete the withdrawal request
                withdrawing_user.delete()
                return redirect('amount_withdrawn')
            else:
                messages.error(request, 'insufficient balance')
                return redirect('amount_withdrawn')
    except WithdrawalRequest.DoesNotExist:
        messages.error(request, 'withdrawal failed')
        return redirect('amount_withdrawn')
    except WithdrawalRequest.MultipleObjectsReturned:
        messages.error(request, 'Two or more transaction id found')
        return redirect('amount_withdrawn')
    except UserAccount.DoesNotExist:
        messages.error(request, 'withdrawal failed')
        return redirect('amount_withdrawn')

@csrf_exempt
def withdraw_request(request):
    balance = UserAccount.objects.get(username=request.user.username).balance
    withdrawable = balance + UserAccount.objects.get(username=request.user.username).bonus
    form = withdraw_form()
    if request.method == 'POST':
        form = withdraw_form(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            phone_number = form.cleaned_data['phone_number']
            confirmation_name = form.cleaned_data['confirmation_name']
            #first check if the user has already requested for a withdrawal
            current_date = timezone.now()
            if current_date.weekday() >= 5:
                messages.error(request, "Withdrawals are done on weekdays only")
                return redirect('withdraw')
            else:
                if WithdrawalRequest.objects.filter(username=request.user.username).exists():
                    messages.error(request, 'Wait kindly as we process the previous withdrawal')
                    return redirect('withdraw')
                # check if the user has enough balance all together with bonus
                user_account = UserAccount.objects.get(username=request.user.username)
                total_balance = user_account.balance + user_account.bonus
                if total_balance < amount:
                    messages.error(request, 'insufficient balance')
                    return redirect('withdraw')
                elif amount < 1000:
                    messages.error(request, 'minimum withdrawal amount is 1000')
                    return redirect('withdraw')
                # save the amount to the withdrawal request model
                withdraw = WithdrawalRequest.objects.create(username=request.user.username, amount=amount, phone_number=phone_number, confirmation_name=confirmation_name)
                withdraw.save()
                messages.success(request, 'withdrawal request successful')
                return redirect('withdraw_status')
    context = {'form': form, 'balance': balance, 'withdrawable': withdrawable}
    return render(request, 'user/withdraw.html', context)

def withdraw_status(request):
    withdraw = WithdrawalRequest.objects.all().order_by('date')
    return render(request, 'user/withdraw_status.html', {'withdraw': withdraw})

def amount_withdrawn(request):
    user = WithdrawalRequest.objects.all().order_by('-date')
    return render(request, 'transactions/withdrawal.html', {'user': user})

def withdraw_status_completed(request):
    withdraw = Withdrawal.objects.filter(username=request.user.username).order_by('-date')
    return render(request, 'user/withdraw_completed.html', {'withdraw': withdraw})

def withdraw_completed(request):
    withdraw = Withdrawal.objects.all().order_by('-date')
    return render(request, 'transactions/withdraw_completed.html', {'withdraw': withdraw})

def withdraw_status_pending(request):
    withdraw = WithdrawalRequest.objects.filter(username=request.user.username)
    #return a HttpResponse of all the active users withdraw request 
    return render(request, 'user/withdraw_pending.html', {'withdraw': withdraw})

# Items
@login_required(login_url='login')
def assets(request):
    items = Item.objects.all()
    #get user balance
    user_balance = "{:,.2f}".format(UserAccount.objects.get(username=request.user.username).balance)
    return render(request, 'assets/assets.html', {'items': items, 'balance': user_balance})


def purchase_item(request, id):
    items = Item.objects.get(pk=id)
    user = UserAccount.objects.get(username=request.user)
    user_profile = UserProfile.objects.get(username=request.user)
    total_balance = user.balance + user.bonus
    if total_balance >= items.price:
       # deduct the amount from the user account
        if user.balance >= items.price:
            user.balance -= items.price
            user.save()
        else:
            total_balance -= items.price
            user.balance = 0
            user.bonus = total_balance
        user.save()
        # save the purchase
        purchase = Purchase(user=user_profile, item=items, price=items.price, release_amount=items.release_amount, title=items.title, description=items.description, image=items.image.url)
        purchase.save()
        messages.success(request, 'purchased successful')
        return redirect('purchase_success',id=id)
    else:
        messages.error(request, 'insufficient balance')
        return redirect('assets')
    
def purchase_success(request, id):
    items = Item.objects.filter(pk=id)
    balance = "{:,.2f}".format(UserAccount.objects.get(username=request.user.username).balance)
    return render(request, 'assets/purchase_success.html', {'items': items  , 'balance': balance})

def purchased_items(request):
    purchases = Purchase.objects.filter(user=request.user.profile)
    profit = 0
    for purchase in purchases:
        profit += purchase.profit
    profit = "{:,.2f}".format(profit)

    return render(request, 'assets/purchased_items.html', {'purchases': purchases, 'profit': profit})

# ***************recommendation***************
def recommended_users(request):
    profile = []
    for prof in UserProfile.objects.all():
        if prof.recommended_by == request.user:
            profile.append(prof)
        #count the number of recommended users
    recommended_users = len(profile)
    return HttpResponse('recommended_users: ' + str(recommended_users))

# ***************edit users***************

# delete a user
def destroy(request, id): 
    user = User.objects.get(id=id)
    user.delete()
    return redirect("all_users")  

# delete a transaction
def destroy_transaction(request, id):
    transaction = Transaction_ids.objects.get(id=id)
    transaction.delete()
    return redirect('transactions_history')

# delete a deposit
def destroy_deposit(request, id):
    user = Deposit.objects.get(id=id)
    user.delete()
    return redirect('deposited_amount')

def destroy_withdraw(request, id):
    user = WithdrawalRequest.objects.get(id=id)
    user.delete()
    return redirect('amount_withdrawn')

#ajax requests
def get_chart_data(request):
    # Replace this with your actual logic to fetch updated data
    updated_data = [12, 99, 0, 6, 70]
    return JsonResponse({'data': updated_data})


# get the transaction id and display the deposit form
@csrf_exempt
def get_transaction(request):
    # get the posted data
    if request.method == 'POST':
            form = transactions_id_form(request.POST)
            if form.is_valid():
                transaction_id = form.cleaned_data['transactions_id']
                request.session['transaction_id'] = transaction_id
                # check if the transaction id exists
                if UserAccount.objects.filter(transactions_id=transaction_id).exists():
                    # display the deposit form
                    return redirect('deposit')
                else:
                   # display an error message
                    messages.error(request, 'invalid transaction id')
                    return redirect('workplace')
            else:
                messages.error(request, 'invalid form')
                return redirect('workplace')
    else:
        return redirect('workplace')


# refresh customer count
def customers(request):
    users = User.objects.all()
    user_count = len(users)
    return HttpResponse(user_count)

# refresh how many users have deposited
def deposited(request):
    deposits = Deposit.objects.all().order_by('-date')
    deposits_count = len(deposits)
    return HttpResponse(deposits_count)

# refresh balance
def refresh_balance(request):
    total_amount = 0
    for user in UserProfile.objects.all():
        total_amount += user.UserAccount.balance
    balance = total_amount
    return HttpResponse(balance)


######################### STK #################################
@login_required
@csrf_exempt
def stkpush(request):

    form = StkpushForm()

    return render(request, 'user/deposit.html', {"form":form})

@csrf_exempt
def init_stk(request):
    if request.method == 'POST':
        form = StkpushForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            
            cl = MpesaClient()
            phone_number = str(phone)
            account_reference = 'reference'
            transaction_desc = 'Description'
            callback_url = 'https://monadoll.tech/callback'
            # callback_url = 'https://permo.pythonanywhere.com/callback'
            
            try:
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                response_data = response.json()
                
                if response_data.get("ResponseCode") == '0':
                    MpesaRequest.objects.create(
                        user=request.user,
                        amount=amount,
                        phone_number=phone,
                        description=response_data["ResponseDescription"],
                        merchant=response_data["MerchantRequestID"],
                        status=response_data["CustomerMessage"],
                    )
                    context = {"response": response_data}
                else:
                    MpesaRequest.objects.create(
                        user=request.user,
                        amount=amount,
                        phone_number=phone,
                        description=response_data.get("errorMessage", "Unknown error"),
                        status="Failed",
                    )
                    context = {"response": response_data}
            except requests.exceptions.RequestException as e:
                context = {"error": str(e)}
            except ValueError as e:
                context = {"error": str(e)}
            except Exception as e:
                context = {"error": str(e)}
        
        return render(request, 'user/stkresult.html', context)

    return render(request, 'user/stkresult.html', context)

####################### END STK ###############################

###################### Callback ############################
@method_decorator(csrf_exempt, name='dispatch')
class MpesaStkPushCallbackView(View):
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        merchant_request_id = stk_callback.get('MerchantRequestID', '')
        checkout_request_id = stk_callback.get('CheckoutRequestID', '')
        result_code = stk_callback.get('ResultCode', '')
        result_desc = stk_callback.get('ResultDesc', '')
        callback_metadata = stk_callback.get('CallbackMetadata', {})
        items = callback_metadata.get('Item', [])
        # data = json.loads(request.body)['Body']['stkCallback']
        
        # print(data['ResultCode'])
        print(result_code)
        print(data)

        if result_code == 0:
            print(data)
            callback_metadata = items
            # Extracting the necessary data from the callback metadata
            amount = next(item['Value'] for item in callback_metadata if item['Name'] == 'Amount')
            print(amount)
            mpesa_receipt_number = next(item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber')
            print(mpesa_receipt_number)
            transaction_date = next(item['Value'] for item in callback_metadata if item['Name'] == 'TransactionDate')
            print(transaction_date)
            phone_number = next(item['Value'] for item in callback_metadata if item['Name'] == 'PhoneNumber')
            print(phone_number)

            # check for macthing merchant and save the amount to the user with the matching merchant

            # saved merchant
            user = MpesaRequest.objects.get(merchant=merchant_request_id).user
            print(user)
            # get the account associated with the user
            account = UserAccount.objects.get(username=user)
            account.balance += Decimal(amount)
            account.save()
            # user.amount += Decimal(amount)
            # user.save()
            # print(user.amount)
            # print(data)

            d = json.loads(request.body.decode('utf-8'))
            body = d.get('Body', {})
            stk_callback = body.get('stkCallback', {})

            # Creating the MpesaPayment entry
            MpesaPayment.objects.create(
                    amount=amount,
                    description= result_desc,
                    type="CustomerPayBillOnline",  # Assuming type from the initial request
                    reference=mpesa_receipt_number,
                    first_name="",  # If available, extract from another part of the callback or request
                    middle_name="",
                    last_name="",
                    phone_number=phone_number,
                    organization_balance=0.00,  # Assuming no balance provided in the callback
                    is_finished=True,
                    is_successful=True,
                    trans_id=mpesa_receipt_number,
                    order_id="",  # If available, extract from another part of the callback or request
                    checkout_request_id= checkout_request_id,
                    # merchant = data["Body"]["stkCallback"]["MerchantRequestID"]
                    merchant = stk_callback.get('MerchantRequestID', '')
                    )

            print("saved successfully in the database")

        else:
            # Handle failed transaction
            MpesaPayment.objects.create(
                    amount=0.00,
                    description= result_desc,
                    type="CustomerPayBillOnline",
                    reference="",
                    first_name="",
                    middle_name="",
                    last_name="",
                    phone_number="",
                    organization_balance=0.00,
                    is_finished=True,
                    is_successful=False,
                    trans_id="",
                    order_id="",
                    checkout_request_id= checkout_request_id,
                    merchant = "",
                    )
            print('error')
        return HttpResponse(data)
########################### End Callback #################################

