"""
New Resume Analysis Service using Groq API for AI-powered resume analysis

This service provides complete resume analysis including text extraction,
structured data extraction using AI, and comprehensive scoring.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

# Import our modular components
from .ai_data_extractor import AIDataExtractor
from .recommendations_generator import RecommendationsGenerator
from .scoring_engine import ResumeScoringEngine
from .text_extractor import ResumeTextExtractor

logger = logging.getLogger(__name__)


class NewResumeAnalysisService:
    """
    Complete resume analysis service with integrated text extraction and AI analysis
    """

    def __init__(self):
        self.text_extractor = ResumeTextExtractor()
        self.data_extractor = AIDataExtractor()
        self.scoring_engine = ResumeScoringEngine()
        self.recommendations_generator = RecommendationsGenerator()

    def extract_resume_text(self, pdf_path: str) -> str:
        """
        Extract text from resume PDF using the text extractor module
        """
        return self.text_extractor.extract_text(pdf_path)

    def extract_and_analyze_resume(self, file_path: str) -> Dict:
        """
        Extract text from resume and analyze it using Groq API

        Args:
            file_path: Path to uploaded resume file

        Returns:
            Dictionary with extraction and analysis results
        """
        try:
            # Step 1: Extract text from resume
            resume_text = self.extract_resume_text(file_path)

            if not resume_text:
                return {
                    "success": False,
                    "error": "Could not extract text from resume",
                    "extracted_data": {},
                    "analysis": {},
                }

            # Step 2: Use Groq API to extract structured data
            structured_data = self._extract_structured_data(resume_text)

            if not structured_data:
                return {
                    "success": False,
                    "error": "Could not extract structured data from resume",
                    "extracted_data": {},
                    "analysis": {},
                }

            # Step 3: Generate analysis and recommendations
            analysis_result = self._generate_analysis(structured_data, resume_text)

            return {
                "success": True,
                "resume_text": resume_text,
                "word_count": len(resume_text.split()),
                "char_count": len(resume_text),
                "extracted_data": structured_data,
                "analysis": analysis_result,
            }

        except Exception as e:
            logger.error(f"Error in extract_and_analyze_resume: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {},
                "analysis": {},
            }

    def _extract_structured_data(self, resume_text: str) -> Dict:
        """
        Extract structured data from resume text using AI data extractor
        """
        return self.data_extractor.extract_structured_data(resume_text)

    def _generate_analysis(self, structured_data: Dict, resume_text: str) -> Dict:
        """
        Generate analysis and recommendations using modular components
        """
        # Calculate overall score and breakdown
        overall_score = self.scoring_engine.calculate_overall_score(structured_data)
        score_breakdown = self.scoring_engine.get_score_breakdown(structured_data)

        # Generate recommendations
        recommendations = (
            self.recommendations_generator.generate_comprehensive_recommendations(
                structured_data, score_breakdown
            )
        )

        # Get improvement priorities
        improvement_priorities = (
            self.recommendations_generator.get_improvement_priority(score_breakdown)
        )

        # Generate analysis summary
        analysis = {
            "scores": {"overall_score": overall_score, **score_breakdown},
            "recommendations": [
                {
                    "category": "General",
                    "priority": "medium",
                    "title": "Improvement Suggestion",
                    "description": rec,
                    "action_items": [],
                }
                for rec in recommendations
            ],
            "summary": {
                "overall_rating": (
                    "Good"
                    if overall_score >= 60
                    else "Average" if overall_score >= 40 else "Needs Improvement"
                ),
                "rating_description": self.scoring_engine.get_score_interpretation(
                    overall_score
                ),
                "score_interpretation": self.scoring_engine.get_score_interpretation(
                    overall_score
                ),
                "improvement_priorities": improvement_priorities,
                "total_recommendations": len(recommendations),
                "total_skills": len(structured_data.get("skills", [])),
                "total_experience": len(structured_data.get("work_experience", [])),
                "total_education": len(structured_data.get("education_details", [])),
                "has_contact_info": bool(
                    structured_data.get("email_address")
                    and structured_data.get("phone_number")
                ),
            },
            "strengths": self._identify_strengths(structured_data, score_breakdown),
            "weaknesses": self._identify_weaknesses(structured_data, score_breakdown),
        }

        return analysis

    def _identify_strengths(
        self, structured_data: Dict, score_breakdown: Dict
    ) -> List[str]:
        """
        Identify strengths based on high-scoring areas
        """
        strengths = []

        # Check high-scoring areas
        for category, score in score_breakdown.items():
            if score >= 80:
                category_name = category.replace("_score", "").replace("_", " ").title()
                strengths.append(f"Strong {category_name}")

        # Check for specific strengths
        if structured_data.get("skills") and len(structured_data["skills"]) > 8:
            strengths.append("Comprehensive skill set")

        if structured_data.get("certifications"):
            strengths.append("Professional certifications")

        if structured_data.get("projects") and len(structured_data["projects"]) > 2:
            strengths.append("Diverse project portfolio")

        return strengths[:5]  # Limit to top 5 strengths

    def _identify_weaknesses(
        self, structured_data: Dict, score_breakdown: Dict
    ) -> List[str]:
        """
        Identify weaknesses based on low-scoring areas
        """
        weaknesses = []

        # Check low-scoring areas
        for category, score in score_breakdown.items():
            if score < 60:
                category_name = category.replace("_score", "").replace("_", " ").title()
                weaknesses.append(f"Limited {category_name}")

        # Check for specific weaknesses
        if not structured_data.get("projects"):
            weaknesses.append("No projects listed")

        if not structured_data.get("certifications"):
            weaknesses.append("No certifications mentioned")

        if not structured_data.get("achievements"):
            weaknesses.append("No achievements highlighted")

        return weaknesses[:5]  # Limit to top 5 weaknesses


# Test function
def test_new_service():
    """Test the new analysis service"""
    service = NewResumeAnalysisService()

    # Test with resume.pdf in parent directory
    result = service.extract_and_analyze_resume("resume.pdf")

    print("=== NEW RESUME ANALYSIS SERVICE TEST ===")
    print(f"Success: {result['success']}")

    if result["success"]:
        print(f"Word count: {result['word_count']}")
        print(f"Overall score: {result['analysis']['scores']['overall_score']}")

        print("\n=== EXTRACTED DATA ===")
        data = result["extracted_data"]
        print(f"Name: {data.get('full_name', 'N/A')}")
        print(f"Email: {data.get('email_address', 'N/A')}")
        print(f"Phone: {data.get('phone_number', 'N/A')}")
        print(f"Skills: {len(data.get('skills', []))} skills")
        print(f"Experience: {len(data.get('work_experience', []))} entries")
        print(f"Projects: {len(data.get('projects', []))} projects")

        print("\n=== RECOMMENDATIONS ===")
        for i, rec in enumerate(result["analysis"]["recommendations"][:3], 1):
            print(f"{i}. {rec['title']} ({rec['priority']})")
            print(f"   {rec['description']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    test_new_service()
