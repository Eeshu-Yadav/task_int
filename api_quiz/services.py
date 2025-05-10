from google import genai
from django.db import models
from django.conf import settings
from .models import QuizTemplate, QuizQuestion, Couple, ChatKeyword
import re
import json
from collections import defaultdict
from .text_processing import TextProcessor
from jsonschema import validate
from django.core.exceptions import ValidationError
from django.db.models import F
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

def jaccard_similarity(a, b):
    sa, sb = set(a), set(b)
    return (len(sa & sb) / len(sa | sb)) if sa or sb else 0.0


class KeywordManager:
    @staticmethod
    def update_keywords(couple_id, text):
        """Handle keyword extraction and storage with proper error handling"""
        try:
            phrases = TextProcessor.extract_phrases(text)
            logger.debug(f"Extracted phrases for couple {couple_id}: {phrases}")

            # Process all phrase types with validation
            for phrase_type in ['words', 'bigrams', 'trigrams']:
                for item in phrases.get(phrase_type, []):
                    if not isinstance(item, tuple) or len(item) != 2:
                        logger.warning(f"Invalid phrase item: {item}")
                        continue

                    phrase, freq = item
                    is_phrase = phrase_type in ['bigrams', 'trigrams']

                    try:
                        obj, created = ChatKeyword.objects.get_or_create(
                            couple_id=couple_id,
                            keyword=phrase,
                            defaults={'frequency': freq, 'is_phrase': is_phrase}
                        )
                        
                        if not created:
                            obj.frequency = F('frequency') + freq
                            obj.save(update_fields=['frequency'])
                            
                    except Exception as e:
                        logger.error(f"Failed to process {phrase_type} '{phrase}': {str(e)}")

            logger.info(f"Successfully updated keywords for couple {couple_id}")
            
        except Exception as e:
            logger.error(f"Keyword update failed: {str(e)}")
            raise

    @staticmethod
    def get_top_keywords(couple_id, limit=10):
        """Retrieve top keywords with proper error handling"""
        try:
            raw = list(ChatKeyword.objects.filter(couple_id=couple_id)
                       .order_by('-frequency')[:limit]
                       .values_list('keyword', flat=True))
            logger.debug(f"Top keywords for couple {couple_id}: {raw}")
            return raw
        except Exception as e:
            logger.error(f"Keyword retrieval failed: {str(e)}")
            return []



class QuizGenerator:
    THRESHOLD = 0.6       # Jaccard similarity threshold for cache reuse
    LOOKBACK = 20
    MAX_NOVELTY = 0.3
    TEMPLATE_MAPPING = {
        'MCQ': ['favorite', 'remember', 'know', 'prefer', 'love'],
        'SLIDER': ['feel', 'happy', 'satisfied', 'communicate', 'trust'],
        'BINARY': ['likely', 'would', 'rather', 'better at', 'more'],
        'SHORT': ['first', 'best', 'memory', 'moment', 'story'],
        'ACTION': ['try', 'practice', 'exercise', 'together', 'touch']
    }

    @staticmethod
    def select_template(keywords):
        """Automatically select the most relevant template"""
        triggers_map = QuizGenerator.TEMPLATE_MAPPING
        scores = defaultdict(int)
        for template, triggers in triggers_map.items():
            for kw in keywords:
                if any(t in kw.lower() for t in triggers):
                    scores[template] += 1
        chosen = max(scores, key=scores.get) if scores else 'MCQ'
        logger.debug(f"Selected template '{chosen}' for keywords {keywords}")
        return chosen

    
    @staticmethod
    def get_cached_questions(couple_id, template_type, keywords):
        logger.debug(f"Attempting exact cache lookup for couple={couple_id}, template={template_type}, keywords={keywords}")
        """Find cached questions matching all keywords"""
        try:
            # sorted_kw = sorted(keywords)
            exact = QuizQuestion.objects.filter(
                couple_id=couple_id,
                template__template_type=template_type,
                source_keywords=keywords
            ).order_by('-created_at').first()
            if exact:
                logger.info(f"Exact cache hit: QuizQuestion {exact.id}")
                return exact
            
            # Next, try cross-couple lookup for same keywords
            cross = QuizQuestion.objects.filter(
                template__template_type=template_type,
                source_keywords=keywords
            ).order_by('-created_at').first()
            if cross:
                logger.info(f"Cross-couple cache hit: QuizQuestion {cross.id}")
                return cross
            
        except Exception as e:
            logger.error(f"Cache lookup failed: {str(e)}")
            return None

    @staticmethod
    def generate_quiz(couple_id, template_type=None, count=5):
        """Generate or retrieve cached quiz questions"""
        try:
            raw_keywords = KeywordManager.get_top_keywords(couple_id)
            if not raw_keywords:
                raise ValueError("No keywords found for this couple")
            keywords = sorted(set(raw_keywords))
            
            logger.debug(f"Canonical keywords for couple {couple_id}: {keywords}")
            if not keywords:
                raise ValueError("No keywords found for this couple")
            #2. Select template
            if not template_type:
                template_type = QuizGenerator.select_template(keywords)
                logger.info(f"Auto-selected template: {template_type}")
            
            #3. Exact cache lookup
            exact = QuizGenerator.get_cached_questions(couple_id, template_type, keywords)
            if exact:
                logger.info(f"Returning cached questions (ID: {exact.id})")
                return exact
            

            # 4. Fuzzy cache lookup
            logger.debug(f"Starting fuzzy lookup over last {QuizGenerator.LOOKBACK} quizzes")
            candidates = QuizQuestion.objects.filter(
                couple_id=couple_id,
                template__template_type=template_type
            ).order_by('-created_at')[:QuizGenerator.LOOKBACK]

            best, best_score = None, 0.0
            for quiz in candidates:
                score = jaccard_similarity(keywords, quiz.source_keywords)
                if score > best_score:
                    best_score, best = score, quiz

            if best and best_score >= QuizGenerator.THRESHOLD:
                old_set = set(best.source_keywords)
                new_set = set(keywords)
                novelty_ratio = len(new_set - old_set) / len(new_set)
                if novelty_ratio <= QuizGenerator.MAX_NOVELTY:
                    logger.info(f"Reusing quiz {best.id} (overlap={best_score:.2f}, novelty={novelty_ratio:.2f})")
                    return best
                else:
                    logger.info(
                        f"Skipping reuse despite good overlap; "
                        f"novelty too high ({novelty_ratio:.2f})"
                    )


            
            logger.info(f"Generating new {template_type} quiz for keywords: {keywords}")
            
            template = QuizTemplate.objects.filter(template_type=template_type).first()
            if not template:
                raise ValueError(f"Template {template_type} not found")
            
            # Build context-aware prompt
            prompt = f"""
            Generate engaging couple questions based on these conversation themes:
            {', '.join(keywords)}
            
            {template.system_prompt}
            
            Important guidelines:
            1. Make questions personal and relationship-focused
            2. Ensure variety in question topics
            3. Keep language warm and inviting
            4. Use the exact JSON format below:
            
            {json.dumps(template.example_json, indent=2)}
            """
            
            # Call Gemini API
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts": [{"text": prompt}]}],
                # generation_config={
                #     "temperature": 0.7,
                #     "top_p": 0.9,
                #     "max_output_tokens": 2000
                # }
                # temperature=0.7
            )
            
            if not response.candidates:
                raise ValueError("Empty response from Gemini API")
            
            # Clean and parse response
            json_str = re.sub(r'[^\{]*({.*})[^\}]*', r'\1', response.text, flags=re.DOTALL)
            data = json.loads(json_str.strip())
            
            # Validate schema
            validate(data, TEMPLATE_SCHEMAS[template_type])
            
            # Create and return new quiz
            new_quiz = QuizQuestion.objects.create(
                couple_id=couple_id,
                template=template,
                question_data=data,
                # keywords=','.join(sorted(keywords)),
                source_keywords=keywords
            )
            logger.info(f"Created new quiz: {new_quiz.id}")
            return new_quiz
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return None
        except ValidationError as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Quiz generation failed: {str(e)}")
            return None