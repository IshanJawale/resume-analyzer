from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path("", views.home, name="home"),
    # Authentication
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    # Dashboard and main features
    path("dashboard/", views.dashboard, name="dashboard"),
    path("upload/", views.upload_resume, name="upload_resume"),
    # Analysis
    path(
        "analysis/<int:analysis_id>/", views.analysis_results, name="analysis_results"
    ),
    path(
        "analysis/<int:analysis_id>/detail/",
        views.analysis_detail,
        name="analysis_detail",
    ),
    path(
        "analysis/<int:analysis_id>/delete/",
        views.delete_analysis,
        name="delete_analysis",
    ),
    path("history/", views.analysis_history, name="analysis_history"),
    # User profile
    path("profile/", views.profile, name="profile"),
]
