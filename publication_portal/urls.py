from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from login import views as login_views


urlpatterns = [
    path('', login_views.login_user, name='login_root'),
    path('admin/', admin.site.urls),
   	path('admin_panel/',include('admin_panel.urls')),
   	path('login/',include('login.urls')),
   	path('agent/',include('agent.urls')),
   	path('customer/',include('customer.urls')),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
