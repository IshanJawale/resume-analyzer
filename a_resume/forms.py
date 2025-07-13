from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ResumeAnalysis, UserProfile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        # Add placeholders
        self.fields["username"].widget.attrs["placeholder"] = "Enter username"
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter last name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter email address"
        self.fields["password1"].widget.attrs["placeholder"] = "Create password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"


class ResumeUploadForm(forms.ModelForm):
    JOB_CATEGORY_CHOICES = [
        ("", "Select target job category (optional)"),
        ("software_engineer", "Software Engineer"),
        ("data_scientist", "Data Scientist"),
        ("web_developer", "Web Developer"),
        ("devops_engineer", "DevOps Engineer"),
        ("product_manager", "Product Manager"),
        ("designer", "Designer"),
        ("analyst", "Business Analyst"),
        ("other", "Other"),
    ]

    target_job_category = forms.ChoiceField(
        choices=JOB_CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = ResumeAnalysis
        fields = ["file", "target_job_category"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.txt",
                    "id": "resume-file",
                }
            )
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB.")

            # Check file extension
            allowed_extensions = [".pdf", ".doc", ".docx"]
            file_extension = file.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    "Only PDF, DOC, and DOCX files are allowed."
                )

        return file


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "phone_number",
            "linkedin_url",
            "github_url",
            "website_url",
            "email_notifications",
            "marketing_emails",
        ]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 (555) 123-4567"}
            ),
            "linkedin_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://linkedin.com/in/username",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username",
                }
            ),
            "website_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://yourwebsite.com",
                }
            ),
            "email_notifications": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "marketing_emails": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        self.fields["first_name"].widget.attrs["class"] = "form-control"
        self.fields["last_name"].widget.attrs["class"] = "form-control"
        self.fields["email"].widget.attrs["class"] = "form-control"

        # Add placeholders
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter last name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter email address"


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        )
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Your Message", "rows": 5}
        )
    )
