# services.py
from google import genai
from django.conf import settings
from .models import QuizTemplate, QuizQuestion, Couple, ChatKeyword
import re
import json
from jsonschema import validate
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

TEMPLATE_SCHEMAS = {
    'MCQ': {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}},
                        "correct_answer": {"type": "string"}
                    },
                    "required": ["question_text", "options", "correct_answer"]
                }
            }
        }
    },
    'SLIDER': {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "min_label": {"type": "string"},
                        "max_label": {"type": "string"}
                    },
                    "required": ["question_text", "min_label", "max_label"]
                }
            }
        }
    },
    'BINARY': {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"}
                    },
                    "required": ["question_text"]
                }
            }
        }
    },
    'SHORT': {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "placeholder": {"type": "string"}
                    },
                    "required": ["question_text"]
                }
            }
        }
    }
}

class QuizGenerator:
    @staticmethod
    def get_keywords(couple_id, limit=5):
        return list(ChatKeyword.objects.filter(couple_id=couple_id)
               .order_by('-frequency')[:limit].values_list('keyword', flat=True))

    @staticmethod
    def get_cached_questions(couple_id, template_type, keywords):
        """Check for existing questions matching ALL keywords"""
        keyword_str = ','.join(sorted(keywords))
        try:
            return QuizQuestion.objects.filter(
                couple_id=couple_id,
                template__template_type=template_type,
                keywords=keyword_str
            ).order_by('-created_at').first()
        except Exception as e:
            print(f"Cache lookup error: {str(e)}")
            return None

    @staticmethod
    def generate_quiz(couple_id, template_type, count=5):

        try:
            keywords = QuizGenerator.get_keywords(couple_id)
            if not keywords:
                raise ValueError("No keywords found for this couple")
            
            keyword_str = ','.join(sorted(keywords))
            cached = QuizGenerator.get_cached_questions(couple_id, template_type, keywords)
            if cached:
                print("✅ Returning cached questions")
                return cached
            
            print(f"⚡ Generating new questions for keywords: {keywords}")

            template = QuizTemplate.objects.filter(template_type=template_type).first()
            if not template:
                raise ValueError(f"Template {template_type} not found")
            
            prompt = f"""
            {template.system_prompt}
            Keywords: {', '.join(keywords)}
            Generate exactly {count} questions in this JSON format:
            {json.dumps(template.example_json)}
            """
        
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts": [{"text": prompt}]}]
            )
        
            if not response.candidates:
                raise ValueError("Empty response from Gemini API")
            
            json_str = re.sub(r'[^\{]*({.*})[^\}]*', r'\1', response.text, flags=re.DOTALL)
            data = json.loads(json_str.strip())
            
            validate(data, TEMPLATE_SCHEMAS[template_type])
        
            return QuizQuestion.objects.create(
                couple_id=couple_id,
                template=template,
                question_data=data,
                keywords=keyword_str
            )
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except ValidationError as e:
            print(f"Schema validation error: {str(e)}")
            return None
        except Exception as e:
            print(f"Quiz generation error: {str(e)}")
            return None