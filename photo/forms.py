"""
Forms module for the photo app
"""

from django import forms
from .models import PhotoModel, DistortPhotoModel


class PhotoForm(forms.ModelForm):
    '''
    Simpler form to upload a file.\n
    Fields are 'img_file'
    '''

    class Meta:
        model = PhotoModel
        fields = ['img_file']


class DistortPhotoForm(forms.ModelForm):
    '''
    Simpler form to distort the selected image file.\n
    Fields are 'img_file', 'f', 'k1', 'k2'
    '''

    class Meta:
        model = DistortPhotoModel
        fields = ['img_file', 'f', 'k1', 'k2']
