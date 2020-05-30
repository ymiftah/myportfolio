''' Views of the photo app'''

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from .forms import PhotoForm
from .models import PhotoModel
from .utils.utils import img_distort, img_features, img_features_matcher, img_stitcher


def home(request):
    ''' Return a basic hello world view'''
    return HttpResponse("Hello, world. You're at the polls index.")


class UploadImageView(View):
    form_class = PhotoForm
    # initial = {'name': 'None', 'img_file': None}
    template_name = 'photo/upload.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect(reverse('photo:display'))

        return render(request, self.template_name, {'form': form})


class DistortView(ListView):
    model = PhotoModel
    template_name = 'photo/distort_img.html'


class FeaturesDetectorView(ListView):
    model = PhotoModel
    template_name = 'photo/features_img.html'


class FeaturesMatcherView(ListView):
    model = PhotoModel
    template_name = 'photo/matcher_img.html'


class ImageStitcherView(ListView):
    model = PhotoModel
    template_name = 'photo/stitcher_img.html'


# from django.http import Http404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status


class Distort(View):
    def get(self, request, pk, *args, **kwargs):
        img = PhotoModel.objects.get(pk=pk)
        params = [
            request.GET.get('f', None),
            request.GET.get('k1', None),
            request.GET.get('k2', None)
        ]

        img = img_distort(img.img_file, params)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response


class FeaturesDetector(View):
    def get(self, request, pk, *args, **kwargs):
        img = PhotoModel.objects.get(pk=pk)
        params = [
            request.GET.get('tol', 1),
        ]

        img = img_features(img.img_file, params)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response


class FeaturesMatcher(View):
    def get(self, request, pk1, pk2, *args, **kwargs):
        img1 = PhotoModel.objects.get(pk=pk1)
        img2 = PhotoModel.objects.get(pk=pk2)
        params = [
            request.GET.get('num', 10),
        ]

        img = img_features_matcher(img1.img_file, img2.img_file, params)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response


class ImageStitcher(View):
    def get(self, request, pk1, pk2, *args, **kwargs):
        img1 = PhotoModel.objects.get(pk=pk1)
        img2 = PhotoModel.objects.get(pk=pk2)

        img = img_stitcher(img1.img_file, img2.img_file)
        response = HttpResponse(content_type="image/png")
        img.save(response, "PNG")
        return response

# class DistortImage(APIView):
#     """
#     Compute distorted image from selection + parameters
#     and respond with the path to the image
#     """

#     def post(self, request, format=None):
#         data = request.data
#         if data is not None:
#             print(data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)