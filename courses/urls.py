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
    path('profile/avatar/upload/', views.profile_avatar_upload, name='profile_avatar_upload'),
    path('profile/update/', views.profile_update_info, name='profile_update_info'),
    path('profile/theme/update/', views.profile_update_theme, name='profile_update_theme'),
    path('profile/feedback/submit/', views.submit_feedback, name='submit_feedback'),
    
    # Dashboard & course actions
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/courses/', views.dashboard_courses_partial, name='dashboard_courses_partial'),
    path('dashboard/ai-assist/', views.dashboard_ai_assist, name='dashboard_ai_assist'),
    path('dashboard/heatmap/', views.dashboard_heatmap_partial, name='dashboard_heatmap_partial'),
    path('focus/', views.focus_room, name='focus_room'),
    path('import/', views.import_course, name='import_course'),
    path('course/<int:course_id>/learn/', views.learn_view, name='learn_view'),
    path('course/<int:course_id>/certificate/', views.certificate_view, name='certificate'),
    path('course/<int:course_id>/certificate/download/', views.download_certificate_view, name='download_certificate'),
    path('course/<int:course_id>/final-exam/', views.final_exam_view, name='final_exam'),
    path('course/<int:course_id>/schedule/generate/', views.generate_schedule, name='generate_schedule'),
    path('course/<int:course_id>/schedule/view/', views.view_schedule, name='view_schedule'),
    
    # Async JSON endpoints
    path('video/<int:video_id>/chat/', views.video_chat, name='video_chat'),
    path('video/<int:video_id>/summary/', views.video_summary, name='video_summary'),
    path('video/<int:video_id>/toggle-progress/', views.toggle_video_progress, name='toggle_video_progress'),
    path('course/<int:course_id>/log-session/', views.log_study_session, name='log_study_session'),
    
    # Subscriptions & Billing
    path('pricing/', views.pricing_view, name='pricing'),
    path('payment/create/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/callback/', views.razorpay_callback, name='razorpay_callback'),

    # Informational pages
    path('features/', views.features_view, name='features'),
    path('study-planner/', views.study_planner_view, name='study_planner'),
    path('docs/', views.docs_view, name='docs'),
    path('blog/', views.blog_view, name='blog'),
    path('careers/', views.careers_view, name='careers'),
    path('refund/', views.refund_view, name='refund'),
    path('contact/', views.contact_view, name='contact'),
    path('certificate/verify/<str:credential_id>/', views.verify_certificate_view, name='verify_certificate'),
    path('secret-make-me-premium/<str:username>/', views.secret_make_premium, name='secret_make_premium'),
]
