"""
Forms module for the photo app
"""

from django import forms
from .models import UpPhoto


class UpPhotoForm(forms.ModelForm):
    '''
    Simpler form to upload a file.\n
    Fields are 'name', 'img_file'
    '''

    class Meta:
        model = UpPhoto
        fields = ['name', 'img_file']
