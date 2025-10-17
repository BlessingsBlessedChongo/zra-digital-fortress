from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/blockchain/', include('blockchain.urls')),
    path('api/v1/ai/', include('ai_engine.urls')),
]