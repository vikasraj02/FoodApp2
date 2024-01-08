from django.core.exceptions import ValidationError
import os

def allow_only_Images_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_ext = ['.png','.jpg','.jpeg']
    if not ext.lower() in valid_ext:
        return ValidationError('Unsupported file extension. allowed extensions ' + str(valid_ext))