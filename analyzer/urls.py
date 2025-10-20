from django.urls import path
from . import views

urlpatterns = [
    path('strings', views.StringListCreateView.as_view(), name='string-list-create'),
    path('strings/filter-by-natural-language', views.StringNaturalLanguageFilterView.as_view(), name='string-natural-language-filter'),
    path('strings/<str:string_value>', views.StringDetailView.as_view(), name='string-detail'),
    
]
