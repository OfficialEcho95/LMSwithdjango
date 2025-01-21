from django.urls import path
from . import assignment_views, views, lesson_view, payment_view
from LMSdjango.messaging_server import socketio_info, message_list, send_message

urlpatterns = [
    path("add_course/", views.add_course, name="add_course"),
    path("", views.course_list, name="course_list"),
    path("<int:course_id>/lessons/", lesson_view.lesson_list, name="lesson_list"),
    path("<int:course_id>/update_course", views.update_course, name="update_course"),
    path("<int:course_id>/delete/", views.delete_course, name="delete_course"),
    path("<int:course_id>/quizzes/", views.quiz_list, name="quiz_list"),
    path("enroll/<int:course_id>/<str:amount>/<str:email>", views.enroll_in_course, name="enroll_course"),
    path("<int:course_id>/course_detail", views.course_detail, name="course_detail"),
    path('course/<int:course_id>/lesson/<int:lesson_id>/', lesson_view.get_lessons_view, name='lesson_details'),
    path("<int:course_id>/add_lesson/", lesson_view.add_lesson_to_course, name="add_lesson_to_course"),
    path("lessons/<int:lesson_id>/delete_lesson", lesson_view.delete_lesson, name="delete_lesson"),
    path("lessons/<int:lesson_id>/update_lesson", lesson_view.update_lesson_view, name="update_lesson"),
    path("lessons/assignment/<int:course_id>/<int:lesson_id>/add_assignment", assignment_views.add_assignment_to_lesson, name='add_assignment_to_lesson'),
    path("lessons/<int:course_id>/<int:lesson_id>/lesson/", lesson_view.get_lessons_view, name="get_lesson"),
    path("lessons/assignment/<int:course_id>/<int:lesson_id>/assignments/", assignment_views.get_assignments_view, name="lesson_assignment"),
    path("lessons/submit_assignment/<int:course_id>/<int:lesson_id>/<int:assignment_id>/assignment", assignment_views.submit_assignment_view, name="submit_assignment"),
    path('purchase_course/initialize-payment/<int:course_id>/<str:amount>/<str:email>', payment_view.initialize_payment, name='initialize_payment'),
    path('verify-payment/<str:reference>/', payment_view.verify_payment, name='verify_payment'),
    path('student_courses/<int:user_id>/', views.course_offered_by_student, name='student_courses'),
    path('student_courses/<int:user_id>/<int:course_id>/', views.remove_course_by_user, name="remove_course"),
    path('learning/<str:course_title>/<str:user_email>', views.learning, name='learning'), 
    path('progress/', views.update_progress, name='update_progress'),
    path("socketio/", socketio_info, name="socketio"),
    path("messages/fetch_messages/", message_list, name='fetch_message'),
    path("messages/send_message/", send_message, name="send_message"),
]


