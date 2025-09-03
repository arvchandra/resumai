from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Permission is granted if user in URL matches logged-in user
    or if user_id is not present in URL.
    """

    def has_permission(self, request, view):
        url_user_id = view.kwargs.get("user_id")

        if url_user_id:
            return url_user_id == request.user.id
        else:
            return True
        