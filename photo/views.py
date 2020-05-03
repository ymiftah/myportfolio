''' Views of the photo app'''

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from .forms import PhotoForm
from .models import PhotoModel
from .utils import img_distort


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


class ImagesListView(ListView):
    model = PhotoModel
    template_name = 'photo/display_img.html'

    # def get(self, request, *args, **kwargs):
    #     form = self.form_class()
    #     return render(request, self.template_name, {'form': form})



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

        img = img_distort(img.img_file, params, return_img=True)
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