"""
AI-Powered Data Extraction Module

Uses Groq API to extract structured data from resume text.
"""

import json
import logging
import os
from typing import Dict, List

import dotenv
from groq import Groq

# Load environment variables
dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class AIDataExtractor:
    """
    Handles AI-powered extraction of structured data from resume text
    """

    def __init__(self):
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def extract_structured_data(self, resume_text: str) -> Dict:
        """
        Extract structured data from resume text using Groq API
        """
        try:
            prompt = f"""{resume_text}

From the above resume text, extract the following information and return it in the exact JSON format shown below:

{{
  "Full Name": "string",
  "Email Address": "string", 
  "Phone Number": "string",
  "Education Details": ["Degree at Institution (Year)", "Degree at Institution (Year)"],
  "Work Experience": ["Job Title at Company (Duration)", "Job Title at Company (Duration)"],
  "Skills": ["skill1", "skill2", "skill3"],
  "Certifications": ["certification1", "certification2"],
  "Projects": ["Project Name - Description", "Project Name - Description"],
  "Languages Spoken": ["language1", "language2"],
  "Hobbies/Interests": ["hobby1", "hobby2"],
  "Achievements": ["achievement1", "achievement2"]
}}

Important:
- For Projects: Include project name and brief description in each string
- For Work Experience: Format as "Job Title at Company (Duration)" 
- For Education: Format as "Degree at Institution (Year)"
- For arrays, always use strings, not objects
- If information is not found, use empty string or empty array
- Return only the JSON object, no additional text or explanation
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

                # Log the raw AI response for debugging
                logger.info("=== RAW AI RESPONSE ===")
                logger.info(json.dumps(raw_data, indent=2, ensure_ascii=False))

                # Map the keys to match our database fields
                structured_data = self._map_groq_response(raw_data)

                # Log the mapped data for debugging
                logger.info("=== MAPPED DATA ===")
                logger.info(json.dumps(structured_data, indent=2, ensure_ascii=False))

                return structured_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw output: {json_output_string}")
                return {}

        except Exception as e:
            logger.error(f"Error in extract_structured_data: {e}")
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
                # Fields that should preserve structure (dictionaries/objects)
                structured_fields = ["education_details", "work_experience", "projects"]
                # Fields that should be lists of strings
                list_string_fields = [
                    "skills",
                    "certifications",
                    "languages_spoken",
                    "hobbies_interests",
                    "achievements",
                ]

                if db_key in structured_fields:
                    # Preserve structure for complex fields
                    mapped_data[db_key] = self._normalize_list_field(value)
                elif db_key in list_string_fields:
                    # Convert to strings for simple list fields
                    if isinstance(value, list):
                        normalized = []
                        for item in value:
                            if isinstance(item, dict):
                                extracted_text = (
                                    self._extract_meaningful_text_from_dict(item)
                                )
                                if extracted_text:
                                    normalized.append(extracted_text)
                            elif isinstance(item, str) and item.strip():
                                normalized.append(item.strip())
                            elif item is not None:
                                text = str(item).strip()
                                if text:
                                    normalized.append(text)
                        mapped_data[db_key] = normalized
                    else:
                        mapped_data[db_key] = self._normalize_list_field(value)
                else:
                    mapped_data[db_key] = str(value) if value is not None else ""
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

        return mapped_data

    def _clean_json_output(self, json_string: str) -> str:
        """
        Clean and prepare JSON string for parsing
        """
        # Remove markdown code blocks
        json_string = json_string.replace("```json", "").replace("```", "")
        # Remove extra whitespace
        json_string = json_string.strip()
        return json_string

    def _normalize_list_field(self, value) -> List:
        """
        Normalize a field to ensure it's a proper list.
        For structured data like projects, preserve the dictionary structure.
        For simple data, convert to strings.
        """
        if value is None:
            return []

        if isinstance(value, list):
            normalized = []
            for item in value:
                if isinstance(item, dict):
                    # For structured data, preserve the original dictionary
                    # but ensure it has at least some meaningful content
                    if any(v for v in item.values() if v):
                        normalized.append(item)
                elif isinstance(item, str) and item.strip():
                    normalized.append(item.strip())
                elif item is not None:
                    text = str(item).strip()
                    if text:
                        normalized.append(text)
            return normalized

        if isinstance(value, dict):
            # If it's a single dict, wrap it in a list
            if any(v for v in value.values() if v):
                return [value]
            return []

        if isinstance(value, str) and value.strip():
            return [value.strip()]

        return [str(value)] if value else []

    def _extract_meaningful_text_from_dict(self, item_dict: dict) -> str:
        """
        Extract meaningful text from a dictionary object
        """
        # Priority fields for different types of data
        priority_fields = [
            "name",
            "title",
            "project_name",
            "project_title",
            "job_title",
            "position",
            "role",
            "company",
            "organization",
            "degree",
            "certification",
            "skill",
            "technology",
            "description",
            "summary",
            "details",
        ]

        # First, try to find priority fields
        for field in priority_fields:
            if field in item_dict and item_dict[field]:
                value = str(item_dict[field]).strip()
                if value:
                    # Add additional context if available
                    context_fields = [
                        "company",
                        "organization",
                        "technologies",
                        "duration",
                        "year",
                    ]
                    context = []
                    for ctx_field in context_fields:
                        if (
                            ctx_field in item_dict
                            and item_dict[ctx_field]
                            and ctx_field != field
                        ):
                            context.append(str(item_dict[ctx_field]))

                    if context:
                        return f"{value} ({', '.join(context)})"
                    return value

        # If no priority fields found, join all non-empty string values
        all_values = []
        for key, value in item_dict.items():
            if value and isinstance(value, (str, int, float)):
                text = str(value).strip()
                if text and text.lower() not in ["none", "null", "undefined"]:
                    all_values.append(text)

        return " - ".join(all_values) if all_values else ""
