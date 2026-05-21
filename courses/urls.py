from django.urls import path
from . import views

urlpatterns = [
    # Static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    
    # User accounts
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('login/google/', views.login_google, name='login_google'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Dashboard & course actions
    path('dashboard/', views.dashboard, name='dashboard'),
    path('focus/', views.focus_room, name='focus_room'),
    path('import/', views.import_course, name='import_course'),
    path('course/<int:course_id>/learn/', views.learn_view, name='learn_view'),
    path('course/<int:course_id>/certificate/', views.certificate_view, name='certificate'),
    path('course/<int:course_id>/final-exam/', views.final_exam_view, name='final_exam'),
    
    # Async JSON endpoints
    path('video/<int:video_id>/chat/', views.video_chat, name='video_chat'),
    path('video/<int:video_id>/summary/', views.video_summary, name='video_summary'),
    path('video/<int:video_id>/toggle-progress/', views.toggle_video_progress, name='toggle_video_progress'),
    path('course/<int:course_id>/log-session/', views.log_study_session, name='log_study_session'),
    
    # Subscriptions & Billing
    path('pricing/', views.pricing_view, name='pricing'),
    path('payment/create/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/callback/', views.razorpay_callback, name='razorpay_callback'),
]
