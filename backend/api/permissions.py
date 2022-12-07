from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    '''
    Permission class allows instance-level access only to an author
    or to requests in SAFE_METHODS (GET, OPTIONS, HEAD).
    View-level access is granted to requests in SAFE_METHODS
    or to an authenticated user.
    The class is used in RecipeViewSet.
    '''

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
