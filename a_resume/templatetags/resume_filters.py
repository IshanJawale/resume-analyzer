import json

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary with a key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""


@register.filter
def get_attr_or_self(obj, attr):
    """Get an attribute from an object, or return the object itself if it's a string"""
    if isinstance(obj, dict):
        return obj.get(attr, "")
    elif isinstance(obj, str):
        return obj if attr in ["name", "title"] else ""
    return ""


@register.filter
def project_name(project):
    """Get project name, handling both dict and string formats"""
    if isinstance(project, dict):
        return (
            project.get("name")
            or project.get("title")
            or project.get("project_name")
            or "Project"
        )
    elif isinstance(project, str):
        return project
    return "Project"


@register.filter
def project_description(project):
    """Get project description"""
    if isinstance(project, dict):
        return project.get("description") or project.get("summary") or ""
    return ""


@register.filter
def project_duration(project):
    """Get project duration"""
    if isinstance(project, dict):
        return project.get("duration") or project.get("period") or ""
    return ""


@register.filter
def project_technologies(project):
    """Get project technologies as a list"""
    if isinstance(project, dict):
        techs = (
            project.get("technologies")
            or project.get("tech_stack")
            or project.get("tools")
            or []
        )
        if isinstance(techs, str):
            return [tech.strip() for tech in techs.split(",") if tech.strip()]
        elif isinstance(techs, list):
            return techs
    return []


@register.filter
def experience_position(experience):
    """Extract position/job title from experience string or dict"""
    if isinstance(experience, dict):
        return (
            experience.get("job_title")
            or experience.get("position")
            or experience.get("title")
            or "Position"
        )
    elif isinstance(experience, str):
        # Parse string like "Frontend Developer at ArcTech Labs Pvt Ltd (Dec2022 - Feb2023)"
        parts = experience.split(" at ")
        if len(parts) >= 2:
            return parts[0].strip()
        return experience.split(" ")[0] if experience else "Position"
    return "Position"


@register.filter
def experience_company(experience):
    """Extract company from experience string or dict"""
    if isinstance(experience, dict):
        return experience.get("company") or experience.get("organization") or "Company"
    elif isinstance(experience, str):
        # Parse string like "Frontend Developer at ArcTech Labs Pvt Ltd (Dec2022 - Feb2023)"
        parts = experience.split(" at ")
        if len(parts) >= 2:
            company_part = parts[1]
            # Remove duration in parentheses
            if "(" in company_part:
                company_part = company_part.split("(")[0].strip()
            return company_part.strip() if company_part.strip() else "Company"
        return "Company"
    return "Company"


@register.filter
def experience_duration(experience):
    """Extract duration from experience string or dict"""
    if isinstance(experience, dict):
        return (
            experience.get("duration")
            or experience.get("period")
            or "Duration not specified"
        )
    elif isinstance(experience, str):
        # Parse string like "Frontend Developer at ArcTech Labs Pvt Ltd (Dec2022 - Feb2023)"
        import re

        match = re.search(r"\(([^)]+)\)", experience)
        if match:
            return match.group(1)
        return "Duration not specified"
    return "Duration not specified"


@register.filter
def education_degree(education):
    """Extract degree from education string or dict"""
    if isinstance(education, dict):
        return education.get("degree") or education.get("qualification") or "Degree"
    elif isinstance(education, str):
        # Parse string like "BE [Computer Engineering] at Savitribai Phule Pune University (2020-2024)"
        if "[" in education and "]" in education:
            # Extract content in brackets
            start = education.find("[")
            end = education.find("]")
            degree_part = education[:start].strip() + " " + education[start + 1 : end]
            return degree_part.strip()
        else:
            # Take first part before 'at'
            parts = education.split(" at ")
            return parts[0].strip() if parts[0].strip() else "Degree"
    return "Degree"


@register.filter
def education_institution(education):
    """Extract institution from education string or dict"""
    if isinstance(education, dict):
        return (
            education.get("institution")
            or education.get("university")
            or education.get("school")
            or "Institution"
        )
    elif isinstance(education, str):
        # Parse string like "BE [Computer Engineering] at Savitribai Phule Pune University (2020-2024)"
        parts = education.split(" at ")
        if len(parts) >= 2:
            institution_part = parts[1]
            # Remove year in parentheses
            if "(" in institution_part:
                institution_part = institution_part.split("(")[0].strip()
            return (
                institution_part.strip() if institution_part.strip() else "Institution"
            )
        return "Institution"
    return "Institution"


@register.filter
def education_year(education):
    """Extract year from education string or dict"""
    if isinstance(education, dict):
        return (
            education.get("year")
            or education.get("graduation_year")
            or education.get("period")
            or "Year not specified"
        )
    elif isinstance(education, str):
        # Parse string like "BE [Computer Engineering] at Savitribai Phule Pune University (2020-2024)"
        import re

        match = re.search(r"\(([^)]+)\)", education)
        if match:
            return match.group(1)
        return "Year not specified"
    return "Year not specified"
