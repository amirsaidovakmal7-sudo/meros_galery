"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve as serve_static_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('favicon.ico', lambda request: HttpResponse(status=204)),
]


# django.conf.urls.static.static() only registers these routes while
# DEBUG=True — it is a no-op otherwise. This project has no separate
# web server (nginx/whitenoise/etc.) serving /static/ or /media/, so with
# DEBUG=False in settings.py (required for ALLOWED_HOSTS to work) every
# photo and every static CSS/JS file 404ed, site-wide. Wiring the same
# view in unconditionally keeps uploaded photos (and the site's own
# styling) working regardless of DEBUG.
urlpatterns += [
    re_path(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), serve_static_file, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), serve_static_file, {'document_root': settings.MEDIA_ROOT}),
]
