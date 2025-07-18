from django.urls import path
from mapalo import views
from .views import BlacklistListView, BlacklistUpdateView, BlacklistDeleteView

urlpatterns = [
    path('', views.home, name='sophans'),
    path('signup/', views.signup, name='public-signup'),
    path('profile-finish/', views.profileFinish, name='profile-finish'),
    path('profile/', views.profileview, name='public-profile'),
    path('subdomain/', views.subDomainRedirect, name="my-domain"),
    path('profile_edit/', views.profileEdit, name="profile-edit"),
    path('features/', views.features, name="features"),
    path('about-sophans/', views.about, name="about-sophans"),
    path('sophans-terms/', views.terms, name="sophans-terms"),
    path('signup-terms/', views.signupTerms, name="signup-terms"),
    path('agree/', views.termsAggreement, name="agree"),
    path("feedback/", views.submit_feedback, name="feedback"),
    path("feedback-send/", views.feedback, name="feedback-send"),
    path("public_settings/", views.publicSettings, name="public-settings"),
    path("email_change/", views.emailChange, name="email-change"),
    path("account_delete/", views.accountDelete, name="account-delete"),
    path("welcome_message/", views.welcome_email, name="wellcome"),
    path("blacklist_tenant/", views.blacklist_tenant, name="blacklist_form"),
    path("blacklists/", BlacklistListView.as_view() , name="blacklists"),
    path("blacklist_update/<int:pk>/", BlacklistUpdateView.as_view() , name="blacklist-update"),
    path("blacklist_delete/<int:pk>/", BlacklistDeleteView.as_view() , name="blacklist-delete"),
]