from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import os

def avatar_upload_path(instance, filename):
    """Upload avatar to profile_pics/USERNAME/ directory with timestamp to bust cache."""
    ext = os.path.splitext(filename)[1].lower()
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return f'profile_pics/{instance.user.username}/avatar_{ts}{ext}'

class UserProfile(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('ultra', 'Ultra'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    daily_target_videos = models.IntegerField(default=2)
    streak_count = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    theme_color = models.CharField(max_length=20, default='red')
    
    # Subscription fields
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    subscription_end_date = models.DateField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_plan_type_display()})"

    @property
    def is_pro(self):
        if self.plan_type in ['pro', 'ultra']:
            return self.is_subscription_active
        return False

    @property
    def is_ultra(self):
        if self.plan_type == 'ultra':
            return self.is_subscription_active
        return False

    @property
    def is_subscription_active(self):
        if self.plan_type == 'free':
            return True
        if self.subscription_end_date:
            return self.subscription_end_date >= datetime.date.today()
        return True

    def update_streak(self):
        """
        Updates the study streak based on activity date.
        Should be called whenever a video is marked completed or a Pomodoro session completes.
        """
        today = datetime.date.today()
        if self.last_active_date is None:
            self.streak_count = 1
            self.last_active_date = today
        elif self.last_active_date == today:
            # Already active today, streak remains unchanged
            pass
        elif self.last_active_date == today - datetime.timedelta(days=1):
            # Active yesterday, increment streak
            self.streak_count += 1
            self.last_active_date = today
        else:
            # Broke streak
            self.streak_count = 1
            self.last_active_date = today
        self.save()

    def sync_streak(self):
        """
        Calculates the true consecutive day streak by inspecting actual study events (Progress and StudySession).
        """
        today = datetime.date.today()
        current_streak = 0
        check_date = today
        
        # First check if there's any activity today
        has_activity_today = (
            Progress.objects.filter(user=self.user, completed_at__date=today, is_completed=True).exists() or
            StudySession.objects.filter(user=self.user, completed_date=today).exists()
        )
        
        if has_activity_today:
            current_streak = 1
            check_date = today - datetime.timedelta(days=1)
        else:
            # Check if there was activity yesterday (if not, streak is 0)
            yesterday = today - datetime.timedelta(days=1)
            has_activity_yesterday = (
                Progress.objects.filter(user=self.user, completed_at__date=yesterday, is_completed=True).exists() or
                StudySession.objects.filter(user=self.user, completed_date=yesterday).exists()
            )
            if has_activity_yesterday:
                current_streak = 1
                check_date = yesterday - datetime.timedelta(days=1)
            else:
                self.streak_count = 0
                self.save()
                return 0
                
        # Now count backwards for consecutive days
        while True:
            active_on_day = (
                Progress.objects.filter(user=self.user, completed_at__date=check_date, is_completed=True).exists() or
                StudySession.objects.filter(user=self.user, completed_date=check_date).exists()
            )
            if active_on_day:
                current_streak += 1
                check_date -= datetime.timedelta(days=1)
            else:
                break
                
        if self.streak_count != current_streak:
            self.streak_count = current_streak
            self.save()
            
        return current_streak

class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    playlist_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    total_duration_seconds = models.IntegerField(default=0)
    target_days = models.IntegerField(default=10) # Deadline in days to calculate target
    passed_exam = models.BooleanField(default=False)
    last_exam_attempt = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_duration_display(self):
        hours = self.total_duration_seconds // 3600
        minutes = (self.total_duration_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @property
    def completed_percentage(self):
        total_videos = self.videos.count()
        if total_videos == 0:
            return 0
        completed_videos = Progress.objects.filter(
            user=self.user, 
            video__course=self, 
            is_completed=True
        ).count()
        return int((completed_videos / total_videos) * 100)

    @property
    def daily_target_videos(self):
        total_videos = self.videos.count()
        if self.target_days and self.target_days > 0:
            return max(1, round(total_videos / self.target_days))
        return 1

    @property
    def daily_completed_today(self):
        today = datetime.date.today()
        return Progress.objects.filter(
            user=self.user,
            video__course=self,
            completed_at__date=today,
            is_completed=True
        ).count()

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    youtube_video_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def is_completed_by_user(self, user):
        return Progress.objects.filter(user=user, video=self, is_completed=True).exists()

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} completed {self.video.title}"

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_sessions', null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    completed_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.duration_minutes} mins on {self.completed_date}"

# Signal handlers to ensure UserProfile is automatically kept in sync
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        if instance.username == 'aryamaddy_1':
            profile.plan_type = 'ultra'
            profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        profile = UserProfile.objects.create(user=instance)
    else:
        profile = instance.profile
        
    if instance.username == 'aryamaddy_1' and profile.plan_type != 'ultra':
        profile.plan_type = 'ultra'
        
    profile.save()
