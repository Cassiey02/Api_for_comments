from rest_framework import mixins, viewsets


class DeleteCreateListViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """
    Миксин позволяет удалять, создавать объект или вернуть список объектов
    """
    pass


class UpdateRetrieveViewSet(mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """Миксин позволяет изменять и возвращать объект"""
    pass
