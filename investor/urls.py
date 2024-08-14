#urlpatterns

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
from .views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #users
    path('', views.landing_page, name='landing_page'),
    path('deposit/', views.transactions_id, name='transactions_id'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('recommended_users/', views.recommended_users, name='recommended_users'),
    path('all_users/', views.all_users, name='all_users'),
    path('delete/<int:id>', views.destroy, name='destroy'),
    path('delete_transaction/<int:id>', views.destroy_transaction, name='destroy_transaction'),
    path('destroy_deposit/<int:id>', views.destroy_deposit, name='destroy_deposit'),

    #authentications
    path('auth/login', views.login_view, name='login'),
    path('auth/reset_password/', auth_views.PasswordResetView.as_view(template_name='auth/reset_password.html'), name='reset_password'),
    path('auth/register/', views.register, name='register'),
    path('auth/register/<str:ref_code>/', views.register, name='register'),
    path('auth/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='reset_complete'),
    path('auth/reset_done/', auth_views.PasswordResetDoneView.as_view(), name='reset_done'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # ******************************************
    # ***************transactions***************
    # ******************************************

    path('transactions/id', views.transactions_id, name='transactions_id'),
    path('transactions_history/', views.transactions_history, name='transactions_history'),
    path('transactions_completed/', views.transactions_completed, name='transactions_completed'),
    path('staff/admin/auth/workplace', views.admin_workplace, name='workplace'),
    path('staff/admin/auth/amount', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw_request, name='withdraw'),
    path('withdraw_status/', views.withdraw_status, name='withdraw_status'),
    path('make_deposit/<int:id>', views.make_deposit, name='make_deposit'),
    path('deposited_amount/', views.deposited_amount, name='deposited_amount'),
    path('make_withdraw/<int:id>', views.make_withdraw, name='make_withdraw'),
    path('destroy_withdraw/<int:id>', views.destroy_withdraw, name='destroy_withdraw'),
    path('amount_withdrawn/', views.amount_withdrawn, name='amount_withdrawn'),

    # Ajax
    path('withdraw_status/completed/', views.withdraw_status_completed, name='withdraw_status_completed'),
    path('withdraw_status/pending/', views.withdraw_status_pending, name='withdraw_status_pending'),
    path('transactions_history/withdraw_completed/', views.withdraw_completed, name='withdraw_completed'),
    path('transactions_history/deposit_completed/', views.deposit_completed, name='deposit_completed'),
    # ############################################
    # ################transactions################
    # ############################################


    #assets
    path('assets/', views.assets, name='assets'),
    path('purchase/<int:id>', views.purchase_item, name='purchase_item'),
    path('purchase/success/<int:id>/', views.purchase_success, name='purchase_success'),
    path('purchased_items/', views.purchased_items, name='purchased_items'),

    #admin
    
    path('staff/admin/auth/admin_login/', views.adminLogin, name='admin_login'),
    path('staff/admin/auth/adminDashboard', views.adminDashboard, name='adminDashboard'),
    path('staff/admin/auth/admin_workplace/', views.admin_workplace, name='admin_workplace'),
    path('staff/admin/auth/admin_logout/', views.admin_logout, name='admin_logout'),
    path('staff/admin/auth/admin_users/', views.admin_users, name='admin_users'),

    #charts(ajax)
    path('get_chart_data/', views.get_chart_data, name='get_chart_data'),
    path('get_transaction/', views.get_transaction, name='get_transaction'),
    
    # refresh customers
    path('customers/', views.customers, name='customers'),

    # refresh deposited
    path('deposited/', views.deposited, name='deposited'),

    # refresh_balance
    path('refresh_balance/', views.refresh_balance, name='refresh_balance'),
    path('stk', views.stkpush, name='stk'),
    path('stkpush', views.init_stk, name='stkpush'),
    # path('callback', views.callback, name='callback'),

    path('callback', MpesaStkPushCallbackView.as_view(), name='mpesa-stk-push-callback'),
   ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
