from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """فقط مالک پست می‌تواند آن را ویرایش یا حذف کند"""
    
    def has_object_permission(self, request, view, obj):
        # متدهای GET, HEAD, OPTIONS همیشه مجاز هستند
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # بررسی می‌کنیم که کاربر مالک پست باشد
        return obj.Profile.user == request.user

class IsProfileOwner(BasePermission):
    """فقط صاحب پروفایل می‌تواند آن را ویرایش کند"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user