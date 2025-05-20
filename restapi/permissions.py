from rest_framework.permissions import BasePermission
from .models import Enrollment  # Add this import at the top
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher()

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student()

class IsCourseTeacher(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.teacher == request.user

class IsEnrollmentStudent(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user

from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsCourseTeacherOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return hasattr(obj, 'teacher') and obj.teacher == request.user

class IsEnrollmentStudentOrCourseTeacherOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'teacher' and obj.course.teacher == request.user:
            return True
        return obj.student == request.user

class CanEnroll(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'student':
            return False
        # Check if student has less than 5 active enrollments
        active_enrollments = Enrollment.objects.filter(student=request.user, is_active=True).count()
        return active_enrollments < 5