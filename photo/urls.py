from django.urls import path

from . import views

app_name = 'photo'
urlpatterns = [
     # HTML
     path('', views.DistortView.as_view(), name='home'),
     path('upload/', views.UploadImageView.as_view(), name='upload'),
     path('distort/', views.DistortView.as_view(), name='distort'),
     path('features/', views.FeaturesDetectorView.as_view(), name='features'),
     path('matcher/', views.FeaturesMatcherView.as_view(), name='matcher'),
     path('stitcher/', views.ImageStitcherView.as_view(), name='stitcher'),

     # API TODO USE django-rest
     path('distort/api/<int:pk>', views.Distort.as_view(),
          name='api-distort'),
     path('features/api/<int:pk>', views.FeaturesDetector.as_view(),
          name='api-features'),
     path('matcher/api/<int:pk1>_<int:pk2>', views.FeaturesMatcher.as_view(),
          name='api-matcher'),
     path('stitcher/api/<int:pk1>_<int:pk2>', views.ImageStitcher.as_view(),
          name='api-stitcher'),
]
