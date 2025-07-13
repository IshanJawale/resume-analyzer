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
        Normalize a field to ensure it's a proper list of strings
        """
        if value is None:
            return []

        if isinstance(value, list):
            # Flatten any nested structures and convert to strings
            normalized = []
            for item in value:
                if isinstance(item, dict):
                    # If it's a dict, try to extract meaningful text
                    if "name" in item:
                        normalized.append(str(item["name"]))
                    elif "title" in item:
                        normalized.append(str(item["title"]))
                    else:
                        # Join all string values from the dict
                        normalized.append(" ".join(str(v) for v in item.values() if v))
                elif isinstance(item, str):
                    normalized.append(item)
                else:
                    normalized.append(str(item))
            return normalized

        if isinstance(value, dict):
            # If it's a dict, extract all string values
            all_values = []
            for v in value.values():
                if isinstance(v, list):
                    all_values.extend(str(item) for item in v if item)
                elif v:
                    all_values.append(str(v))
            return all_values

        if isinstance(value, str):
            return [value] if value else []

        return [str(value)] if value else []
