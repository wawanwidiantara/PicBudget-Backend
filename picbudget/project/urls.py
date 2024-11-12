import logging
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include, path

import picbudget.accounts.urls
import picbudget.authentication.urls
import picbudget.wallets.urls
import picbudget.transactions.urls

API_PREFIX = "api/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(API_PREFIX, include(picbudget.authentication.urls)),
    path(API_PREFIX, include(picbudget.accounts.urls)),
    path(API_PREFIX, include(picbudget.wallets.urls)),
    path(API_PREFIX, include(picbudget.transactions.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
