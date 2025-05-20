from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CourseViewSet, EnrollmentViewSet
from .views import (
    login_view, 
    signup_view, 
    logout_view, 
    dashboard_view,
    user_list_view,
    course_list_view,
    enrollment_list_view,
    user_create_view,
    user_edit_view,
    user_delete_view,
    course_create_view, 
    course_edit_view, 
    course_delete_view,
    enroll_in_course_view

)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')  # Add basename

urlpatterns = [
    
    # API URLs (existing)
    path('api/', include(router.urls)),
    
    # Frontend URLs
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('users/', user_list_view, name='user_list'),
    path('courses/', course_list_view, name='course_list'),
    path('enrollments/', enrollment_list_view, name='enrollment_list'),

    #user crud by admin
    path('users/create/', user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', user_edit_view, name='user_edit'),
    path('users/<int:user_id>/delete/', user_delete_view, name='user_delete'),

    #course crud by admin and teacher

    path('courses/create/', course_create_view, name='course_create'),
    path('courses/<int:course_id>/edit/', course_edit_view, name='course_edit'),
    path('courses/<int:course_id>/delete/', course_delete_view, name='course_delete'),


    #enroll
    path('courses/<int:course_id>/enroll/', enroll_in_course_view, name='enroll_in_course'),


]
