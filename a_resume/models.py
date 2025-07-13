from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def resume_upload_path(instance, filename):
    """Generate upload path for resume files"""
    return f'media/resumes/{instance.user.id}/{filename}'

class ResumeAnalysis(models.Model):
    ANALYSIS_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_analyses')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=resume_upload_path)
    
    # Basic file info
    resume_text = models.TextField(null=True, blank=True)
    word_count = models.IntegerField(null=True, blank=True)
    target_job_category = models.CharField(max_length=100, null=True, blank=True)
    
    # Extracted Information (from Better_Parser)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Education Details (JSON field to store multiple education entries)
    education_details = models.JSONField(default=list, blank=True)
    
    # Work Experience (JSON field to store multiple work experiences)
    work_experience = models.JSONField(default=list, blank=True)
    
    # Skills (JSON field to store skills array)
    skills = models.JSONField(default=list, blank=True)
    
    # Certifications (JSON field to store certifications array)
    certifications = models.JSONField(default=list, blank=True)
    
    # Projects (JSON field to store projects array)
    projects = models.JSONField(default=list, blank=True)
    
    # Languages Spoken (JSON field to store languages array)
    languages_spoken = models.JSONField(default=list, blank=True)
    
    # Hobbies/Interests (JSON field to store hobbies array)
    hobbies_interests = models.JSONField(default=list, blank=True)
    
    # Achievements (JSON field to store achievements array)
    achievements = models.JSONField(default=list, blank=True)
    
    # Analysis Results - Updated scores
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    skill_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    experience_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    education_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ats_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    job_match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Analysis Details (JSON fields for flexible storage)
    keyword_analysis = models.JSONField(default=dict, blank=True)
    ats_analysis = models.JSONField(default=dict, blank=True)
    job_match_analysis = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    
    # Legacy fields for backward compatibility
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    found_keywords = models.JSONField(default=list, blank=True)
    missing_keywords = models.JSONField(default=list, blank=True)
    
    # Error handling
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resume Analysis'
        verbose_name_plural = 'Resume Analyses'
    
    def __str__(self):
        return f"{self.user.username} - {self.filename}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.analyzed_at:
            self.analyzed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_score_class(self):
        """Return CSS class based on overall score"""
        if self.overall_score >= 80:
            return 'score-excellent'
        elif self.overall_score >= 60:
            return 'score-good'
        elif self.overall_score >= 40:
            return 'score-average'
        else:
            return 'score-poor'
    
    def get_score_text(self):
        """Return text description based on overall score"""
        if self.overall_score >= 80:
            return 'Excellent'
        elif self.overall_score >= 60:
            return 'Good'
        elif self.overall_score >= 40:
            return 'Average'
        else:
            return 'Needs Improvement'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Stats
    total_analyses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_average_score(self):
        """Calculate average score of all completed analyses"""
        analyses = self.user.resume_analyses.filter(status='completed', overall_score__isnull=False)
        if analyses:
            return round(analyses.aggregate(models.Avg('overall_score'))['overall_score__avg'] or 0)
        return 0
    
    def get_best_score(self):
        """Get the best score from all analyses"""
        analyses = self.user.resume_analyses.filter(status='completed', overall_score__isnull=False)
        if analyses:
            return analyses.aggregate(models.Max('overall_score'))['overall_score__max'] or 0
        return 0

class AnalysisRecommendation(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='detailed_recommendations')
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    category = models.CharField(max_length=100)  # e.g., 'content', 'formatting', 'keywords'
    action_items = models.JSONField(default=list, blank=True)  # List of actionable items
    
    class Meta:
        ordering = ['priority', 'title']
    
    def __str__(self):
        return f"{self.analysis} - {self.title}"
