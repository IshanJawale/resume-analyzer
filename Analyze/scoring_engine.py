"""
Resume Scoring Engine Module

Provides comprehensive scoring algorithms for resume analysis.
"""

from typing import Dict, List


class ResumeScoringEngine:
    """
    Handles all scoring calculations for resume analysis
    """

    # Key skills that are highly valued
    HIGH_VALUE_SKILLS = {
        "technical": [
            "python",
            "javascript",
            "react",
            "node.js",
            "aws",
            "docker",
            "kubernetes",
            "machine learning",
            "ai",
            "data science",
            "sql",
            "postgresql",
            "mongodb",
            "git",
            "agile",
            "scrum",
            "devops",
            "cloud computing",
            "microservices",
            "api",
            "tensorflow",
            "pytorch",
            "django",
            "flask",
            "spring boot",
            "angular",
            "vue.js",
            "typescript",
            "java",
            "c++",
            "golang",
            "rust",
            "kotlin",
            "swift",
        ],
        "soft": [
            "leadership",
            "communication",
            "teamwork",
            "problem solving",
            "critical thinking",
            "project management",
            "time management",
            "analytical",
            "creative",
            "adaptable",
        ],
    }

    # Minimum thresholds for scoring
    MIN_WORK_EXPERIENCE_YEARS = 2
    MIN_EDUCATION_LEVEL = "bachelor"
    MIN_SKILLS_COUNT = 5

    def calculate_overall_score(self, structured_data: Dict) -> int:
        """
        Calculate overall resume score based on multiple factors
        """
        scores = {
            "skills": self._calculate_skills_score(structured_data.get("skills", [])),
            "experience": self._calculate_experience_score(
                structured_data.get("work_experience", [])
            ),
            "education": self._calculate_education_score(
                structured_data.get("education_details", [])
            ),
            "projects": self._calculate_projects_score(
                structured_data.get("projects", [])
            ),
            "certifications": self._calculate_certifications_score(
                structured_data.get("certifications", [])
            ),
            "completeness": self._calculate_completeness_score(structured_data),
        }

        # Weighted average calculation
        weights = {
            "skills": 0.25,
            "experience": 0.25,
            "education": 0.15,
            "projects": 0.15,
            "certifications": 0.10,
            "completeness": 0.10,
        }

        overall_score = sum(scores[key] * weights[key] for key in scores)
        return max(0, min(100, int(overall_score)))

    def _calculate_skills_score(self, skills: List) -> int:
        """
        Calculate score based on skills quality and quantity
        """
        print(f"DEBUG: Skills input: {skills}")
        print(f"DEBUG: Skills type: {type(skills)}")
        print(f"DEBUG: Skills length: {len(skills) if skills else 0}")
        
        if not skills:
            print("DEBUG: No skills found, returning 0")
            return 0

        # Handle both list of strings and list of dicts
        processed_skills = []
        for skill in skills:
            if isinstance(skill, dict):
                # Extract skill name from dict
                skill_name = skill.get('name') or skill.get('skill') or str(skill)
                processed_skills.append(skill_name)
            elif isinstance(skill, str):
                processed_skills.append(skill)
            else:
                processed_skills.append(str(skill))
        
        print(f"DEBUG: Processed skills: {processed_skills}")
        
        skills_lower = [
            skill.lower() for skill in processed_skills if skill and isinstance(skill, str)
        ]
        print(f"DEBUG: Skills lower: {skills_lower}")
        
        technical_matches = sum(
            1
            for skill in skills_lower
            if any(tech in skill for tech in self.HIGH_VALUE_SKILLS["technical"])
        )
        soft_matches = sum(
            1
            for skill in skills_lower
            if any(soft in skill for soft in self.HIGH_VALUE_SKILLS["soft"])
        )

        print(f"DEBUG: Technical matches: {technical_matches}")
        print(f"DEBUG: Soft matches: {soft_matches}")

        # Base score for having skills
        base_score = min(len(processed_skills) * 2, 40)

        # Bonus for high-value skills
        technical_bonus = min(technical_matches * 8, 40)
        soft_bonus = min(soft_matches * 5, 20)

        total_score = min(base_score + technical_bonus + soft_bonus, 100)
        print(f"DEBUG: Base score: {base_score}, Technical bonus: {technical_bonus}, Soft bonus: {soft_bonus}, Total: {total_score}")

        return total_score

    def _calculate_experience_score(self, work_experience: List) -> int:
        """
        Calculate score based on work experience
        """
        if not work_experience:
            return 0

        # Count total years of experience
        total_years = len(work_experience)  # Simplified calculation
        base_score = min(total_years * 15, 60)

        # Bonus for senior positions
        senior_positions = [
            "senior",
            "lead",
            "manager",
            "director",
            "architect",
            "principal",
            "head",
            "chief",
        ]
        leadership_bonus = 0
        for exp in work_experience:
            if isinstance(exp, str):
                exp_lower = exp.lower()
                if any(pos in exp_lower for pos in senior_positions):
                    leadership_bonus += 10

        return min(base_score + leadership_bonus, 100)

    def _calculate_education_score(self, education: List) -> int:
        """
        Calculate score based on education level
        """
        if not education:
            return 30  # Basic score for missing education

        education_levels = {
            "phd": 100,
            "doctorate": 100,
            "master": 85,
            "mba": 85,
            "bachelor": 70,
            "associate": 50,
            "diploma": 40,
            "certificate": 30,
        }

        max_score = 0
        for edu in education:
            if isinstance(edu, str):
                edu_lower = edu.lower()
                for level, score in education_levels.items():
                    if level in edu_lower:
                        max_score = max(max_score, score)
                        break

        return max_score if max_score > 0 else 50

    def _calculate_projects_score(self, projects: List) -> int:
        """
        Calculate score based on projects
        """
        if not projects:
            return 0

        # Base score for having projects
        base_score = min(len(projects) * 15, 60)

        # Bonus for project complexity indicators
        complexity_keywords = [
            "machine learning",
            "ai",
            "full stack",
            "microservices",
            "cloud",
            "api",
            "database",
            "web application",
            "mobile app",
            "deployment",
            "production",
        ]

        complexity_bonus = 0
        for project in projects:
            if isinstance(project, str):
                project_lower = project.lower()
                matches = sum(
                    1 for keyword in complexity_keywords if keyword in project_lower
                )
                complexity_bonus += min(matches * 5, 15)

        return min(base_score + complexity_bonus, 100)

    def _calculate_certifications_score(self, certifications: List) -> int:
        """
        Calculate score based on certifications
        """
        if not certifications:
            return 0

        # High-value certifications
        valuable_certs = [
            "aws",
            "azure",
            "google cloud",
            "pmp",
            "scrum master",
            "cissp",
            "ceh",
            "cisa",
            "comptia",
            "cisco",
            "oracle",
            "microsoft",
            "salesforce",
        ]

        base_score = min(len(certifications) * 10, 40)
        value_bonus = 0

        for cert in certifications:
            if isinstance(cert, str):
                cert_lower = cert.lower()
                if any(valuable in cert_lower for valuable in valuable_certs):
                    value_bonus += 15

        return min(base_score + value_bonus, 100)

    def _calculate_completeness_score(self, structured_data: Dict) -> int:
        """
        Calculate score based on profile completeness
        """
        required_fields = [
            "full_name",
            "email_address",
            "phone_number",
            "work_experience",
            "education_details",
            "skills",
        ]

        completed_fields = 0
        for field in required_fields:
            value = structured_data.get(field)
            if value and (
                (isinstance(value, list) and len(value) > 0)
                or (isinstance(value, str) and value.strip())
            ):
                completed_fields += 1

        # Additional points for optional but valuable fields
        optional_fields = ["projects", "certifications", "achievements"]
        for field in optional_fields:
            value = structured_data.get(field)
            if value and (
                (isinstance(value, list) and len(value) > 0)
                or (isinstance(value, str) and value.strip())
            ):
                completed_fields += 0.5

        max_possible = len(required_fields) + len(optional_fields) * 0.5
        completeness_ratio = completed_fields / max_possible
        return int(completeness_ratio * 100)

    def get_score_breakdown(self, structured_data: Dict) -> Dict[str, int]:
        """
        Get detailed score breakdown for each category
        """
        return {
            "skills_score": self._calculate_skills_score(
                structured_data.get("skills", [])
            ),
            "experience_score": self._calculate_experience_score(
                structured_data.get("work_experience", [])
            ),
            "education_score": self._calculate_education_score(
                structured_data.get("education_details", [])
            ),
            "projects_score": self._calculate_projects_score(
                structured_data.get("projects", [])
            ),
            "certifications_score": self._calculate_certifications_score(
                structured_data.get("certifications", [])
            ),
            "completeness_score": self._calculate_completeness_score(structured_data),
        }

    def get_score_interpretation(self, score: int) -> str:
        """
        Get interpretation of the overall score
        """
        if score >= 90:
            return "Excellent - Outstanding resume with comprehensive information"
        elif score >= 80:
            return "Very Good - Strong resume with good coverage of key areas"
        elif score >= 70:
            return "Good - Solid resume with room for minor improvements"
        elif score >= 60:
            return "Average - Decent resume but could benefit from enhancements"
        elif score >= 50:
            return "Below Average - Resume needs significant improvements"
        else:
            return "Poor - Resume requires major restructuring and content additions"
