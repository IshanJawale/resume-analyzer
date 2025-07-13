"""
New Resume Analysis Service using Groq API for AI-powered resume analysis

This service provides complete resume analysis including text extraction,
structured data extraction using AI, and comprehensive scoring.
"""

import sys
import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import dotenv

from groq import Groq

# PDF processing imports
import pdfplumber

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print(
        "Warning: OCR libraries not available. Only text-based PDFs will be supported."
    )

# Load environment variables
dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class NewResumeAnalysisService:
    """
    Complete resume analysis service with integrated text extraction and AI analysis
    """

    def __init__(self):
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def extract_resume_text(self, pdf_path: str) -> str:
        """
        Extract text from resume PDF - handles both text and image-based PDFs

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        extracted_text = ""

        try:
            print(f"Extracting text from: {pdf_path}")

            # Method 1: Try extracting text directly from PDF
            print("Attempting direct text extraction...")
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n"

            # Check if we got meaningful text (more than just spaces/newlines)
            if len(extracted_text.strip()) > 50:  # Arbitrary threshold
                print("✓ Direct text extraction successful!")
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                print(f"✓ Extracted {word_count} words, {char_count} characters")
                return extracted_text.strip()
            else:
                print("Direct text extraction failed or insufficient. Trying OCR...")
                extracted_text = ""  # Reset

                if not OCR_AVAILABLE:
                    print(
                        "❌ OCR libraries not available. Cannot process image-based PDFs."
                    )
                    return ""

                # Method 2: Use OCR for image-based or flattened PDFs
                print("Converting PDF to images for OCR...")

                # Convert PDF to images
                pages = convert_from_path(pdf_path, dpi=300)  # High DPI for better OCR

                print(f"Processing {len(pages)} pages with OCR...")
                for page_num, page_image in enumerate(pages):
                    print(f"  Processing page {page_num + 1}/{len(pages)}...")

                    # Use OCR to extract text from the image
                    page_text = pytesseract.image_to_string(page_image, lang="eng")

                    if page_text and page_text.strip():
                        extracted_text += f"--- Page {page_num + 1} ---\n"
                        extracted_text += page_text + "\n"

                if extracted_text.strip():
                    print("✓ OCR extraction successful!")
                    word_count = len(extracted_text.split())
                    char_count = len(extracted_text)
                    print(f"✓ Extracted {word_count} words, {char_count} characters")
                    return extracted_text.strip()
                else:
                    print("❌ Both direct extraction and OCR failed.")
                    return ""

        except Exception as e:
            print(f"❌ Error during text extraction: {e}")
            return ""

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
        Extract structured data from resume text using Groq API
        """
        try:
            prompt = f"""{resume_text}

From the above text, extract the following information:
1. Full Name
2. Email Address
3. Phone Number
4. Education Details (Degree, Institution, Year)
5. Work Experience (Job Title, Company, Duration)
6. Skills
7. Certifications
8. Projects
9. Languages Spoken
10. Hobbies/Interests
11. Achievements

Return the extracted information in JSON format with appropriate keys. The output should be only the JSON object without any additional text or explanation.
"""

            completion = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Lower temperature for more consistent extraction
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
            )

            json_output_string = completion.choices[0].message.content.strip()

            # Clean up the JSON string
            json_output_string = self._clean_json_output(json_output_string)

            # Parse JSON
            try:
                raw_data = json.loads(json_output_string)
                # Map the keys to match our database fields
                structured_data = self._map_groq_response(raw_data)
                return structured_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw output: {json_output_string}")
                return {}

        except Exception as e:
            logger.error(f"Error in _extract_structured_data: {e}")
            return {}

    def _map_groq_response(self, raw_data: Dict) -> Dict:
        """
        Map Groq API response keys to our database field names
        """
        mapped_data = {}

        # Map direct fields
        mapping = {
            "Full Name": "full_name",
            "Email Address": "email_address",
            "Phone Number": "phone_number",
            "Education Details": "education_details",
            "Work Experience": "work_experience",
            "Skills": "skills",
            "Certifications": "certifications",
            "Projects": "projects",
            "Languages Spoken": "languages_spoken",
            "Hobbies/Interests": "hobbies_interests",
            "Achievements": "achievements",
        }

        for groq_key, db_key in mapping.items():
            if groq_key in raw_data:
                value = raw_data[groq_key]
                # Ensure all list fields are actual lists, not None
                if db_key in [
                    "education_details",
                    "work_experience",
                    "skills",
                    "certifications",
                    "projects",
                    "languages_spoken",
                    "hobbies_interests",
                    "achievements",
                ]:
                    if value is None:
                        mapped_data[db_key] = []
                    elif isinstance(value, list):
                        mapped_data[db_key] = value
                    else:
                        mapped_data[db_key] = [value] if value else []
                else:
                    mapped_data[db_key] = value if value is not None else ""
            else:
                # Provide default values for missing fields
                if db_key in [
                    "education_details",
                    "work_experience",
                    "skills",
                    "certifications",
                    "projects",
                    "languages_spoken",
                    "hobbies_interests",
                    "achievements",
                ]:
                    mapped_data[db_key] = []
                else:
                    mapped_data[db_key] = ""

        # Handle skills if it's a dictionary (convert to list)
        if "skills" in mapped_data and isinstance(mapped_data["skills"], dict):
            # Flatten skills dictionary into a single list
            all_skills = []
            for category, skill_list in mapped_data["skills"].items():
                if isinstance(skill_list, list):
                    all_skills.extend(skill_list)
                elif isinstance(skill_list, str):
                    all_skills.append(skill_list)
            mapped_data["skills"] = all_skills

        # Ensure work_experience is a list
        if "work_experience" in mapped_data and not isinstance(
            mapped_data["work_experience"], list
        ):
            mapped_data["work_experience"] = (
                [mapped_data["work_experience"]]
                if mapped_data["work_experience"]
                else []
            )

        # Ensure education_details is a list
        if "education_details" in mapped_data and not isinstance(
            mapped_data["education_details"], list
        ):
            mapped_data["education_details"] = (
                [mapped_data["education_details"]]
                if mapped_data["education_details"]
                else []
            )

        return mapped_data

    def _clean_json_output(self, json_string: str) -> str:
        """Clean up JSON output from Groq API"""
        # Remove markdown code blocks if present
        if json_string.startswith("```json"):
            json_string = json_string[7:]
        if json_string.startswith("```"):
            json_string = json_string[3:]
        if json_string.endswith("```"):
            json_string = json_string[:-3]

        return json_string.strip()

    def _generate_analysis(self, structured_data: Dict, resume_text: str) -> Dict:
        """
        Generate analysis and recommendations based on extracted data
        """
        analysis = {
            "scores": {},
            "recommendations": [],
            "summary": {},
            "strengths": [],
            "weaknesses": [],
        }

        # Calculate scores
        scores = self._calculate_scores(structured_data)
        analysis["scores"] = scores

        # Generate recommendations
        recommendations = self._generate_recommendations(structured_data, scores)
        analysis["recommendations"] = recommendations

        # Generate summary
        summary = self._generate_summary(structured_data, scores)
        analysis["summary"] = summary

        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(
            structured_data, scores
        )
        analysis["strengths"] = strengths
        analysis["weaknesses"] = weaknesses

        return analysis

    def _calculate_scores(self, data: Dict) -> Dict:
        """Calculate various scores based on extracted data"""
        scores = {
            "overall_score": 0,
            "skill_score": 0,
            "experience_score": 0,
            "education_score": 0,
            "contact_score": 0,
            "project_score": 0,
        }

        # Contact information score (0-20)
        contact_score = 0
        if data.get("full_name"):
            contact_score += 5
        if data.get("email_address"):
            contact_score += 5
        if data.get("phone_number"):
            contact_score += 5
        if data.get("languages_spoken"):
            contact_score += 5
        scores["contact_score"] = contact_score

        # Skills score (0-25)
        skills = data.get("skills", [])
        if isinstance(skills, list):
            skill_count = len(skills)
            skills_score = min(skill_count * 2, 25)
        else:
            skills_score = 10 if skills else 0
        scores["skill_score"] = skills_score

        # Experience score (0-25)
        work_experience = data.get("work_experience", [])
        if isinstance(work_experience, list):
            exp_count = len(work_experience)
            experience_score = min(exp_count * 8, 25)
        else:
            experience_score = 15 if work_experience else 0
        scores["experience_score"] = experience_score

        # Education score (0-15)
        education = data.get("education_details", [])
        if isinstance(education, list):
            edu_count = len(education)
            education_score = min(edu_count * 7, 15)
        else:
            education_score = 10 if education else 0
        scores["education_score"] = education_score

        # Project score (0-15)
        projects = data.get("projects", [])
        if isinstance(projects, list):
            project_count = len(projects)
            project_score = min(project_count * 3, 15)
        else:
            project_score = 10 if projects else 0
        scores["project_score"] = project_score

        # Calculate overall score
        overall_score = (
            scores["contact_score"]
            + scores["skill_score"]
            + scores["experience_score"]
            + scores["education_score"]
            + scores["project_score"]
        )

        # Add bonus for certifications and achievements
        if data.get("certifications"):
            overall_score += 5
        if data.get("achievements"):
            overall_score += 5

        scores["overall_score"] = min(overall_score, 100)

        return scores

    def _generate_recommendations(self, data: Dict, scores: Dict) -> List[Dict]:
        """Generate recommendations based on extracted data and scores"""
        recommendations = []

        # Contact information recommendations
        if scores["contact_score"] < 15:
            missing_contact = []
            if not data.get("full_name"):
                missing_contact.append("full name")
            if not data.get("email_address"):
                missing_contact.append("email address")
            if not data.get("phone_number"):
                missing_contact.append("phone number")

            if missing_contact:
                recommendations.append(
                    {
                        "category": "Contact Information",
                        "priority": "high",
                        "title": "Complete Contact Information",
                        "description": f'Add missing contact details: {", ".join(missing_contact)}',
                        "action_items": [f"Add {item}" for item in missing_contact],
                    }
                )

        # Skills recommendations
        if scores["skill_score"] < 15:
            recommendations.append(
                {
                    "category": "Skills",
                    "priority": "high",
                    "title": "Expand Skills Section",
                    "description": "Add more relevant technical and soft skills to strengthen your profile",
                    "action_items": [
                        "List programming languages and frameworks",
                        "Include software tools and platforms",
                        "Add soft skills like communication and teamwork",
                        "Consider adding emerging technologies",
                    ],
                }
            )

        # Experience recommendations
        if scores["experience_score"] < 15:
            recommendations.append(
                {
                    "category": "Work Experience",
                    "priority": "high",
                    "title": "Enhance Work Experience",
                    "description": "Add more detailed work experience with quantifiable achievements",
                    "action_items": [
                        "Include specific job responsibilities",
                        "Add quantifiable achievements with metrics",
                        "Use action verbs to describe accomplishments",
                        "Include internships and part-time work",
                    ],
                }
            )

        # Education recommendations
        if scores["education_score"] < 10:
            recommendations.append(
                {
                    "category": "Education",
                    "priority": "medium",
                    "title": "Add Education Details",
                    "description": "Include comprehensive education information",
                    "action_items": [
                        "Add degree information",
                        "Include institution names and graduation years",
                        "Add relevant coursework",
                        "Include academic achievements",
                    ],
                }
            )

        # Projects recommendations
        if scores["project_score"] < 10:
            recommendations.append(
                {
                    "category": "Projects",
                    "priority": "high",
                    "title": "Add Personal Projects",
                    "description": "Include relevant projects to demonstrate your skills",
                    "action_items": [
                        "Add 2-3 personal or academic projects",
                        "Include project descriptions and outcomes",
                        "List technologies used",
                        "Add project links or GitHub repositories",
                    ],
                }
            )

        # Certifications recommendations
        if not data.get("certifications"):
            recommendations.append(
                {
                    "category": "Certifications",
                    "priority": "medium",
                    "title": "Add Professional Certifications",
                    "description": "Include relevant certifications to boost credibility",
                    "action_items": [
                        "List professional certifications",
                        "Add certification dates and issuing organizations",
                        "Include online course certifications",
                        "Consider pursuing industry-relevant certifications",
                    ],
                }
            )

        # Achievements recommendations
        if not data.get("achievements"):
            recommendations.append(
                {
                    "category": "Achievements",
                    "priority": "medium",
                    "title": "Highlight Achievements",
                    "description": "Add specific achievements and accomplishments",
                    "action_items": [
                        "Include awards and recognition",
                        "Add competition wins or hackathon participation",
                        "List publications or research contributions",
                        "Include volunteer work and leadership roles",
                    ],
                }
            )

        return recommendations

    def _generate_summary(self, data: Dict, scores: Dict) -> Dict:
        """Generate analysis summary"""
        overall_score = scores["overall_score"]

        if overall_score >= 80:
            rating = "Excellent"
            rating_description = "Outstanding resume with comprehensive information"
        elif overall_score >= 60:
            rating = "Good"
            rating_description = "Good resume with minor areas for improvement"
        elif overall_score >= 40:
            rating = "Average"
            rating_description = "Average resume that needs significant enhancement"
        else:
            rating = "Poor"
            rating_description = "Resume needs major improvements in multiple areas"

        return {
            "rating": rating,
            "description": rating_description,
            "overall_score": overall_score,
            "total_skills": (
                len(data.get("skills", []))
                if isinstance(data.get("skills"), list)
                else 0
            ),
            "total_experience": (
                len(data.get("work_experience", []))
                if isinstance(data.get("work_experience"), list)
                else 0
            ),
            "total_projects": (
                len(data.get("projects", []))
                if isinstance(data.get("projects"), list)
                else 0
            ),
            "total_education": (
                len(data.get("education_details", []))
                if isinstance(data.get("education_details"), list)
                else 0
            ),
            "has_contact_info": bool(
                data.get("email_address") and data.get("phone_number")
            ),
            "has_certifications": bool(data.get("certifications")),
            "has_achievements": bool(data.get("achievements")),
        }

    def _identify_strengths_weaknesses(self, data: Dict, scores: Dict) -> tuple:
        """Identify strengths and weaknesses based on scores"""
        strengths = []
        weaknesses = []

        # Analyze each category
        if scores["contact_score"] >= 15:
            strengths.append("Complete contact information")
        else:
            weaknesses.append("Missing contact details")

        if scores["skill_score"] >= 20:
            strengths.append("Comprehensive skills section")
        elif scores["skill_score"] >= 15:
            strengths.append("Good skills coverage")
        else:
            weaknesses.append("Limited skills listed")

        if scores["experience_score"] >= 20:
            strengths.append("Strong work experience")
        elif scores["experience_score"] >= 15:
            strengths.append("Adequate work experience")
        else:
            weaknesses.append("Limited work experience")

        if scores["education_score"] >= 12:
            strengths.append("Strong educational background")
        elif scores["education_score"] < 8:
            weaknesses.append("Limited education details")

        if scores["project_score"] >= 12:
            strengths.append("Good project portfolio")
        elif scores["project_score"] < 8:
            weaknesses.append("Few or no projects listed")

        # Additional strengths
        if data.get("certifications"):
            strengths.append("Professional certifications")

        if data.get("achievements"):
            strengths.append("Notable achievements")

        if data.get("languages_spoken") and len(data.get("languages_spoken", [])) > 1:
            strengths.append("Multilingual capabilities")

        return strengths, weaknesses


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
        print(f"Rating: {result['analysis']['summary']['overall_rating']}")

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
