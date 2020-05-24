from django.urls import path

from . import views

app_name = 'photo'
urlpatterns = [
     # HTML
     path('', views.home, name='home'),
     path('upload/', views.UploadImageView.as_view(), name='upload'),
     path('distort/', views.DistortView.as_view(), name='distort'),
     path('features/', views.FeaturesDetectorView.as_view(), name='features'),
     path('matcher/', views.FeaturesMatcherView.as_view(), name='matcher'),

     # API TODO USE django-rest
     path('distort/api/<int:pk>', views.Distort.as_view(),
          name='api-distort'),
     path('features/api/<int:pk>', views.FeaturesDetector.as_view(),
          name='api-features'),
     path('matcher/api/<int:pk1>_<int:pk2>', views.FeaturesMatcher.as_view(),
          name='api-matcher'),
]
