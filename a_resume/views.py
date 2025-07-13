from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Max, Count
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import sys
import tempfile
import requests
from .models import ResumeAnalysis, UserProfile, AnalysisRecommendation
from .forms import ResumeUploadForm, UserProfileForm, CustomUserCreationForm

# Add Analyze directory to Python path for compatibility
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Analyze'))

try:
    from Analyze.new_analysis_service import NewResumeAnalysisService
    analysis_service = NewResumeAnalysisService()
except ImportError as e:
    print(f"Import error: {e}")
    analysis_service = None

def home(request):
    """Homepage view"""
    return render(request, 'a_resume/home.html')

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'a_resume/login.html', {'form': form})

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'a_resume/register.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard view"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user statistics
    total_analyses = ResumeAnalysis.objects.filter(user=request.user).count()
    completed_analyses = ResumeAnalysis.objects.filter(user=request.user, status='completed')
    
    avg_score = 0
    best_score = 0
    total_suggestions = 0
    
    if completed_analyses.exists():
        scores = completed_analyses.values_list('overall_score', flat=True)
        avg_score = round(sum(scores) / len(scores))
        best_score = max(scores)
        total_suggestions = sum(len(analysis.recommendations) for analysis in completed_analyses)
    
    # Get recent analyses
    recent_analyses = ResumeAnalysis.objects.filter(user=request.user)[:5]
    
    context = {
        'total_resumes': total_analyses,
        'avg_score': avg_score,
        'best_score': best_score,
        'total_suggestions': total_suggestions,
        'recent_analyses': recent_analyses,
    }
    
    return render(request, 'a_resume/dashboard.html', context)

@login_required
def upload_resume(request):
    """Handle resume upload"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_analysis = form.save(commit=False)
            resume_analysis.user = request.user
            resume_analysis.filename = request.FILES['file'].name
            resume_analysis.save()
            
            # Perform AI analysis
            try:
                perform_ai_analysis(resume_analysis)
                messages.success(request, 'Resume uploaded and analyzed successfully!')
            except Exception as e:
                messages.error(request, f'Resume uploaded but analysis failed: {str(e)}')
            
            return redirect('analysis_results', analysis_id=resume_analysis.id)
        else:
            messages.error(request, 'Please correct the errors below.')
            return redirect('dashboard')
    else:
        return redirect('dashboard')

@login_required
def analysis_results(request, analysis_id):
    """Display analysis results"""
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)
    
    # If analysis is still processing, show loading page
    if analysis.status in ['pending', 'processing']:
        return render(request, 'a_resume/analysis_processing.html', {'analysis': analysis})
    
    # Format the data for template compatibility
    formatted_analysis = analysis
    
    # Ensure summary has the expected field names for template
    if analysis.summary:
        summary = analysis.summary.copy() if analysis.summary else {}
        if 'rating' in summary and 'overall_rating' not in summary:
            summary['overall_rating'] = summary['rating']
        if 'description' in summary and 'rating_description' not in summary:
            summary['rating_description'] = summary['description']
        formatted_analysis.summary = summary
    
    # Format work experience for template compatibility
    if analysis.work_experience:
        formatted_experience = []
        for exp in analysis.work_experience:
            if isinstance(exp, dict):
                formatted_exp = {}
                # Map Groq API field names to template field names
                formatted_exp['job_title'] = exp.get('Job Title', exp.get('job_title', ''))
                formatted_exp['company'] = exp.get('Company', exp.get('company', ''))
                formatted_exp['duration'] = exp.get('Duration', exp.get('duration', ''))
                formatted_exp['description'] = exp.get('Description', exp.get('description', ''))
                formatted_experience.append(formatted_exp)
            else:
                formatted_experience.append(exp)
        formatted_analysis.work_experience = formatted_experience
    
    # Format education for template compatibility
    if analysis.education_details:
        formatted_education = []
        for edu in analysis.education_details:
            if isinstance(edu, dict):
                formatted_edu = {}
                formatted_edu['degree'] = edu.get('Degree', edu.get('degree', ''))
                formatted_edu['institution'] = edu.get('Institution', edu.get('institution', ''))
                formatted_edu['year'] = edu.get('Year', edu.get('year', ''))
                formatted_education.append(formatted_edu)
            else:
                formatted_education.append(edu)
        formatted_analysis.education_details = formatted_education
    
    # Format skills for template compatibility
    if analysis.skills:
        import json
        import ast
        
        skills_data = analysis.skills
        formatted_skills = []
        
        # Handle different skill data formats
        if isinstance(skills_data, str):
            try:
                # Try JSON parsing first
                parsed_skills = json.loads(skills_data.replace("'", '"'))
                if isinstance(parsed_skills, dict):
                    # Flatten dictionary into list
                    for category, skill_list in parsed_skills.items():
                        if isinstance(skill_list, list):
                            for skill_item in skill_list:
                                if isinstance(skill_item, str):
                                    formatted_skills.append(skill_item)
                                elif isinstance(skill_item, dict):
                                    skill_name = skill_item.get('name', skill_item.get('skill', str(skill_item)))
                                    if skill_name:
                                        formatted_skills.append(skill_name)
                        elif isinstance(skill_list, str):
                            formatted_skills.append(skill_list)
                        elif isinstance(skill_list, dict):
                            skill_name = skill_list.get('name', skill_list.get('skill', str(skill_list)))
                            if skill_name:
                                formatted_skills.append(skill_name)
                elif isinstance(parsed_skills, list):
                    formatted_skills = parsed_skills
                else:
                    formatted_skills = [skills_data]
            except (json.JSONDecodeError, ValueError):
                try:
                    # Try literal_eval for Python-style dict strings
                    parsed_skills = ast.literal_eval(skills_data)
                    if isinstance(parsed_skills, dict):
                        for category, skill_list in parsed_skills.items():
                            if isinstance(skill_list, list):
                                for skill_item in skill_list:
                                    if isinstance(skill_item, str):
                                        formatted_skills.append(skill_item)
                                    elif isinstance(skill_item, dict):
                                        skill_name = skill_item.get('name', skill_item.get('skill', str(skill_item)))
                                        if skill_name:
                                            formatted_skills.append(skill_name)
                            elif isinstance(skill_list, str):
                                formatted_skills.append(skill_list)
                            elif isinstance(skill_list, dict):
                                skill_name = skill_list.get('name', skill_list.get('skill', str(skill_list)))
                                if skill_name:
                                    formatted_skills.append(skill_name)
                    elif isinstance(parsed_skills, list):
                        formatted_skills = parsed_skills
                    else:
                        formatted_skills = [skills_data]
                except (ValueError, SyntaxError):
                    # If all parsing fails, treat as single skill
                    formatted_skills = [skills_data]
        elif isinstance(skills_data, dict):
            # Flatten dictionary into list
            for category, skill_list in skills_data.items():
                if isinstance(skill_list, list):
                    for skill_item in skill_list:
                        if isinstance(skill_item, str):
                            formatted_skills.append(skill_item)
                        elif isinstance(skill_item, dict):
                            # Handle nested dict skills
                            skill_name = skill_item.get('name', skill_item.get('skill', str(skill_item)))
                            if skill_name:
                                formatted_skills.append(skill_name)
                elif isinstance(skill_list, str):
                    formatted_skills.append(skill_list)
                elif isinstance(skill_list, dict):
                    # Handle dict as skill
                    skill_name = skill_list.get('name', skill_list.get('skill', str(skill_list)))
                    if skill_name:
                        formatted_skills.append(skill_name)
        elif isinstance(skills_data, list):
            # Handle list of skills or list containing dict
            for item in skills_data:
                if isinstance(item, str):
                    formatted_skills.append(item)
                elif isinstance(item, dict):
                    # Flatten dictionary into list
                    for category, skill_list in item.items():
                        if isinstance(skill_list, list):
                            for skill_item in skill_list:
                                if isinstance(skill_item, str):
                                    formatted_skills.append(skill_item)
                                elif isinstance(skill_item, dict):
                                    skill_name = skill_item.get('name', skill_item.get('skill', str(skill_item)))
                                    if skill_name:
                                        formatted_skills.append(skill_name)
                        elif isinstance(skill_list, str):
                            formatted_skills.append(skill_list)
                        elif isinstance(skill_list, dict):
                            skill_name = skill_list.get('name', skill_list.get('skill', str(skill_list)))
                            if skill_name:
                                formatted_skills.append(skill_name)
        else:
            formatted_skills = []
        
        # Remove duplicates while preserving order and handle any remaining dict objects
        seen = set()
        unique_skills = []
        for skill in formatted_skills:
            # Convert any remaining dict objects to strings or extract meaningful values
            if isinstance(skill, dict):
                # Try to get a meaningful string from dict
                skill_str = skill.get('name', skill.get('skill', str(skill)))
                if skill_str and isinstance(skill_str, str) and skill_str not in seen:
                    seen.add(skill_str)
                    unique_skills.append(skill_str)
            elif skill and isinstance(skill, str) and skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        formatted_analysis.skills = unique_skills
    
    # Format projects for template compatibility
    if analysis.projects:
        formatted_projects = []
        for proj in analysis.projects:
            if isinstance(proj, dict):
                formatted_proj = {}
                formatted_proj['name'] = proj.get('Project Name', proj.get('name', ''))
                formatted_proj['description'] = proj.get('Description', proj.get('description', ''))
                formatted_proj['duration'] = proj.get('Duration', proj.get('duration', ''))
                formatted_proj['technologies'] = proj.get('Technologies', proj.get('technologies', []))
                formatted_projects.append(formatted_proj)
            else:
                formatted_projects.append(proj)
        formatted_analysis.projects = formatted_projects
    
    context = {
        'analysis': formatted_analysis,
        'overall_score': analysis.overall_score,
        'summary': formatted_analysis.summary,
    }
    
    return render(request, 'a_resume/new_analysis_results.html', context)

@login_required
def analysis_history(request):
    """Display user's analysis history"""
    analyses = ResumeAnalysis.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        analyses = analyses.filter(filename__icontains=search_query)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        analyses = analyses.order_by('created_at')
    elif sort_by == 'highest':
        analyses = analyses.order_by('-overall_score')
    elif sort_by == 'lowest':
        analyses = analyses.order_by('overall_score')
    else:  # newest
        analyses = analyses.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(analyses, 8)  # Show 8 analyses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'a_resume/analysis_history.html', context)

@login_required
def analysis_detail(request, analysis_id):
    """Redirect to analysis results - this is for backward compatibility"""
    return redirect('analysis_results', analysis_id=analysis_id)

@login_required
def profile(request):
    """User profile view"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            
            # Update user info
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    # Get user statistics
    total_analyses = ResumeAnalysis.objects.filter(user=request.user).count()
    avg_score = user_profile.get_average_score()
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'total_analyses': total_analyses,
        'avg_score': avg_score,
    }
    
    return render(request, 'a_resume/profile.html', context)

@login_required
def delete_analysis(request, analysis_id):
    """Delete an analysis"""
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, user=request.user)
    
    if request.method == 'POST':
        # Delete the file from Cloudinary storage
        if analysis.file:
            try:
                # For Cloudinary storage, use the storage backend's delete method
                analysis.file.storage.delete(analysis.file.name)
                print(f"Successfully deleted file from Cloudinary: {analysis.file.name}")
            except Exception as delete_error:
                print(f"Warning: Could not delete file from Cloudinary: {delete_error}")
                # Continue with analysis deletion even if file deletion fails
        
        analysis.delete()
        messages.success(request, 'Analysis deleted successfully!')
        return redirect('analysis_history')
    
    return render(request, 'a_resume/confirm_delete.html', {'analysis': analysis})

# Utility Functions
# The analyze_resume function has been replaced with perform_ai_analysis

def perform_ai_analysis(resume_analysis):
    """Perform AI analysis on uploaded resume using new Groq-based service"""
    if not analysis_service:
        # Fallback to mock analysis if service is not available
        perform_mock_analysis(resume_analysis)
        return

    try:
        import tempfile
        
        # For Cloudinary storage, use Django's storage backend read method
        try:
            print(f"Reading file using Django storage: {resume_analysis.file.name}")
            
            # Open the file using Django storage backend
            with resume_analysis.file.open('rb') as cloudinary_file:
                file_content = cloudinary_file.read()
            
            print(f"✅ Successfully read {len(file_content)} bytes from Cloudinary")
            
            # Create temporary file with same extension
            file_extension = os.path.splitext(resume_analysis.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
                print(f"Saved to temporary file: {temp_file_path}")
                
        except Exception as storage_error:
            print(f"Django storage read failed: {storage_error}")
            # If that fails, there might be a fundamental issue with the storage configuration
            raise Exception(f"Could not read file from Cloudinary storage: {storage_error}")
        
        try:
            # Use the new analysis service with temporary file
            result = analysis_service.extract_and_analyze_resume(temp_file_path)
            
            if not result['success']:
                raise Exception(f"Analysis failed: {result.get('error', 'Unknown error')}")
            
            # Update resume analysis with extracted data
            resume_analysis.status = 'completed'
            resume_analysis.resume_text = result['resume_text']
            resume_analysis.word_count = result['word_count']
            
            # Store extracted structured data with safe defaults
            extracted_data = result['extracted_data']
            resume_analysis.full_name = extracted_data.get('full_name', '') or ''
            resume_analysis.email_address = extracted_data.get('email_address', '') or ''
            resume_analysis.phone_number = extracted_data.get('phone_number', '') or ''
            
            # Ensure all JSON fields are lists, never None
            resume_analysis.education_details = extracted_data.get('education_details') or []
            resume_analysis.work_experience = extracted_data.get('work_experience') or []
            
            # Handle skills - if it's a dict, flatten it to a list
            skills_data = extracted_data.get('skills') or []
            if isinstance(skills_data, dict):
                # Flatten skills dictionary into a single list
                flattened_skills = []
                for category, skill_list in skills_data.items():
                    if isinstance(skill_list, list):
                        flattened_skills.extend(skill_list)
                    elif isinstance(skill_list, str):
                        flattened_skills.append(skill_list)
                resume_analysis.skills = flattened_skills
            elif isinstance(skills_data, str):
                # If it's a string representation of a dict, try to parse it
                try:
                    import ast
                    parsed_skills = ast.literal_eval(skills_data)
                    if isinstance(parsed_skills, dict):
                        flattened_skills = []
                        for category, skill_list in parsed_skills.items():
                            if isinstance(skill_list, list):
                                flattened_skills.extend(skill_list)
                            elif isinstance(skill_list, str):
                                flattened_skills.append(skill_list)
                        resume_analysis.skills = flattened_skills
                    else:
                        resume_analysis.skills = skills_data if isinstance(skills_data, list) else [skills_data]
                except:
                    # If parsing fails, treat as single skill or split by commas
                    resume_analysis.skills = [skills_data] if skills_data else []
            else:
                resume_analysis.skills = skills_data
                
            resume_analysis.certifications = extracted_data.get('certifications') or []
            resume_analysis.projects = extracted_data.get('projects') or []
            resume_analysis.languages_spoken = extracted_data.get('languages_spoken') or []
            resume_analysis.hobbies_interests = extracted_data.get('hobbies_interests') or []
            resume_analysis.achievements = extracted_data.get('achievements') or []
            
            # Store analysis results
            analysis = result['analysis']
            scores = analysis['scores']
            resume_analysis.overall_score = scores.get('overall_score', 0)
            resume_analysis.skill_score = scores.get('skill_score', 0)
            resume_analysis.experience_score = scores.get('experience_score', 0)
            resume_analysis.education_score = scores.get('education_score', 0)
            resume_analysis.ats_score = scores.get('contact_score', 0)  # Using contact score as ATS score
            resume_analysis.job_match_score = scores.get('project_score', 0)  # Using project score as job match
            
            # Store analysis details with safe defaults
            resume_analysis.summary = analysis.get('summary') or {}
            resume_analysis.strengths = analysis.get('strengths') or []
            resume_analysis.weaknesses = analysis.get('weaknesses') or []
            resume_analysis.recommendations = analysis.get('recommendations') or []
            
            resume_analysis.save()
            
            # Save detailed recommendations
            for rec_data in analysis['recommendations']:
                AnalysisRecommendation.objects.create(
                    analysis=resume_analysis,
                    category=rec_data.get('category', 'General'),
                    priority=rec_data.get('priority', 'medium'),
                    title=rec_data.get('title', 'Recommendation'),
                    description=rec_data.get('description', ''),
                    action_items=rec_data.get('action_items', [])
                )
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # File might already be deleted
        
    except Exception as e:
        # Handle errors
        resume_analysis.status = 'failed'
        resume_analysis.error_message = str(e)
        resume_analysis.save()
        raise

def perform_mock_analysis(resume_analysis):
    """Fallback mock analysis when AI service is not available"""
    resume_analysis.status = 'completed'
    resume_analysis.resume_text = "Sample resume text for testing"
    resume_analysis.word_count = 150
    resume_analysis.overall_score = 75
    resume_analysis.skill_score = 80
    resume_analysis.experience_score = 70
    resume_analysis.education_score = 75
    resume_analysis.ats_score = 85
    resume_analysis.job_match_score = 60
    
    # Mock extracted data
    resume_analysis.full_name = "John Doe"
    resume_analysis.email_address = "john.doe@example.com"
    resume_analysis.phone_number = "+1234567890"
    resume_analysis.education_details = [
        {"degree": "Bachelor of Science", "institution": "University of Example", "year": "2020"}
    ]
    resume_analysis.work_experience = [
        {"job_title": "Software Developer", "company": "Tech Corp", "duration": "2020-2023"}
    ]
    resume_analysis.skills = ["Python", "JavaScript", "React", "Django"]
    resume_analysis.certifications = ["AWS Certified Developer"]
    resume_analysis.projects = [
        {"name": "E-commerce Website", "description": "Built with React and Node.js"}
    ]
    resume_analysis.languages_spoken = ["English", "Spanish"]
    resume_analysis.hobbies_interests = ["Reading", "Coding", "Photography"]
    resume_analysis.achievements = ["Dean's List", "Hackathon Winner"]
    
    resume_analysis.summary = {
        'overall_rating': 'Good',
        'rating_description': 'Good resume with minor areas for improvement',
        'overall_score': 75,
        'total_skills': 4,
        'total_experience': 1,
        'total_projects': 1,
        'total_education': 1,
        'has_contact_info': True,
        'has_certifications': True,
        'has_achievements': True
    }
    
    resume_analysis.strengths = ['Strong technical skills', 'Good experience', 'Complete contact information']
    resume_analysis.weaknesses = ['Could add more projects', 'Limited certifications']
    
    resume_analysis.save()
    
    # Add sample recommendations
    AnalysisRecommendation.objects.create(
        analysis=resume_analysis,
        category='Skills',
        priority='high',
        title='Expand Technical Skills',
        description='Add more programming languages and frameworks',
        action_items=['Learn React', 'Add SQL experience', 'Include cloud platforms']
    )
