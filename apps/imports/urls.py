from django.urls import path

from .views import ExcelImportView

app_name = 'imports'

urlpatterns = [
    path('imports/upload/', ExcelImportView.as_view(), name='upload'),
]