"""
Resume Recommendations Generator Module

Generates intelligent recommendations for resume improvement.
"""

from typing import Dict, List


class RecommendationsGenerator:
    """
    Generates personalized recommendations for resume improvement
    """

    def __init__(self):
        self.trending_skills = {
            "software_development": [
                "React",
                "Node.js",
                "TypeScript",
                "Docker",
                "Kubernetes",
                "AWS",
                "Microservices",
                "GraphQL",
                "Next.js",
                "Tailwind CSS",
            ],
            "data_science": [
                "Python",
                "Machine Learning",
                "Deep Learning",
                "TensorFlow",
                "PyTorch",
                "Data Visualization",
                "SQL",
                "Big Data",
                "Apache Spark",
                "MLOps",
            ],
            "cloud_computing": [
                "AWS",
                "Azure",
                "Google Cloud Platform",
                "Terraform",
                "Ansible",
                "Jenkins",
                "GitLab CI/CD",
                "Prometheus",
                "Grafana",
                "Service Mesh",
            ],
            "cybersecurity": [
                "Penetration Testing",
                "SIEM",
                "Incident Response",
                "Vulnerability Assessment",
                "Cloud Security",
                "Zero Trust",
                "DevSecOps",
                "Threat Hunting",
                "Compliance",
                "Risk Assessment",
            ],
        }

    def generate_comprehensive_recommendations(
        self, structured_data: Dict, score_breakdown: Dict
    ) -> List[str]:
        """
        Generate comprehensive recommendations based on analysis
        """
        recommendations = []

        # Skills recommendations
        recommendations.extend(self._get_skills_recommendations(structured_data))

        # Experience recommendations
        recommendations.extend(self._get_experience_recommendations(structured_data))

        # Education recommendations
        recommendations.extend(self._get_education_recommendations(structured_data))

        # Projects recommendations
        recommendations.extend(self._get_projects_recommendations(structured_data))

        # Certifications recommendations
        recommendations.extend(
            self._get_certifications_recommendations(structured_data)
        )

        # Format and presentation recommendations
        recommendations.extend(self._get_format_recommendations(structured_data))

        # Content optimization recommendations
        recommendations.extend(self._get_content_recommendations(structured_data))

        # Score-based recommendations
        recommendations.extend(self._get_score_based_recommendations(score_breakdown))

        return recommendations[:15]  # Limit to top 15 recommendations

    def _get_skills_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate skills-related recommendations
        """
        recommendations = []
        skills = structured_data.get("skills", [])

        if not skills or len(skills) < 5:
            recommendations.append(
                "Add more technical skills to strengthen your profile. Aim for at least 8-10 relevant skills."
            )

        # Check for trending skills
        current_skills_lower = [skill.lower() for skill in skills if isinstance(skill, str)]
        missing_trending = []

        for category, trending in self.trending_skills.items():
            category_skills = [
                skill for skill in trending if skill.lower() not in current_skills_lower
            ]
            if category_skills:
                missing_trending.extend(category_skills[:3])

        if missing_trending:
            recommendations.append(
                f"Consider adding trending skills: {', '.join(missing_trending[:5])}"
            )

        # Soft skills check
        soft_skills = [
            "leadership",
            "communication",
            "teamwork",
            "problem solving",
            "project management",
        ]
        has_soft_skills = any(soft in " ".join(str(skill) for skill in skills if skill).lower() for soft in soft_skills)

        if not has_soft_skills:
            recommendations.append(
                "Include soft skills like leadership, communication, and teamwork to show well-rounded capabilities."
            )

        return recommendations

    def _get_experience_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate experience-related recommendations
        """
        recommendations = []
        work_experience = structured_data.get("work_experience", [])

        if not work_experience:
            recommendations.append(
                "Add work experience section with job titles, companies, and key achievements."
            )
        elif len(work_experience) < 2:
            recommendations.append(
                "Consider adding more work experience entries or internships to show career progression."
            )

        # Check for quantifiable achievements
        has_metrics = any(
            any(char.isdigit() for char in str(exp)) for exp in work_experience
        )

        if not has_metrics:
            recommendations.append(
                "Quantify your achievements with specific numbers, percentages, or metrics (e.g., 'Increased sales by 25%')."
            )

        # Check for action verbs
        weak_verbs = ["responsible for", "worked on", "helped with"]
        strong_verbs = ["led", "developed", "implemented", "optimized", "achieved"]

        experience_text = " ".join(str(exp) for exp in work_experience).lower()
        has_weak_verbs = any(verb in experience_text for verb in weak_verbs)
        has_strong_verbs = any(verb in experience_text for verb in strong_verbs)

        if has_weak_verbs and not has_strong_verbs:
            recommendations.append(
                "Use strong action verbs (led, developed, implemented) instead of passive language."
            )

        return recommendations

    def _get_education_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate education-related recommendations
        """
        recommendations = []
        education = structured_data.get("education_details", [])

        if not education:
            recommendations.append(
                "Add education details including degree, institution, and graduation year."
            )

        # Check for relevant coursework or honors
        education_text = " ".join(str(edu) for edu in education).lower()
        has_details = any(
            keyword in education_text
            for keyword in [
                "gpa",
                "honors",
                "dean's list",
                "summa cum laude",
                "magna cum laude",
            ]
        )

        if education and not has_details:
            recommendations.append(
                "Consider adding relevant coursework, GPA (if 3.5+), or academic honors to strengthen education section."
            )

        return recommendations

    def _get_projects_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate projects-related recommendations
        """
        recommendations = []
        projects = structured_data.get("projects", [])

        if not projects:
            recommendations.append(
                "Add a projects section showcasing your technical abilities and problem-solving skills."
            )
        elif len(projects) < 2:
            recommendations.append(
                "Include 2-3 significant projects with technology stack and outcomes."
            )

        # Check for GitHub/portfolio links
        projects_text = " ".join(str(project) for project in projects).lower()
        has_links = any(
            platform in projects_text
            for platform in ["github", "gitlab", "portfolio", "demo", "live"]
        )

        if projects and not has_links:
            recommendations.append(
                "Include GitHub links or live demo URLs for your projects to showcase your work."
            )

        return recommendations

    def _get_certifications_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate certifications-related recommendations
        """
        recommendations = []
        certifications = structured_data.get("certifications", [])

        if not certifications:
            recommendations.append(
                "Consider obtaining industry-relevant certifications to validate your expertise."
            )

        # Suggest specific certifications based on skills
        skills = structured_data.get("skills", [])
        skills_text = " ".join(str(skill) for skill in skills if skill).lower()

        cert_suggestions = []
        if any(aws_skill in skills_text for aws_skill in ["aws", "cloud", "amazon"]):
            cert_suggestions.append("AWS Certified Solutions Architect")

        if any(
            data_skill in skills_text
            for data_skill in ["python", "machine learning", "data science"]
        ):
            cert_suggestions.append("Google Data Analytics Certificate")

        if any(
            pm_skill in skills_text
            for pm_skill in ["project management", "agile", "scrum"]
        ):
            cert_suggestions.append("PMP or Scrum Master certification")

        if cert_suggestions and len(certifications) < 2:
            recommendations.append(
                f"Consider pursuing: {', '.join(cert_suggestions[:2])}"
            )

        return recommendations

    def _get_format_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate formatting and presentation recommendations
        """
        recommendations = []

        # Check for contact information completeness
        missing_contact = []
        if not structured_data.get("email_address"):
            missing_contact.append("email")
        if not structured_data.get("phone_number"):
            missing_contact.append("phone number")

        if missing_contact:
            recommendations.append(
                f"Ensure your contact information includes: {', '.join(missing_contact)}"
            )

        # Professional summary recommendation
        if not any(
            field in structured_data
            for field in ["summary", "objective", "professional_summary"]
        ):
            recommendations.append(
                "Add a professional summary at the top highlighting your key strengths and career goals."
            )

        return recommendations

    def _get_content_recommendations(self, structured_data: Dict) -> List[str]:
        """
        Generate content optimization recommendations
        """
        recommendations = []

        # Check for industry keywords
        all_content = " ".join(
            str(value)
            for value in structured_data.values()
            if isinstance(value, (str, list))
        ).lower()

        # ATS optimization
        if "resume" not in all_content and "cv" not in all_content:
            recommendations.append(
                "Optimize for ATS by including industry-specific keywords throughout your resume."
            )

        # Length recommendations
        word_count = len(all_content.split())
        if word_count < 200:
            recommendations.append(
                "Expand your resume content. Aim for 400-600 words for a comprehensive presentation."
            )
        elif word_count > 800:
            recommendations.append(
                "Consider condensing your resume. Keep it concise while maintaining important details."
            )

        return recommendations

    def _get_score_based_recommendations(self, score_breakdown: Dict) -> List[str]:
        """
        Generate recommendations based on score analysis
        """
        recommendations = []

        # Identify lowest scoring areas
        sorted_scores = sorted(score_breakdown.items(), key=lambda x: x[1])

        for category, score in sorted_scores[:2]:  # Focus on 2 lowest areas
            if score < 60:
                category_name = category.replace("_score", "").replace("_", " ").title()
                recommendations.append(
                    f"Focus on improving your {category_name} section - current score: {score}/100"
                )

        return recommendations

    def get_improvement_priority(self, score_breakdown: Dict) -> List[str]:
        """
        Get prioritized list of areas for improvement
        """
        sorted_scores = sorted(score_breakdown.items(), key=lambda x: x[1])
        return [
            category.replace("_score", "").replace("_", " ").title()
            for category, score in sorted_scores
            if score < 80
        ]
