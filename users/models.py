from django.db import models
from django.conf import settings

import os
import uuid

# Create your models here.


def upload_directory(instance, filename):
    return os.path.join(settings.BASE_DIR, 'uploads/{}_{}.py'.format(instance.name, uuid.uuid4().hex))


class Game(models.Model):
    name = models.CharField(max_length=2048)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    code = models.FileField(upload_to=upload_directory)
