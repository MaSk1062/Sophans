
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
import django.contrib.auth.views as auth_views
import stephan.views as steph_views
from mask import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("stephan.urls")),
    path("login/", auth_views.LoginView.as_view(template_name='stephan/login.html'), name='tenant-login'),
    path('logout/', steph_views.landlordLogout, name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='stephan/passwordchange.html') ,name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='stephan/passwaordchange_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='stephan/password_reset.html', email_template_name='stephan/reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='stephan/Passwordreset_done.html') , name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='stephan/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='stephan/passwordreset_complete.html'), name='password_reset_complete'),
    path('lata/', include('lata.urls')),

]+ debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
