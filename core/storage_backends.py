from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class PublicMediaStorage(S3Boto3Storage):
    location = settings.PUBLIC_MEDIA_LOCATION
    default_acl = 'private'  # You’re using signed URLs, so it's private
    file_overwrite = False
    custom_domain = False  # Prevents Django from trying to use MEDIA_URL
    querystring_auth = True  # Enables signed URLs