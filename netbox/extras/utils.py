from django.db.models import Q
from django.utils.deconstruct import deconstructible
from taggit.managers import _TaggableManager

from extras.constants import EXTRAS_FEATURES
from extras.registry import registry


def is_taggable(obj):
    """
    Return True if the instance can have Tags assigned to it; False otherwise.
    """
    return bool(
        hasattr(obj, 'tags')
        and issubclass(obj.tags.__class__, _TaggableManager)
    )


def image_upload(instance, filename):
    """
    Return a path for uploading image attchments.
    """
    path = 'image-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name:
        if extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png']:
            filename = '.'.join([instance.name, extension])
        else:
            filename = instance.name

    return f'{path}{instance.content_type.name}_{instance.object_id}_{filename}'


@deconstructible
class FeatureQuery:
    """
    Helper class that delays evaluation of the registry contents for the functionality store
    until it has been populated.
    """
    def __init__(self, feature):
        self.feature = feature

    def __call__(self):
        return self.get_query()

    def get_query(self):
        """
        Given an extras feature, return a Q object for content type lookup
        """
        query = Q()
        for app_label, models in registry['model_features'][self.feature].items():
            query |= Q(app_label=app_label, model__in=models)

        return query


def register_features(model, features):
    for feature in features:
        if feature not in EXTRAS_FEATURES:
            raise ValueError(f"{feature} is not a valid extras feature!")
        app_label, model_name = model._meta.label_lower.split('.')
        registry['model_features'][feature][app_label].add(model_name)
