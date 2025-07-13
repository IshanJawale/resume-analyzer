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
