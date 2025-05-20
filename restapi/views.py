from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,CustomUserEditForm,CourseForm
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Course, Enrollment
from .serializers import (
    UserSerializer, 
    CourseSerializer, 
    EnrollmentSerializer, 
    CreateEnrollmentSerializer
)
from .permissions import (
    IsAdmin, 
    IsTeacher, 
    IsStudent, 
    IsCourseTeacher, 
    IsEnrollmentStudent
)
from django.shortcuts import get_object_or_404

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Course.objects.all()
        elif user.is_teacher():
            return Course.objects.filter(teacher=user)
        else:
            return Course.objects.all()

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()  # Add this line
    serializer_class = EnrollmentSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateEnrollmentSerializer
        return EnrollmentSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsStudent]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Enrollment.objects.all()
        elif user.is_teacher():
            return Enrollment.objects.filter(course__teacher=user)
        else:
            return Enrollment.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(student=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            EnrollmentSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.is_admin():
        return render(request, 'admin_dashboard.html')
    elif request.user.is_teacher():
        return render(request, 'teacher_dashboard.html')
    else:
        return render(request, 'student_dashboard.html')

@login_required
def user_list_view(request):
    if not request.user.is_admin():
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
def course_list_view(request):
    if request.user.is_admin():
        courses = Course.objects.all()
    elif request.user.is_teacher():
        courses = Course.objects.filter(teacher=request.user)
    else:
        courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

@login_required
def enrollment_list_view(request):
    if request.user.is_admin():
        enrollments = Enrollment.objects.all()
    elif request.user.is_teacher():
        enrollments = Enrollment.objects.filter(course__teacher=request.user)
    else:
        enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'enrollment_list.html', {'enrollments': enrollments})


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Course, Enrollment
from .serializers import (
    UserSerializer, 
    CourseSerializer, 
    EnrollmentSerializer, 
    CreateEnrollmentSerializer
)
from .permissions import (
    IsAdmin,
    IsTeacher,
    IsStudent,
    IsCourseTeacherOrAdmin,
    IsEnrollmentStudentOrCourseTeacherOrAdmin,
    CanEnroll
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # All authenticated users can view courses
            permission_classes = [IsAdmin | IsTeacher | IsStudent]
        elif self.action in ['create']:
            # Only teachers and admins can create courses
            permission_classes = [IsAdmin | IsTeacher]
        else:
            # Only course teacher or admin can update/delete
            permission_classes = [IsCourseTeacherOrAdmin]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Automatically set the teacher to the current user if they're a teacher
        if self.request.user.role == 'teacher':
            serializer.save(teacher=self.request.user)
        else:
            serializer.save()
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        elif user.role == 'teacher':
            return Course.objects.filter(teacher=user)
        else:  # student
            return Course.objects.all()

    @action(detail=True, methods=['get'], permission_classes=[IsAdmin | IsTeacher])
    def enrollments(self, request, pk=None):
        course = self.get_object()
        if request.user.role == 'teacher' and course.teacher != request.user:
            return Response(
                {"detail": "You can only view enrollments for your own courses."},
                status=status.HTTP_403_FORBIDDEN
            )
        enrollments = course.enrollments.all()
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdmin | IsTeacher | IsStudent]
        elif self.action in ['create']:
            permission_classes = [CanEnroll]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsEnrollmentStudentOrCourseTeacherOrAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateEnrollmentSerializer
        return EnrollmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Enrollment.objects.all()
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__teacher=user)
        else:  # student
            return Enrollment.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course_id = serializer.validated_data['course'].id
        course = Course.objects.get(id=course_id)
        
        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course,
            is_active=True
        ).exists()
        
        if existing_enrollment:
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = serializer.save(student=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_destroy(self, instance):
        # Instead of deleting, set is_active to False
        instance.is_active = False
        instance.save()



#crud  operation user by admin
@login_required
def user_create_view(request):
    if not request.user.is_admin():
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_form.html', {'form': form, 'title': 'Add New User'})
@login_required
def user_edit_view(request, user_id):
    if not request.user.is_admin():
        return redirect('dashboard')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, 'user_form.html', {'form': form, 'title': 'Edit User'})

@login_required
def user_delete_view(request, user_id):
    if not request.user.is_admin():
        return redirect('dashboard')

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'confirm_delete.html', {'user': user})


# crud operation course by admin 

@login_required
def course_create_view(request):
    if not (request.user.is_teacher() or request.user.is_admin()):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form, 'title': 'Create Course'})

@login_required
def course_edit_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not (request.user == course.teacher or request.user.is_admin()):
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form, 'title': 'Edit Course'})

@login_required
def course_delete_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not (request.user == course.teacher or request.user.is_admin()):
        return redirect('dashboard')

    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'confirm_delete.html', {'course': course})


#course enrol by student
from django.contrib import messages
from django.core.exceptions import ValidationError

@login_required
def enroll_in_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST' and request.user.is_student():
        try:
            # Check if already enrolled
            already_enrolled = Enrollment.objects.filter(course=course, student=request.user, is_active=True).exists()
            if already_enrolled:
                messages.info(request, "You are already enrolled in this course.")
            else:
                # Create enrollment
                enrollment = Enrollment(course=course, student=request.user)
                enrollment.full_clean()  # Will raise ValidationError if >5 courses
                enrollment.save()
                messages.success(request, "Successfully enrolled in the course.")
        except ValidationError as e:
            messages.error(request, "You can’t enroll in more than 5 courses. Complete your existing ones first.")
    
    return redirect('course_list')  # অথবা যেখানে তুমি redirect করতে চাও
