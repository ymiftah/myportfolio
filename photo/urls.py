from django.urls import path

from . import views

app_name = 'photo'
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.UploadImageView.as_view(), name='upload'),
    path('distort/', views.ImagesListView.as_view(), name='distort'),
    path('features/', views.ImagesListView.as_view(), name='features'),
    path('distort/api/<int:pk>', views.Distort.as_view(),
         name='api-distort'),
    path('features/api/<int:pk>', views.Distort.as_view(),
         name='api-features'),
]
