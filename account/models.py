from django.db import models
from django.contrib.auth.models import User
from social_django.models import AbstractUserSocialAuth

# TODO: fix this bug. For now, leave it here to run correctly
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "{0}/{1}".format(instance.user.username, filename)

class CustomSocialAuthUser(AbstractUserSocialAuth):
    user = models.ForeignKey(User, on_delete=models.CASCADE)