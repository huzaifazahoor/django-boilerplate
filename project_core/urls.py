"""
URL configuration for project_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

import os

from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        lambda request: HttpResponse(
            """
        <html>
            <head>
                <title>Site Under Maintenance - Meyka</title>
                <style>
                    html, body {
                height: 100%;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: Arial, sans-serif;
                background-color: #f3f4f6;
                color: #333;
                text-align: center;
            }

                </style>
            </head>
            <body>
                <h1>Under Development<br>Please check back soon!</h1>
            </body>
        </html>
    """
        ),
    ),
    path("env/", lambda request: JsonResponse(dict(os.environ))),
]
