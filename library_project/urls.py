
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from library_project import settings
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/logout/', views.custom_logout, name='logout'),
    path('accounts/', include('accounts.urls')),
    path('', include('library.urls')),
    path('payment/', include('payment.urls', namespace='payment'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)