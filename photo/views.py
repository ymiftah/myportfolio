''' Views of the photo app'''

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from .forms import UpPhotoForm
from .models import UpPhoto


def home(request):
    ''' Return a basic hello world view'''
    return HttpResponse("Hello, world. You're at the polls index.")


class UploadImageView(View):
    form_class = UpPhotoForm
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
    model = UpPhoto
    template_name = 'photo/display_img.html'

    # def get(self, request, *args, **kwargs):
    #     form = self.form_class()
    #     return render(request, self.template_name, {'form': form})
