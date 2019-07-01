"""fusioncharts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from samples import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
"""
from django.conf.urls import url
from django.contrib import admin
from UI import graph
from UI import views
from UI import datahandler

urlpatterns = [
    url(r'^$', graph.show_chart, name='chart'),
    url(r'^count/', views.update_chart, name='update_chart'),
    url(r'^admin/', admin.site.urls),
    url(r'^datahandler', datahandler.getdata),
]
