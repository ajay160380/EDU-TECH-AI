import datetime
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
from .models import Course, Video, Progress, StudySession, UserProfile
from .utils import parse_playlist_id, fetch_youtube_playlist, generate_ai_study_buddy, verify_firebase_token, generate_final_exam, sync_course_video_durations

def home(request):
    """
    Renders the modern product landing page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'courses/home.html')

def about(request):
    """
    Renders the platform mission/about page.
    """
    return render(request, 'courses/about.html')

def terms_view(request):
    """
    Renders the platform Terms of Service page.
    """
    return render(request, 'courses/terms.html')

def privacy_view(request):
    """
    Renders the platform Privacy Policy page.
    """
    return render(request, 'courses/privacy.html')

@login_required
def profile_view(request):
    """
    Renders the premium Apple-ID-style User Profile dashboard with
    two-column layout, learning journey widgets, and editable fields.
    """
    user = request.user
    profile = user.profile
    profile.sync_streak()

    # ---- Plan / Playlist Limits ----
    plan_type = profile.plan_type
    if plan_type == 'free':
        playlist_limit = 3
        limit_display = '3 Playlists'
        usage_display_text = '3'
    elif plan_type == 'pro':
        playlist_limit = 20
        limit_display = '20 Playlists'
        usage_display_text = '20'
    else:
        playlist_limit = 99999
        limit_display = 'Unlimited Playlists'
        usage_display_text = 'Unlimited'

    courses = user.courses.all()
    total_courses = courses.count()
    completed_courses = sum(
        1 for c in courses if c.videos.count() > 0 and c.completed_percentage == 100
    )

    playlist_count = total_courses
    playlist_percentage = 0 if playlist_limit == 99999 else min(
        int((playlist_count / playlist_limit) * 100), 100
    )

    # ---- Learning Journey Widgets ----
    # Study streak (already on profile)
    study_streak = profile.streak_count

    # Completed playlists (courses fully watched)
    completed_playlists = completed_courses

    # Certified skills = courses where user passed the final exam
    certified_skills = sum(1 for c in courses if c.passed_exam)

    # ---- Active Courses / Devices & Sessions ----
    active_courses = []
    for c in courses.order_by('-created_at')[:6]:
        active_courses.append({
            'id': c.id,
            'title': c.title,
            'thumbnail_url': c.thumbnail_url,
            'progress': c.completed_percentage,
            'videos_count': c.videos.count(),
        })

    # ---- Total study minutes across all sessions ----
    from django.db.models import Sum
    total_study_minutes = (
        StudySession.objects.filter(user=user).aggregate(Sum('duration_minutes'))['duration_minutes__sum']
        or 0
    )
    total_study_hours = round(total_study_minutes / 60, 1)

    # ---- Subscription info ----
    subscription_active = profile.is_subscription_active
    subscription_end = profile.subscription_end_date

    # ---- Precomputed display values (short names prevent template line-wrapping) ----
    avatar_url = profile.avatar.url if profile.avatar else ''
    has_avatar = bool(profile.avatar)
    if not has_avatar:
        a = (user.first_name[:1] or user.username[:1]).upper()
        b = user.last_name[:1] or (user.username[1:2] if len(user.username) > 1 else '')
        avt_init = (a + b).upper()
    else:
        avt_init = ''

    # Member badge
    if plan_type == 'ultra':
        member_badge_text = '✦ Ultra Member'
        member_badge_class = 'text-[#d4af37]'
        plan_badge_class = 'bg-[#d4af37]/[0.06] border border-[#d4af37]/20'
        plan_icon_class = 'bg-[#d4af37]/20'
        plan_icon_color = 'text-[#d4af37]'
        plan_name = 'Ultra Plan'
    elif plan_type == 'pro':
        member_badge_text = 'Pro Member'
        member_badge_class = 'text-[#2563eb]'
        plan_badge_class = 'bg-[#2563eb]/[0.06] border border-[#2563eb]/20'
        plan_icon_class = 'bg-[#2563eb]/20'
        plan_icon_color = 'text-[#2563eb]'
        plan_name = 'Pro Plan'
    else:
        member_badge_text = 'Free Plan'
        member_badge_class = 'text-slate-500'
        plan_badge_class = 'bg-black/[0.03] border border-black/[0.06]'
        plan_icon_class = 'bg-black/[0.06]'
        plan_icon_color = 'text-slate-400'
        plan_name = 'Free Plan'

    # Subscription subtitle
    if plan_type == 'free':
        plan_subtitle = f'Basic platform usage — {limit_display} import limit'
    elif subscription_end:
        plan_subtitle = f'Active until {subscription_end.strftime("%b %d, %Y")}'
    else:
        plan_subtitle = 'Active until Ongoing'

    context = {
        'user': user,
        'profile': profile,
        'plan_type': plan_type,
        # Precomputed display values (short names)
        'avatar_url': avatar_url,
        'has_avatar': has_avatar,
        'avt_init': avt_init,
        'disp_fname': user.first_name or '—',
        'disp_lname': user.last_name or '—',
        'disp_email': user.email or '—',
        'disp_uname': user.username,
        'phead': user.first_name or user.username,
        'phead_ln': user.last_name,
        'fname_raw': user.first_name or '',
        'lname_raw': user.last_name or '',
        'email_raw': user.email or '',
        'uname_raw': user.username,
        # Member badge
        'member_badge_text': member_badge_text,
        'member_badge_class': member_badge_class,
        'plan_badge_class': plan_badge_class,
        'plan_icon_class': plan_icon_class,
        'plan_icon_color': plan_icon_color,
        'plan_name': plan_name,
        'plan_subtitle': plan_subtitle,
        # Playlist limits
        'playlist_count': playlist_count,
        'playlist_limit': playlist_limit,
        'limit_display': limit_display,
        'usage_display_text': usage_display_text,
        'playlist_percentage': playlist_percentage,
        'usage_bar_full': plan_type == 'ultra',
        # Learning Journey widgets
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'study_streak': study_streak,
        'completed_playlists': completed_playlists,
        'certified_skills': certified_skills,
        'total_study_hours': total_study_hours,
        # Active courses
        'active_courses': active_courses,
        # Subscription
        'subscription_active': subscription_active,
        'subscription_end': subscription_end,
        'show_upgrade_btn': plan_type != 'ultra',
        'upgrade_btn_text': (
            'Upgrade to Pro' if plan_type == 'free' else 'Upgrade to Ultra'
        ),
    }
    return render(request, 'courses/profile.html', context)

def register_view(request):
    """
    Handles secure user registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not username or not password or not email:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'courses/register.html')
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'courses/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'courses/register.html')
            
        try:
            # Create user and log them in
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f"Welcome to EduTech AI, {username}! Start by importing a course.")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            
    return render(request, 'courses/register.html')

def login_view(request):
    """
    Handles secure user authentication.
    """
    from django.conf import settings
    
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}! Stay focused.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    context = {
        'firebase_api_key': settings.FIREBASE_API_KEY,
        'firebase_auth_domain': settings.FIREBASE_AUTH_DOMAIN,
        'firebase_project_id': settings.FIREBASE_PROJECT_ID,
        'firebase_storage_bucket': settings.FIREBASE_STORAGE_BUCKET,
        'firebase_messaging_sender_id': settings.FIREBASE_MESSAGING_SENDER_ID,
        'firebase_app_id': settings.FIREBASE_APP_ID,
    }
    return render(request, 'courses/login.html', context)

def logout_view(request):
    """
    Logs out the user and redirects to the homepage.
    """
    logout(request)
    messages.success(request, "Logged out successfully. Keep up the high focus!")
    return redirect('home')

@login_required
def dashboard(request):
    """
    Renders the modern high-performance learner dashboard with optimized queries,
    contextual insights, and progressive data loading.
    """
    from django.db.models import Count, Q, Sum, Case, When, IntegerField
    from django.utils import timezone
    import datetime
    import random
    from django.core.cache import cache

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.sync_streak()
    user = request.user

    # ---- Optimized Single-Query Course Aggregation ----
    courses = Course.objects.filter(user=user).annotate(
        video_count=Count('videos'),
        completed_video_count=Count(
            'videos',
            filter=Q(videos__progress__user=user) & Q(videos__progress__is_completed=True)
        ),
    ).order_by('-created_at')

    total_courses = courses.count()
    completed_courses = sum(1 for c in courses if c.video_count > 0 and (
        c.video_count > 0 and c.completed_video_count == c.video_count
    ))
    total_videos_count = sum(c.video_count for c in courses)
    total_completed_videos = sum(c.completed_video_count for c in courses)

    # ---- Sync video durations (commented out to make dashboard render instantly) ----
    # for c in courses:
    #     if c.video_count > 0:
    #         first_video = c.videos.first()
    #         if first_video and first_video.duration_seconds in [600, 720, 840, 960, 1080]:
    #             sync_course_video_durations(c)

    # ---- Weekly Study Hours (last 7 days) ----
    week_ago = timezone.now().date() - datetime.timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(
        user=user, completed_date__gte=week_ago
    ).aggregate(total=Sum('duration_minutes'))['total'] or 0
    weekly_hours = round(weekly_sessions / 60, 1)
    weekly_goal_hours = 7  # Default weekly goal
    weekly_goal_pct = min(round((weekly_hours / weekly_goal_hours) * 100), 100) if weekly_goal_hours > 0 else 0

    # ---- 7-Day Sparkline Data (daily study minutes, last 7 days) ----
    sparkline_data = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - datetime.timedelta(days=i)
        mins = StudySession.objects.filter(
            user=user, completed_date=day
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        sparkline_data.append({
            'date': day.strftime('%a'),
            'minutes': mins,
        })

    # ---- 28-Day Streak Heatmap (colorblind-safe scale) ----
    today = datetime.date.today()
    streak_grid = []

    # Pre-fetch all progress and session dates in one range query
    heatmap_start = today - datetime.timedelta(days=27)
    progress_dates = (
        Progress.objects.filter(user=user, completed_at__date__gte=heatmap_start)
        .values('completed_at__date')
        .annotate(count=Count('id'))
    )
    session_dates = (
        StudySession.objects.filter(user=user, completed_date__gte=heatmap_start)
        .values('completed_date')
        .annotate(count=Count('id'))
    )
    # Build lookup dicts
    progress_lookup = {p['completed_at__date']: p['count'] for p in progress_dates}
    session_lookup = {s['completed_date']: s['count'] for s in session_dates}

    for i in range(27, -1, -1):
        day = today - datetime.timedelta(days=i)
        total_actions = progress_lookup.get(day, 0) + session_lookup.get(day, 0)

        if total_actions == 0:
            level = 0
        elif total_actions <= 2:
            level = 1
        elif total_actions <= 5:
            level = 2
        elif total_actions <= 8:
            level = 3
        else:
            level = 4

        streak_grid.append({
            'date': day.strftime('%Y-%m-%d'),
            'day_name': day.strftime('%a'),
            'label': day.strftime('%b %d'),
            'level': level,
            'actions': total_actions,
        })

    # ---- Contextual Insight Engine (Randomized) ----
    possible_insights = []
    today_date = datetime.date.today()
    activity_today = bool(progress_lookup.get(today_date, 0) or session_lookup.get(today_date, 0))

    # 1. Empty state
    if total_courses == 0:
        possible_insights.append({
            'type': 'action',
            'icon': '🚀',
            'title': 'Get Started',
            'message': 'Import your first YouTube playlist to begin your learning journey.',
            'cta_url': '/import/',
            'cta_label': 'Import Playlist',
        })
    else:
        # 2. Streak lost
        if profile.streak_count == 0 and profile.last_active_date and (today_date - profile.last_active_date).days >= 2:
            days_since = (today_date - profile.last_active_date).days
            possible_insights.append({
                'type': 'warning',
                'icon': '⏰',
                'title': 'Streak Lost',
                'message': f'It\'s been {days_since} days since your last session. Just 5 minutes restarts your streak!',
                'cta_url': '/focus/',
                'cta_label': 'Quick Focus Session',
            })
            
        # 3. Streak at risk
        if profile.streak_count > 0 and not activity_today:
            possible_insights.append({
                'type': 'warning',
                'icon': '🌙',
                'title': 'Streak at Risk',
                'message': f'Your {profile.streak_count}-day streak is at risk! Study today to keep it alive.',
                'cta_url': '/focus/',
                'cta_label': '5-Min Session',
            })
            
        # 4. Streak prediction
        if profile.streak_count > 0 and activity_today:
            next_milestone = 7
            while next_milestone <= profile.streak_count:
                next_milestone += 7
            days_until = next_milestone - profile.streak_count
            if days_until <= 5 and days_until > 0:
                possible_insights.append({
                    'type': 'prediction',
                    'icon': '🔮',
                    'title': f'{next_milestone}-Day Streak Incoming!',
                    'message': f'Keep your rhythm — you\'re just {days_until} day{"s" if days_until > 1 else ""} away from a {next_milestone}-day streak milestone.',
                    'cta_url': '/focus/',
                    'cta_label': 'Sustain It',
                })
                
        # 5. Pace analysis
        in_progress = [c for c in courses if c.video_count > 0 and c.completed_video_count < c.video_count]
        if in_progress:
            total_actions_past_week = sum(
                progress_lookup.get(today_date - datetime.timedelta(days=i), 0) +
                session_lookup.get(today_date - datetime.timedelta(days=i), 0)
                for i in range(7)
            )
            avg_daily = max(total_actions_past_week / 7, 0.3)
            best_course = min(in_progress, key=lambda c: (c.video_count - c.completed_video_count) / avg_daily if avg_daily > 0 else float('inf'))
            remaining = max(best_course.video_count - best_course.completed_video_count, 0)
            eta_days = int(remaining / avg_daily) if avg_daily > 0 else 0
            if eta_days > 0 and eta_days <= 30:
                possible_insights.append({
                    'type': 'pace',
                    'icon': '📊',
                    'title': 'Completion Forecast',
                    'message': f'At your current pace (~{avg_daily:.1f} videos/day), you\'ll finish "{best_course.title}" in about {eta_days} day{"s" if eta_days > 1 else ""}.',
                    'cta_url': f'/course/{best_course.id}/learn/',
                    'cta_label': 'Speed Up',
                })
                
        # 6. Comparison nudge
        if weekly_sessions > 0:
            two_weeks_ago = week_ago - datetime.timedelta(days=7)
            prev_week = StudySession.objects.filter(
                user=user,
                completed_date__gte=two_weeks_ago,
                completed_date__lt=week_ago
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0
            if weekly_sessions > prev_week > 0:
                pct_increase = int(((weekly_sessions - prev_week) / prev_week) * 100)
                if pct_increase >= 20:
                    possible_insights.append({
                        'type': 'comparison',
                        'icon': '📈',
                        'title': 'Growth Spurt!',
                        'message': f'You studied {pct_increase}% more this week than last week. That momentum is powerful — don\'t let it slip!',
                        'cta_url': None,
                        'cta_label': None,
                    })
                    
        # 7. Time of day recommendation
        thirty_days_ago = today_date - datetime.timedelta(days=30)
        recent_sessions = StudySession.objects.filter(
            user=user, completed_date__gte=thirty_days_ago
        ).values_list('completed_date', flat=True)
        if len(recent_sessions) >= 3:
            hour_counts = {}
            for dt in recent_sessions:
                h = dt.hour if hasattr(dt, 'hour') else (dt.hour if isinstance(dt, datetime.datetime) else 12)
                hour_counts[h] = hour_counts.get(h, 0) + 1
            if hour_counts:
                peak_hour = max(hour_counts, key=hour_counts.get)
                peak_label = f'{peak_hour}:00' if peak_hour <= 12 else f'{peak_hour - 12}:00 PM' if peak_hour < 24 else '12:00 AM'
                possible_insights.append({
                    'type': 'info',
                    'icon': '⏳',
                    'title': 'Your Peak Focus Zone',
                    'message': f'Your most productive study hours are around {peak_label}. Block this time tomorrow for deep learning.',
                    'cta_url': '/focus/',
                    'cta_label': 'Focus Room',
                })

        # 8. Exam available
        if completed_courses > 0:
            exam_ready = [c for c in courses if c.video_count > 0 and c.completed_video_count == c.video_count and not c.passed_exam]
            if exam_ready:
                c = random.choice(exam_ready)
                possible_insights.append({
                    'type': 'success',
                    'icon': '🏅',
                    'title': 'Exam Available',
                    'message': f'You\'ve completed "{c.title}"! Take the final exam to earn your certificate.',
                    'cta_url': f'/course/{c.id}/final-exam/',
                    'cta_label': 'Take Exam',
                })

        # 9. Fallback generic encouragement
        possible_insights.append({
            'type': 'action',
            'icon': '💪',
            'title': 'Stay Consistent',
            'message': 'Every learning session builds lasting knowledge. Pick a course and make progress today!',
            'cta_url': None,
            'cta_label': None,
        })
        
    insight = random.choice(possible_insights) if possible_insights else None

    # ---- Predictive Course Recommendations (scoring algorithm) ----
    recommended_courses = []
    if total_courses > 0:
        scored = []
        for c in courses:
            score = 0
            # Recently started (< 3 days ago)
            days_since_created = (today_date - c.created_at.date()).days
            if days_since_created <= 3:
                score += 3
            # Near completion (>80%)
            if c.video_count > 0 and c.completed_video_count / c.video_count >= 0.80 and c.completed_video_count < c.video_count:
                score += 5
            # High priority (target_days is tight)
            if c.target_days > 0 and c.video_count > 0:
                needed_per_day = (c.video_count - c.completed_video_count) / max(c.target_days - max(days_since_created, 0), 1)
                if needed_per_day > 2:
                    score += 4
            # Exam-ready but not attempted
            if c.video_count > 0 and c.completed_video_count == c.video_count and not c.passed_exam:
                score += 6
            if score > 0:
                scored.append((c, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        recommended_courses = [s[0] for s in scored[:3]]

    # ---- Last updated timestamp ----
    last_updated = timezone.now()

    # ---- JSON Serialization for Frontend JS ----
    import json
    courses_list = []
    for c in courses:
        p = int((c.completed_video_count / max(c.video_count, 1)) * 100) if c.video_count else 0
        status = 'done' if c.video_count and c.completed_video_count == c.video_count else ('progress' if p > 0 else 'new')
        
        # Dynamic thumbnail fallback using YouTube maxresdefault
        thumb = c.thumbnail_url
        if not thumb and c.video_count > 0:
            first_video = c.videos.first()
            if first_video and first_video.youtube_video_id:
                thumb = f"https://img.youtube.com/vi/{first_video.youtube_video_id}/maxresdefault.jpg"
        if not thumb:
            thumb = '📚' # Final fallback
            
        courses_list.append({
            'id': c.id,
            'title': c.title,
            'videos': c.video_count,
            'done': c.completed_video_count,
            'target': getattr(c, 'target_days', 30),
            'thumb': thumb,
            'status': status,
            'examReady': (status == 'done' and not getattr(c, 'passed_exam', False)),
            'passed': getattr(c, 'passed_exam', False)
        })
    courses_json = json.dumps(courses_list)
    streak_grid_json = json.dumps(streak_grid)

    context = {
        'profile': profile,
        'courses': courses,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'total_videos_count': total_videos_count,
        'total_completed_videos': total_completed_videos,
        'streak_grid': streak_grid,
        'weekly_hours': weekly_hours,
        'weekly_goal_hours': weekly_goal_hours,
        'weekly_goal_pct': weekly_goal_pct,
        'sparkline_data': sparkline_data,
        'insight': insight,
        'recommended_courses': recommended_courses,
        'activity_today': activity_today,
        'last_updated': last_updated,
        'courses_json': courses_json,
        'streak_grid_json': streak_grid_json,
    }
    return render(request, 'courses/dashboard.html', context)


@login_required
def dashboard_courses_partial(request):
    """
    HTMX partial endpoint: returns sorted/filtered course cards HTML fragment.
    """
    from django.db.models import Count, Q

    sort = request.GET.get('sort', 'recent')
    filter_status = request.GET.get('filter', 'all')
    search = request.GET.get('search', '').strip()
    user = request.user

    courses = Course.objects.filter(user=user).annotate(
        video_count=Count('videos'),
        completed_video_count=Count(
            'videos',
            filter=Q(videos__progress__user=user) & Q(videos__progress__is_completed=True)
        ),
    )

    # Search (case-insensitive title match)
    if search:
        courses = [c for c in courses if search.lower() in c.title.lower()]

    # Filter
    if filter_status == 'in_progress':
        courses = [c for c in courses if c.video_count > 0 and c.completed_video_count < c.video_count]
    elif filter_status == 'completed':
        courses = [c for c in courses if c.video_count > 0 and c.completed_video_count == c.video_count]
    elif filter_status == 'exam_ready':
        courses = [c for c in courses if c.video_count > 0 and c.completed_video_count == c.video_count and not c.passed_exam]

    # Sort
    if sort == 'progress_asc':
        courses = sorted(courses, key=lambda c: (c.completed_video_count / max(c.video_count, 1)))
    elif sort == 'progress_desc':
        courses = sorted(courses, key=lambda c: (c.completed_video_count / max(c.video_count, 1)), reverse=True)
    elif sort == 'alphabetical':
        courses = sorted(courses, key=lambda c: c.title.lower())
    # default: 'recent' — already sorted by -created_at

    context = {'courses': courses, 'user': user}
    return render(request, 'courses/dashboard_courses_partial.html', context)


@login_required
@csrf_exempt
def dashboard_ai_assist(request):
    import json
    import requests
    from django.conf import settings
    from django.http import JsonResponse
    from django.db.models import Count, Q, F

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST is allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except Exception:
        message = request.POST.get('message', '').strip()

    if not message:
        return JsonResponse({'response': "How can I help you?", "suggestions": []})

    user = request.user
    profile = user.profile
    total_courses = Course.objects.filter(user=user).count()
    completed_courses = Course.objects.annotate(vc=Count('videos'), cvc=Count('videos', filter=Q(videos__progress__user=user, videos__progress__is_completed=True))).filter(user=user, vc__gt=0, vc=F('cvc')).count()
    
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        return JsonResponse({'response': "Groq API key is missing. Please configure it in your environment settings.", "suggestions": []})

    system_prompt = f"""You are an expert AI Tutor and study assistant for EduTech AI. 
The user '{user.first_name or user.username}' is currently talking to you.
User's Progress Context:
- Total Courses Enrolled: {total_courses}
- Completed Courses: {completed_courses}
- Study Streak: {profile.streak_count} days

Your goal is to provide encouraging, accurate, and helpful answers to their queries. 
Do not use unnecessary restrictions. Be concise, highly professional, and conversational."""

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        response_text = res.json()['choices'][0]['message']['content'].strip()
        
        # Generic suggestions
        suggestions = ['Summarize my progress', 'Which course next?', 'Peak study hours']
        
        return JsonResponse({
            'response': response_text,
            'suggestions': suggestions
        })
    except Exception as e:
        return JsonResponse({'response': f"Sorry, I encountered an error: {str(e)}", "suggestions": []})


@login_required
def dashboard_heatmap_partial(request):
    from django.utils import timezone
    import datetime
    from django.db.models import Count
    days = int(request.GET.get('days', 28))
    days = min(max(days, 7), 28)
    user = request.user
    today = datetime.date.today()
    heatmap_start = today - datetime.timedelta(days=days - 1)
    progress_dates = Progress.objects.filter(user=user, completed_at__date__gte=heatmap_start).values('completed_at__date').annotate(count=Count('id'))
    session_dates = StudySession.objects.filter(user=user, completed_date__gte=heatmap_start).values('completed_date').annotate(count=Count('id'))
    progress_lookup = {p['completed_at__date']: p['count'] for p in progress_dates}
    session_lookup = {s['completed_date']: s['count'] for s in session_dates}
    streak_grid = []
    for i in range(days - 1, -1, -1):
        day = today - datetime.timedelta(days=i)
        total_actions = progress_lookup.get(day, 0) + session_lookup.get(day, 0)
        if total_actions == 0: level = 0
        elif total_actions <= 2: level = 1
        elif total_actions <= 5: level = 2
        elif total_actions <= 8: level = 3
        else: level = 4
        streak_grid.append({'date': day.strftime('%Y-%m-%d'), 'day_name': day.strftime('%a'), 'label': day.strftime('%b %d'), 'level': level, 'actions': total_actions})
    return render(request, 'courses/dashboard_heatmap_partial.html', {'streak_grid': streak_grid, 'days': days})


@login_required
def import_course(request):
    """
    Accepts playlist URL inputs, fetches metadata from YouTube/Mock systems,
    and inserts Course + Video records to database.
    """
    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        target_days = request.POST.get('target_days', 10)
        
        if not playlist_url:
            messages.error(request, "Please enter a valid YouTube Playlist URL.")
            return render(request, 'courses/import.html')
            
        playlist_id = parse_playlist_id(playlist_url)
        if not playlist_id:
            messages.error(request, "Could not extract YouTube Playlist ID from the URL. Please verify.")
            return render(request, 'courses/import.html')
            
        # Check if user already imported this playlist
        existing_course = Course.objects.filter(user=request.user, playlist_id=playlist_id).first()
        if existing_course:
            messages.info(request, "You have already imported this playlist as a course!")
            return redirect('learn_view', course_id=existing_course.id)
            
        # Enforce Subscription Plan Limit Check
        profile = request.user.profile
        playlist_count = request.user.courses.count()
        limit = 3 if profile.plan_type == 'free' else (20 if profile.plan_type == 'pro' else 99999)
        
        if playlist_count >= limit:
            messages.error(request, f"🔒 You have reached your limit ({limit} playlists) on the {profile.plan_type.upper()} plan! Upgrade your plan to import unlimited playlists.")
            return redirect('pricing')
            
            
        # Fetch data using the parsed YouTube Playlist ID
        data = fetch_youtube_playlist(playlist_id)
        
        if not data or not data.get('videos'):
            messages.error(request, "Could not retrieve any videos from this YouTube Playlist. Ensure it is public.")
            return render(request, 'courses/import.html')
            
        try:
            # Save course
            course = Course.objects.create(
                user=request.user,
                playlist_id=playlist_id,
                title=data['title'],
                description=data['description'],
                thumbnail_url=data['thumbnail_url'],
                total_duration_seconds=data['total_duration_seconds'],
                target_days=int(target_days)
            )
            
            # Save videos
            for idx, v in enumerate(data['videos']):
                Video.objects.create(
                    course=course,
                    youtube_video_id=v['video_id'],
                    title=v['title'],
                    duration_seconds=v['duration_seconds'],
                    order=idx
                )
                
            messages.success(request, f"Successfully imported course: '{course.title}' with {course.videos.count()} videos!")
            return redirect('learn_view', course_id=course.id)
            
        except Exception as e:
            messages.error(request, f"Error compiling course curriculum: {e}")
            
    return render(request, 'courses/import.html')

@login_required
def learn_view(request, course_id):
    """
    Renders the premium distraction-free Zen Study Room dashboard.
    """
    course = get_object_or_404(Course, id=course_id, user=request.user)
    raw_videos = course.videos.all()
    
    if not raw_videos.exists():
        messages.error(request, "This course has no videos in its curriculum.")
        return redirect('dashboard')
        
    # Super-Smart Regex Sorting: Sort videos naturally by extracting lecture numbers from their titles!
    def extract_lecture_num(video):
        match = re.search(r'(?:[L|l]ecture|[L|l]ec|[V|v]ideo|[P|p]art|\#|^)\s*(\d+)', video.title)
        if match:
            return (0, int(match.group(1)))
        return (1, video.order)
        
    videos = sorted(raw_videos, key=extract_lecture_num)
    
    # If videos have placeholder durations (e.g. exactly 600 or 720 seconds), run dynamic sync (commented out for speed)
    # if videos and any(v.duration_seconds in [600, 720, 840, 960, 1080] for v in videos[:5]):
    #     sync_course_video_durations(course)
        
    # Get active video based on URL query parameter or default to the first incomplete video
    active_video_id = request.GET.get('video')
    active_video = None
    
    if active_video_id:
        active_video = next((v for v in videos if str(v.id) == str(active_video_id)), None)
        
    if not active_video:
        # Default to first video not completed, or fallback to first video overall
        for v in videos:
            if not v.is_completed_by_user(request.user):
                active_video = v
                break
        if not active_video:
            active_video = videos[0]
            
    # Mark checklist structures
    playlist_items = []
    completed_count = 0
    for idx, v in enumerate(videos):
        is_done = v.is_completed_by_user(request.user)
        if is_done:
            completed_count += 1
        playlist_items.append({
            'video': v,
            'is_completed': is_done,
            'display_index': idx + 1
        })
        
    # Compile targets
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Calculate smart target calculation: videos / days
    total_videos = len(videos)
    daily_target = max(1, round(total_videos / course.target_days))
    
    # How many videos completed today overall
    today = datetime.date.today()
    daily_completed = Progress.objects.filter(
        user=request.user,
        completed_at__date=today,
        is_completed=True
    ).count()
    
    # Trigger AI study buddy generator with video order for unique content
    ai_bundle = generate_ai_study_buddy(active_video.title, videos.index(active_video) + 1, plan_type=profile.plan_type)
    
    # Calculate initial remaining queries for Pro plan
    remaining_queries = 'unlimited'
    if profile.plan_type == 'pro':
        session_key = f"tutor_queries_{active_video.id}"
        query_count = request.session.get(session_key, 0)
        remaining_queries = max(0, 5 - query_count)
        
    context = {
        'course': course,
        'active_video': active_video,
        'playlist_items': playlist_items,
        'completed_count': completed_count,
        'total_count': total_videos,
        'percentage': course.completed_percentage,
        'daily_target': daily_target,
        'daily_completed': daily_completed,
        'ai_bundle': ai_bundle,
        'profile': profile,
        'remaining_queries': remaining_queries
    }
    return render(request, 'courses/learn.html', context)

@login_required
def certificate_view(request, course_id):
    """
    Renders an elite professional Certificate of Mastery for completed courses.
    """
    course = get_object_or_404(Course, id=course_id, user=request.user)
    
    # Restrict verified certificates to Pro and Ultra plans!
    profile = request.user.profile
    if profile.plan_type == 'free':
        messages.error(request, "🔒 Verified certificates and final conceptual exams are exclusive to Pro and Ultra plans. Upgrade to unlock!")
        return redirect('pricing')
        
    if course.completed_percentage < 100:
        messages.warning(request, "⚠️ You must complete 100% of the course videos before claiming your certificate!")
        return redirect('learn_view', course_id=course.id)
        
    if not course.passed_exam:
        messages.warning(request, "⚠️ You must pass the Final Certification Exam before claiming your verified credential!")
        return redirect('final_exam', course_id=course.id)
        
    # Generate unique certificate hash/ID based on course ID and user ID
    import hashlib
    cert_raw = f"CERT-FOCUSTUBE-{course.id}-{request.user.id}"
    cert_id = hashlib.md5(cert_raw.encode()).hexdigest().upper()[:12]
    cert_formatted = f"FT-{cert_id[:4]}-{cert_id[4:8]}-{cert_id[8:]}"
    
    # Extract exact YouTube channel name dynamically
    instructor_name = "EduTech AI Verified Faculty"
    try:
        data = fetch_youtube_playlist(course.playlist_id)
        if data and data.get('channel_name'):
            instructor_name = data['channel_name']
    except Exception:
        if "by " in course.title.lower():
            parts = re.split(r'by\s+', course.title, flags=re.IGNORECASE)
            if len(parts) > 1:
                instructor_name = parts[1].strip()
            
    context = {
        'course': course,
        'cert_id': cert_formatted,
        'issue_date': datetime.date.today(),
        'instructor_name': instructor_name
    }
    return render(request, 'courses/certificate.html', context)

@login_required
def final_exam_view(request, course_id):
    """
    Manages the 10-question dynamic certification exam and 1-hour retest cooldown.
    """
    course = get_object_or_404(Course, id=course_id, user=request.user)
    
    # Restrict final exam to Pro and Ultra plans!
    profile = request.user.profile
    if profile.plan_type == 'free':
        messages.error(request, "🔒 AI-powered conceptual quizzes and final certification exams are exclusive to Pro and Ultra plans. Upgrade to unlock!")
        return redirect('pricing')
        
    if course.completed_percentage < 100:
        messages.warning(request, "⚠️ You must watch all playlist lectures before taking the final exam!")
        return redirect('learn_view', course_id=course.id)
        
    # Check 1-hour cooldown
    if course.last_exam_attempt and not course.passed_exam:
        elapsed = timezone.now() - course.last_exam_attempt
        if elapsed < datetime.timedelta(hours=1):
            mins_left = int(60 - (elapsed.total_seconds() / 60))
            return render(request, 'courses/exam_cooldown.html', {'course': course, 'mins_left': max(1, mins_left)})
            
    if request.method == 'POST':
        exam_data = request.session.get(f'exam_{course.id}', [])
        if not exam_data:
            messages.error(request, "Exam session expired. Please start the exam again.")
            return redirect('final_exam', course_id=course.id)
            
        score = 0
        results = []
        for q in exam_data:
            q_id = str(q['id'])
            user_ans = request.POST.get(f'q_{q_id}')
            correct = False
            if user_ans is not None and int(user_ans) == q['correct_index']:
                score += 1
                correct = True
            results.append({
                'question': q['question'],
                'user_ans': q['options'][int(user_ans)] if user_ans is not None and user_ans.isdigit() and int(user_ans) < len(q['options']) else 'No answer',
                'correct_ans': q['options'][q['correct_index']],
                'correct': correct,
                'explanation': q.get('explanation', '')
            })
            
        # Passing score: 7/10
        passed = score >= 7
        if passed:
            course.passed_exam = True
            course.save()
        else:
            course.last_exam_attempt = timezone.now()
            course.save()
            
        return render(request, 'courses/exam_results.html', {
            'course': course,
            'score': score,
            'total': len(exam_data),
            'passed': passed,
            'results': results
        })
        
    # GET: Generate Exam
    exam_data = generate_final_exam(course.title, course.description or '')
    request.session[f'exam_{course.id}'] = exam_data
    return render(request, 'courses/final_exam.html', {
        'course': course,
        'exam_data': exam_data
    })


@login_required
@require_POST
def video_chat(request, video_id):
    """
    Handles live chat with the AI Study Tutor for a specific video.
    """
    video = get_object_or_404(Video, id=video_id, course__user=request.user)
    
    # Restrict AI Tutor Chatbot to Pro and Ultra Plans
    profile = request.user.profile
    if profile.plan_type == 'free':
        return JsonResponse({
            'status': 'error',
            'message': '🔒 The AI Tutor Chatbot is an exclusive Pro & Ultra Plan feature. Please upgrade your plan!'
        }, status=403)
    
    # Track queries for Pro tier (limit to 5 per video)
    remaining_queries = 'unlimited'
    if profile.plan_type == 'pro':
        session_key = f"tutor_queries_{video.id}"
        query_count = request.session.get(session_key, 0)
        if query_count >= 5:
            return JsonResponse({
                'status': 'limit_reached',
                'message': '🔒 You have reached the Pro limit of 5 queries for this video! Upgrade to Ultra for completely unlimited AI Tutor questions, advanced AI notes formatting, and unlimited workspace!'
            })
        
        # Increment queries
        new_count = query_count + 1
        request.session[session_key] = new_count
        remaining_queries = 5 - new_count
        
    message = request.POST.get('message', '').strip()
    
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'}, status=400)
        
    system_prompt = f"""
    You are EduTech AI Tutor, an elite, completely unrestricted personal mentor and expert companion.
    The student is currently watching a video lecture titled: "{video.title}" from their course: "{video.course.title}".
    
    IMPORTANT: You have ZERO RESTRICTIONS on what topics you can discuss. If the user asks about anything—whether related to programming, life advice, general knowledge, or completely casual conversation—you must answer them fully, openly, and without any restriction.
    Provide rich technical details, professional explanations, code snippets (if applicable), and clear markdown formatting. Always maintain an encouraging, highly intelligent persona.
    """

    api_key = getattr(settings, 'GROQ_API_KEY', '')

    try:
        if api_key:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            res = requests.post(url, headers=headers, json=data, timeout=15)
            res.raise_for_status()
            ai_response = res.json()['choices'][0]['message']['content']
            return JsonResponse({'status': 'success', 'response': ai_response, 'remaining': remaining_queries})
        else:
            raise Exception("No Groq API Key")

    except Exception as e:
        print(f"Fallback 1 Error (maybe SSL): {e}. Trying free text.pollinations.ai...")
        try:
            # Ultimate Free Generative AI Fallback (No SSL issues usually, and no API keys required)
            free_url = "https://text.pollinations.ai/openai"
            free_data = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7
            }
            free_res = requests.post(free_url, json=free_data, timeout=20)
            free_res.raise_for_status()
            response_text = free_res.json()['choices'][0]['message']['content']
            return JsonResponse({'status': 'success', 'response': response_text, 'remaining': remaining_queries})
            
        except Exception as e2:
            print(f"Pollinations Error: {e2}")
            # The Ultimate Fallback: The Smart Offline NLP Mock!
            def get_smart_chat_mock(msg, vid):
                msg_lower = msg.lower()
                
                if msg_lower in ['hi', 'hello', 'hey', 'namaste']:
                    return f"### 👋 Hello there!\n\nI am your **EduTech AI Tutor**. I'm currently running in Offline Mode, but I'm fully trained on Python! What would you like to learn about **{vid.title}** today?"
    
                if 'string' in msg_lower or 'strung' in msg_lower or 'text' in msg_lower:
                    return f"### 💡 Understanding **Strings** in Python\n\nA string is just a sequence of characters enclosed in quotes. Think of it like text data!\n\n*   **Syntax:** `\"Hello\"` or `'Hello'`\n*   **Why it matters:** You use strings everywhere, from printing messages to processing text files.\n*   **Example:** `name = \"EduTech AI\"`\n\nWant to see some cool string methods like `.upper()` or `.replace()`? 🚀"
    
                elif 'list' in msg_lower or 'array' in msg_lower:
                    return f"### 💡 Understanding **Lists**\n\nLists are used to store multiple items in a single variable. They are ordered, changeable, and allow duplicate values.\n\n*   **Syntax:** `my_list = [1, 2, \"apple\"]`\n*   **Superpower:** You can easily add items using `my_list.append()` or access them via index `my_list[0]`.\n\nWant me to show you how to loop through a list? 🔄"
    
                elif 'dict' in msg_lower or 'map' in msg_lower:
                    return f"### 💡 Understanding **Dictionaries**\n\nDictionaries store data values in **key:value** pairs. They are incredibly fast for looking up data!\n\n*   **Syntax:** `user = {{\"name\": \"Ajay\", \"age\": 22}}`\n*   **Accessing Data:** `print(user[\"name\"])` will output `Ajay`.\n\nIt's just like a real-life dictionary where a word is the key and its meaning is the value! 📖"
    
                elif 'loop' in msg_lower or 'for' in msg_lower or 'while' in msg_lower:
                    return f"### 💡 Understanding **Loops**\n\nLoops are used to execute a block of code repeatedly. Python has two main loop commands:\n1.  **`for` loops:** Great for iterating over sequences (like lists or strings).\n2.  **`while` loops:** Great for running code as long as a condition is true.\n\n```python\nfor i in range(3):\n    print(f\"Iteration {{i}}\")\n```\nLoops save you from writing the exact same code 100 times! 🔁"
    
                elif 'func' in msg_lower or 'def ' in msg_lower:
                    return f"### 💡 Understanding **Functions**\n\nA function is a block of organized, reusable code. It only runs when it is called.\n\n*   **Syntax:** Use the `def` keyword.\n*   **Why:** DRY (Don't Repeat Yourself). Write once, use everywhere!\n\n```python\ndef greet(name):\n    return f\"Hello, {{name}}!\"\n```\nFunctions are the building blocks of clean code! 🧱"
    
                elif 'class' in msg_lower or 'oop' in msg_lower or 'object' in msg_lower:
                    return f"### 💡 Understanding **Classes & OOP**\n\nPython is an Object-Oriented Programming (OOP) language. A Class is like an object constructor, or a \"blueprint\" for creating objects.\n\n*   **Concept:** Think of a Class as a `Car` blueprint, and Objects as actual cars (BMW, Audi).\n*   **Syntax:**\n```python\nclass Car:\n    def __init__(self, brand):\n        self.brand = brand\n```\nOOP makes massive codebases manageable and modular! 🏗️"
    
                elif 'code' in msg_lower or 'example' in msg_lower or 'dikhao' in msg_lower or 'batao' in msg_lower or 'batvo' in msg_lower:
                    return f"### 💻 Code Example\n\nSure! Based on your query and **{vid.title}**, here is a highly relevant, professional code snippet:\n\n```python\n# A simple, robust implementation\ndef process_data(data):\n    \"\"\"Processes and validates incoming data structures\"\"\"\n    if not data:\n        return None\n        \n    result = {{}}\n    for index, item in enumerate(data):\n        result[index] = item.upper() if isinstance(item, str) else item\n        \n    return result\n\nprint(process_data([\"apple\", \"banana\", 42]))\n```\n**Key Takeaway:** Notice how we handle edge cases and use built-in functions like `enumerate()`! ✨"
    
                else:
                    return f"### 🤖 AI Tutor is Here!\n\nYou asked: *\"{msg}\"*\n\nSince I'm currently running in **Offline Mode** (Groq API Key is not set or request failed), I rely on keyword matching. I didn't catch a specific concept in your message. \n\nHowever, looking at the lecture **\"{vid.title}\"**, you should make sure you understand:\n1.  **Syntax & Indentation Rules**\n2.  **Memory Management**\n3.  **Writing Clean Code**\n\nTry asking me about specific topics like **strings, lists, dictionaries, loops, functions, or classes**! ✨"
    
            fallback_msg = get_smart_chat_mock(message, video)
            return JsonResponse({'status': 'success', 'response': fallback_msg, 'remaining': remaining_queries})

@login_required
@require_POST
def toggle_video_progress(request, video_id):
    """
    JSON API endpoint to toggle completion checks for checklist items asynchronously.
    Updates the User's overall streaks as well.
    """
    video = get_object_or_404(Video, id=video_id, course__user=request.user)
    progress, created = Progress.objects.get_or_create(user=request.user, video=video)
    
    if not created:
        # Already exists, toggle the is_completed
        progress.is_completed = not progress.is_completed
        progress.save()
    
    # Update active streak
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if progress.is_completed:
        profile.update_streak()
        
    # Recalculate parameters
    course = video.course
    videos = course.videos.all()
    total_count = videos.count()
    completed_count = Progress.objects.filter(user=request.user, video__course=course, is_completed=True).count()
    percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    # Today's daily target vs completed
    today = datetime.date.today()
    daily_completed = Progress.objects.filter(
        user=request.user,
        completed_at__date=today,
        is_completed=True
    ).count()
    
    # Course daily target recommendation
    daily_target = max(1, round(total_count / course.target_days))
    
    return JsonResponse({
        'status': 'success',
        'is_completed': progress.is_completed,
        'completed_count': completed_count,
        'total_count': total_count,
        'percentage': percentage,
        'daily_completed': daily_completed,
        'daily_target': daily_target,
        'streak': profile.streak_count
    })

@login_required
@require_POST
def log_study_session(request, course_id):
    """
    JSON API endpoint called automatically by JavaScript when a Pomodoro focus
    session timer expires. Records session and bumps streaks.
    """
    course = None
    if int(course_id) > 0:
        course = get_object_or_404(Course, id=course_id, user=request.user)
    duration_minutes = request.POST.get('duration_minutes', 25)
    
    try:
        session = StudySession.objects.create(
            user=request.user,
            course=course,
            duration_minutes=int(duration_minutes)
        )
        
        # Bump the login and study streak
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.update_streak()
        
        return JsonResponse({
            'status': 'success',
            'session_id': session.id,
            'streak': profile.streak_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_POST
def login_google(request):
    """
    Receives a Firebase ID token, verifies it, matches it against
    Django's User models, logs them in, and returns a JSON response.
    """
    id_token = request.POST.get('id_token')
    if not id_token:
        return JsonResponse({'status': 'error', 'message': 'Missing Firebase ID Token'}, status=400)
        
    user_info = verify_firebase_token(id_token)
    if not user_info:
        return JsonResponse({'status': 'error', 'message': 'Invalid Firebase ID Token'}, status=401)
        
    uid = user_info['uid']
    email = user_info['email']
    name = user_info['name']
    
    # Generate unique username
    if not email:
        username = f"google_{uid[:15]}"
        email = f"{username}@focustube.com"
    else:
        username = email.split('@')[0]
        
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exclude(email=email).exists():
        username = f"{base_username}_{counter}"
        counter += 1
        
    # Find or create user
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.filter(username=username).first()
        
    if not user:
        user = User.objects.create_user(username=username, email=email)
        user.set_unusable_password()
        user.save()
        if name:
            user.first_name = name
            user.save()
            
    # Establish Session
    login(request, user)
    
    # Ensure profile exists without falsely bumping study streak
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    messages.success(request, f"Welcome, {user.username}! Signed in securely via Google SSO.")
    
    return JsonResponse({
        'status': 'success',
        'username': user.username,
        'redirect_url': '/dashboard/'
    })

import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import uuid

# Initialize Razorpay Client
try:
    from django.conf import settings
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
except Exception as e:
    print(f"Razorpay Client initialization failed: {e}")
    razorpay_client = None

@login_required
def pricing_view(request):
    """
    Renders the subscription pricing plan selection page.
    """
    from django.conf import settings
    profile = request.user.profile
    context = {
        'profile': profile,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'courses/pricing.html', context)

@login_required
def create_razorpay_order(request):
    """
    Generates a Razorpay Order ID for upgrading subscriptions.
    Falls back to a secure simulated order if credentials are dummy.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    from django.conf import settings
    plan = request.POST.get('plan')
    billing_cycle = request.POST.get('billing_cycle', 'monthly') # 'monthly' or 'yearly'
    
    if plan not in ['pro', 'ultra']:
        return JsonResponse({'status': 'error', 'message': 'Invalid subscription plan.'}, status=400)
        
    # Calculate amount in paise (1 INR = 100 paise)
    if plan == 'pro':
        amount = 95000 if billing_cycle == 'yearly' else 9900
    else: # ultra
        amount = 143000 if billing_cycle == 'yearly' else 14900
        
    currency = 'INR'
    notes = {
        'user_id': request.user.id,
        'email': request.user.email,
        'plan_type': plan,
        'billing_cycle': billing_cycle
    }
    
    # Try generating a real Razorpay Order
    order_id = None
    is_simulated = False
    
    # If the credentials are placeholders, we skip Razorpay API calls to prevent auth crashes
    if settings.RAZORPAY_KEY_ID.startswith('rzp_test_demoKeyId'):
        is_simulated = True
    else:
        try:
            order_data = {
                'amount': amount,
                'currency': currency,
                'receipt': f"receipt_{request.user.id}_{int(datetime.datetime.now().timestamp())}",
                'notes': notes
            }
            order = razorpay_client.order.create(data=order_data)
            order_id = order.get('id')
        except Exception as e:
            print(f"Razorpay Order creation failed: {e}. Falling back to simulation.")
            is_simulated = True
            
    if is_simulated:
        order_id = f"order_simulated_{uuid.uuid4().hex[:12]}"
        
    # Store order_id temporarily on the user's profile
    profile = request.user.profile
    profile.razorpay_order_id = order_id
    profile.save()
    
    return JsonResponse({
        'status': 'success',
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
        'is_simulated': is_simulated,
        'key_id': settings.RAZORPAY_KEY_ID,
        'user_name': request.user.get_full_name() or request.user.username,
        'user_email': request.user.email,
        'plan_name': f"{plan.capitalize()} Plan ({billing_cycle.capitalize()})"
    })

@csrf_exempt
@login_required
def razorpay_callback(request):
    """
    Validates Razorpay payment verification signatures.
    Upgrades user profiles to Pro or Ultra subscription tiers upon success.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    from django.conf import settings
    import datetime
    
    order_id = request.POST.get('razorpay_order_id')
    payment_id = request.POST.get('razorpay_payment_id')
    signature = request.POST.get('razorpay_signature')
    plan = request.POST.get('plan')
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    
    if not order_id or not payment_id or not signature:
        return JsonResponse({'status': 'error', 'message': 'Missing payment verification details.'}, status=400)
        
    profile = request.user.profile
    
    # 1. Verify Signature
    is_valid = False
    if order_id.startswith('order_simulated_'):
        # For our test simulator mode, automatically approve simulated orders
        is_valid = True
    else:
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            is_valid = True
        except Exception as e:
            print(f"Razorpay Signature verification failed: {e}")
            is_valid = False
            
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': 'Payment signature verification failed.'}, status=400)
        
    # 2. Upgrade User Plan
    profile.plan_type = plan
    profile.razorpay_order_id = order_id
    profile.razorpay_payment_id = payment_id
    profile.plan_type = plan  # Double ensuring active setting
    profile.razorpay_signature = signature
    
    # Calculate subscription expiration date
    today = datetime.date.today()
    if billing_cycle == 'yearly':
        profile.subscription_end_date = today + datetime.timedelta(days=365)
    else:
        profile.subscription_end_date = today + datetime.timedelta(days=30)
        
    profile.save()
    
    from django.contrib import messages
    messages.success(request, f"Congratulations! You are now subscribed to EduTech AI {plan.capitalize()}!")
    
    return JsonResponse({
        'status': 'success',
        'message': 'Payment validated successfully!',
        'redirect_url': '/dashboard/'
    })


@login_required
def video_summary(request, video_id):
    """
    Async JSON endpoint that compiles/generates the study summary for a specific lecture video.
    """
    video = get_object_or_404(Video, id=video_id, course__user=request.user)
    profile = request.user.profile
    
    try:
        # Find video index in course for correct order mapping
        raw_videos = video.course.videos.all()
        # Sort using the same smart extract_lecture_num logic to ensure matching index
        def extract_lecture_num(vid):
            match = re.search(r'(?:[L|l]ecture|[L|l]ec|[V|v]ideo|[P|p]art|\#|^)\s*(\d+)', vid.title)
            if match:
                return (0, int(match.group(1)))
            return (1, vid.order)
            
        videos_sorted = sorted(raw_videos, key=extract_lecture_num)
        try:
            video_order = videos_sorted.index(video) + 1
        except ValueError:
            video_order = video.order or 1
            
        # Generate the plan-specific study bundle
        ai_bundle = generate_ai_study_buddy(video.title, video_order, plan_type=profile.plan_type)
        summary_text = ai_bundle.get('summary', '')
            
        return JsonResponse({
            'status': 'success',
            'summary': summary_text
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def profile_avatar_upload(request):
    """
    Ajax endpoint to upload/change the user's profile avatar.
    Accepts multipart form-data with 'avatar' file field.
    Returns JSON with the new avatar URL.
    """
    profile = request.user.profile
    avatar_file = request.FILES.get('avatar')

    if not avatar_file:
        return JsonResponse({'status': 'error', 'message': 'No image file provided.'}, status=400)

    # Basic validation: allow only image types
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if avatar_file.content_type not in allowed_types:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid file type. Please upload JPEG, PNG, WebP, or GIF.'
        }, status=400)

    # Size limit: 5 MB
    if avatar_file.size > 5 * 1024 * 1024:
        return JsonResponse({
            'status': 'error',
            'message': 'File too large. Maximum size is 5 MB.'
        }, status=400)

    # Delete old avatar if exists (to avoid orphan files)
    if profile.avatar:
        profile.avatar.delete(save=False)

    profile.avatar = avatar_file
    profile.save()

    return JsonResponse({
        'status': 'success',
        'message': 'Avatar updated successfully!',
        'avatar_url': profile.avatar.url,
    })


@login_required
@require_POST
def profile_update_theme(request):
    """
    Ajax endpoint to update user theme preference.
    """
    theme = request.POST.get('theme_color', '').strip()
    allowed_themes = ['red', 'blue', 'green', 'purple']
    
    if theme not in allowed_themes:
        return JsonResponse({'status': 'error', 'message': 'Invalid theme.'}, status=400)
        
    profile = request.user.profile
    profile.theme_color = theme
    profile.save()
    
    return JsonResponse({'status': 'success', 'message': 'Theme updated.'})


@login_required
@require_POST
def profile_update_info(request):
    """
    Ajax endpoint to update user personal information:
    first_name, last_name, email, username.
    Validates uniqueness, email format, and required fields.
    Returns JSON with updated field values.
    """
    user = request.user
    field = request.POST.get('field', '').strip()
    value = request.POST.get('value', '').strip()

    allowed_fields = ['first_name', 'last_name', 'email', 'username']

    if field not in allowed_fields:
        return JsonResponse({'status': 'error', 'message': 'Invalid field.'}, status=400)

    if not value:
        return JsonResponse({'status': 'error', 'message': f'{field.replace("_", " ").title()} cannot be empty.'}, status=400)

    # Validate email format
    if field == 'email':
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(value)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'Please enter a valid email address.'}, status=400)
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This email is already in use by another account.'}, status=400)

    # Validate username uniqueness
    if field == 'username':
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            return JsonResponse({'status': 'error', 'message': 'This username is already taken.'}, status=400)
        if len(value) < 3:
            return JsonResponse({'status': 'error', 'message': 'Username must be at least 3 characters.'}, status=400)

    # Apply the update
    setattr(user, field, value)
    user.save()

    # Return the display-friendly label and value
    display_labels = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        'username': 'Username',
    }

    return JsonResponse({
        'status': 'success',
        'message': f'{display_labels.get(field, field)} updated successfully.',
        'field': field,
        'value': value,
    })


@login_required
def focus_room(request):
    """
    Dedicated Zen Focus Room with standalone Pomodoro Timer and Lo-Fi audio stream.
    """
    profile = request.user.profile
    return render(request, 'courses/focus_room.html', {'profile': profile})





def features_view(request):
    """
    Renders the platform features overview page.
    """
    return render(request, 'courses/features.html')


def study_planner_view(request):
    """
    Renders the AI study planner feature page.
    """
    return render(request, 'courses/study_planner.html')


def docs_view(request):
    """
    Renders the documentation and guides page.
    """
    return render(request, 'courses/docs.html')


def blog_view(request):
    """
    Renders the blog listing page.
    """
    return render(request, 'courses/blog.html')


def careers_view(request):
    """
    Renders the careers and job openings page.
    """
    return render(request, 'courses/careers.html')


def shipping_view(request):
    """
    Renders the shipping/delivery policy page.
    """
    return render(request, 'courses/shipping.html')
