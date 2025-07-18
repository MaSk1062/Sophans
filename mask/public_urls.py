
from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from mapalo import views as m_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("mapalo.urls")),
    path("login/", auth_views.LoginView.as_view(template_name='mapalo/auth/login.html'), name='public-login'),
    path('logout/', m_views.landlordLogout, name='public-logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='mapalo/auth/passwordchange.html') ,name='public-password-change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='mapalo/auth/passwaordchange_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='mapalo/auth/password_reset.html', email_template_name='stephan/reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='mapalo/auth/Passwordreset_done.html') , name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='mapalo/auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='mapalo/auth/passwordreset_complete.html'), name='password_reset_complete'),
    path('payment/', include('payment.urls')),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
