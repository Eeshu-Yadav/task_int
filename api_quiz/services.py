from google import genai
from django.db import models
from django.conf import settings
from .models import QuizTemplate, QuizQuestion, Couple, ChatKeyword, RelationshipAssessment
import re
import json
from collections import defaultdict
from .text_processing import TextProcessor
from jsonschema import validate
from django.core.exceptions import ValidationError
from django.db.models import F,Q
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

EMOTION_MAP = {
    # Conflict & tension
    'fight': {
        'tone': 'reconciliation',
        'lead_in': "I know sometimes couples argue. Let’s turn that energy into warm reminders of why you love each other:\n"
    },
    'argue': {
        'tone': 'reconciliation',
        'lead_in': "Arguments happen—here are questions to help you reconnect and laugh again:\n"
    },
    'disagreement': {
        'tone': 'reconciliation',
        'lead_in': "Disagreements come and go. Let’s pivot to the good times with these prompts:\n"
    },
    # Sadness & low mood
    'sad': {
        'tone': 'comfort',
        'lead_in': "Feeling down? These questions will bring back your brightest moments:\n"
    },
    'upset': {
        'tone': 'comfort',
        'lead_in': "When one of you is upset, small joys can help heal. Try these prompts:\n"
    },
    'lonely': {
        'tone': 'comfort',
        'lead_in': "Loneliness can creep in. These questions remind you you’re in this together:\n"
    },
    # Anger & frustration
    'angry': {
        'tone': 'calm',
        'lead_in': "Anger can be intense. Let’s cool down with questions that spark empathy:\n"
    },
    'frustrated': {
        'tone': 'calm',
        'lead_in': "Frustration builds walls. These prompts will help you find the door back to each other:\n"
    },
    # Boredom & routine
    'bored': {
        'tone': 'excite',
        'lead_in': "Feeling stuck in a rut? Shake things up with these fun, fresh questions:\n"
    },
    'routine': {
        'tone': 'excite',
        'lead_in': "Routines are comforting but can be stale. Let’s spark new energy with these prompts:\n"
    },
    # Jealousy & insecurity
    'jealous': {
        'tone': 'reassurance',
        'lead_in': "Jealousy can sting. These questions will remind you of the trust you share:\n"
    },
    'insecure': {
        'tone': 'reassurance',
        'lead_in': "Insecurity can weigh you down. Let’s build each other up with these prompts:\n"
    },
    # Gratitude & warmth
    'grateful': {
        'tone': 'celebrate',
        'lead_in': "Gratitude lights up hearts. Reflect on your blessings together with these prompts:\n"
    },
    'thankful': {
        'tone': 'celebrate',
        'lead_in': "Thankfulness deepens bonds. Here are questions to share your appreciation:\n"
    },
    # Excitement & passion
    'excited': {
        'tone': 'energize',
        'lead_in': "Excitement is contagious! Fuel your passion with these playful prompts:\n"
    },
    'passion': {
        'tone': 'energize',
        'lead_in': "Let’s turn up the heat—here are questions that spark intimacy and fun:\n"
    },
    # Nostalgia & memories
    'memory': {
        'tone': 'nostalgic',
        'lead_in': "Let’s take a trip down memory lane with these reflective prompts:\n"
    },
    'nostalgia': {
        'tone': 'nostalgic',
        'lead_in': "Nostalgia warms the heart. Recall your best moments with these questions:\n"
    },
    # Stress & relief
    'stress': {
        'tone': 'soothe',
        'lead_in': "Stress can build walls. These gentle prompts will help you unwind together:\n"
    },
    'anxious': {
        'tone': 'soothe',
        'lead_in': "Anxiety can be overwhelming. Find calm together with these soothing questions:\n"
    },
    # Missing & longing
    'miss': {
        'tone': 'longing',
        'lead_in': "Missing each other’s presence? These prompts will bring you close in spirit:\n"
    },
    'longing': {
        'tone': 'longing',
        'lead_in': "Longing can feel heavy. Let’s bridge the distance with these heartfelt prompts:\n"
    }
}

def jaccard_similarity(a, b):
    sa, sb = set(a), set(b)
    return (len(sa & sb) / len(sa | sb)) if sa or sb else 0.0


class KeywordManager:
    # @staticmethod
    # def update_keywords(couple_id, text):
    #     """Handle keyword extraction and storage with proper error handling"""
    #     try:
    #         phrases = TextProcessor.extract_phrases(text)
    #         logger.debug(f"Extracted phrases for couple {couple_id}: {phrases}")

    #         # Process all phrase types with validation
    #         for phrase_type in ['words', 'bigrams', 'trigrams']:
    #             for item in phrases.get(phrase_type, []):
    #                 if not isinstance(item, tuple) or len(item) != 2:
    #                     logger.warning(f"Invalid phrase item: {item}")
    #                     continue

    #                 phrase, freq = item
    #                 is_phrase = phrase_type in ['bigrams', 'trigrams']

    #                 try:
    #                     obj, created = ChatKeyword.objects.get_or_create(
    #                         couple_id=couple_id,
    #                         keyword=phrase,
    #                         defaults={'frequency': freq, 'is_phrase': is_phrase}
    #                     )
                        
    #                     if not created:
    #                         obj.frequency = F('frequency') + freq
    #                         obj.save(update_fields=['frequency'])
                            
    #                 except Exception as e:
    #                     logger.error(f"Failed to process {phrase_type} '{phrase}': {str(e)}")

    #         logger.info(f"Successfully updated keywords for couple {couple_id}")
            
    #     except Exception as e:
    #         logger.error(f"Keyword update failed: {str(e)}")
    #         raise

    # @staticmethod
    # def update_keywords(couple_id, text):
    #     """Enhanced keyword processing with phrase prioritization"""
    #     try:
    #         phrases = TextProcessor.extract_phrases(text)
            
    #         # Filter and weight phrases
    #         processed = []
    #         for phrase_type in ['trigrams', 'bigrams', 'words']:
    #             for phrase, freq in phrases.get(phrase_type, []):
    #                 # Add type-based weights
    #                 weight = {
    #                     'trigrams': 3,
    #                     'bigrams': 2,
    #                     'words': 1
    #                 }[phrase_type]
                    
    #                 # Filter meaningless phrases
    #                 if TextProcessor.is_meaningful(phrase):
    #                     processed.append((phrase, freq * weight))
            
    #         # Update database with weighted frequencies
    #         for phrase, weighted_freq in processed:
    #             obj, created = ChatKeyword.objects.update_or_create(
    #                 couple_id=couple_id,
    #                 keyword=phrase,
    #                 defaults={'frequency': weighted_freq}
    #             )
    #             if not created:
    #                 obj.frequency = F('frequency') + weighted_freq
    #                 obj.save(update_fields=['frequency'])
    #         logger.info(f"Updated keywords for couple {couple_id}")
    #     except Exception as e:
    #         logger.error(f"Keyword update failed: {str(e)}")
    #         raise
        
    @staticmethod
    # def update_keywords(couple_id, text):
    #     """Extract, filter, de-overlap top phrases, then upsert frequencies."""
    #     try:
    #         # 1) Extract raw phrases
    #         phrases = TextProcessor.extract_phrases(text)
    #         processed = []
    #         for phrase_type in ('trigrams', 'bigrams', 'words'):
    #             weight = {'trigrams':3, 'bigrams':2, 'words':1}[phrase_type]
    #             for phrase, freq in phrases.get(phrase_type, []):
    #                 if TextProcessor.is_meaningful(phrase):
    #                     processed.append((phrase, freq * weight))

    #         # 2) Sort by (score, length) descending
    #         processed.sort(key=lambda x: (x[1], len(x[0].split())), reverse=True)

    #         # 3) Pick top-10, skipping overlaps
    #         selected = []
    #         for phrase, score in processed:
    #             # skip if phrase is substring of any already selected, or vice versa
    #             if any(phrase in s or s in phrase for s in selected):
    #                 continue
    #             selected.append(phrase)
    #             if len(selected) >= 10:
    #                 break

    #         logger.debug(f"Final keywords for couple {couple_id}: {selected}")

    #         # 4) Upsert into ChatKeyword table
    #         for kw in selected:
    #             # weight based on original list
    #             freq = next(s for p, s in processed if p == kw)
    #             obj, created = ChatKeyword.objects.get_or_create(
    #                 couple_id=couple_id,
    #                 keyword=kw,
    #                 defaults={'frequency': freq, 'is_phrase': ' ' in kw}
    #             )
    #             if not created:
    #                 obj.frequency = F('frequency') + freq
    #                 obj.save(update_fields=['frequency'])

    #         logger.info(f"Updated keywords for couple {couple_id}: {selected}")

    #     except Exception as e:
    #         logger.error(f"Keyword update failed: {e}")
    #         raise

    def update_keywords(couple_id, text):
        """Extract only general keywords (unigrams) to avoid over-personalization"""
        try:
            # 1) Extract raw words only
            phrases = TextProcessor.extract_phrases(text)
            # Keep only unigrams for general personalization
            processed = [
                (word, freq) for word, freq in phrases.get('words', [])
                if TextProcessor.is_meaningful(word)
            ]

            # 2) Sort by frequency descending
            processed.sort(key=lambda x: x[1], reverse=True)

            # 3) Pick top-N unigrams
            selected = [phrase for phrase, _ in processed[:10]]
            logger.debug(f"General keywords for couple {couple_id}: {selected}")

            # 4) Upsert into ChatKeyword table
            for kw in selected:
                freq = next((f for p, f in processed if p == kw), 1)
                obj, created = ChatKeyword.objects.get_or_create(
                    couple_id=couple_id,
                    keyword=kw,
                    defaults={'frequency': freq, 'is_phrase': False}
                )
                if not created:
                    obj.frequency = F('frequency') + freq
                    obj.save(update_fields=['frequency'])

            logger.info(f"Updated general keywords for couple {couple_id}: {selected}")
        except Exception as e:
            logger.error(f"Keyword update failed: {e}")
            raise

    # @staticmethod
    # def get_top_keywords(couple_id, limit=10):
    #     """Retrieve top keywords with proper error handling"""
    #     try:
    #         raw = list(ChatKeyword.objects.filter(couple_id=couple_id)
    #                    .extra(select={'length': 'LENGTH(keyword)'})
    #                    .order_by('-frequency', '-length')[:limit]
    #                    .values_list('keyword', flat=True))
    #         logger.debug(f"Top keywords for couple {couple_id}: {raw}")
    #         return raw
    #     except Exception as e:
    #         logger.error(f"Keyword retrieval failed: {str(e)}")
    #         return []

    @staticmethod
    # def get_top_keywords(couple_id, limit=10):
    #     """Return the current top-10 keywords (after de-overlap) for this couple."""
    #     try:
    #         raw = list(
    #             ChatKeyword.objects
    #             .filter(couple_id=couple_id)
    #             .order_by('-frequency')[:limit]
    #             .values_list('keyword', flat=True)
    #         )
    #         logger.debug(f"Top keywords for couple {couple_id}: {raw}")
    #         return raw
    #     except Exception as e:
    #         logger.error(f"Keyword retrieval failed: {e}")
    #         return []

    @staticmethod
    def get_top_keywords(couple_id, limit=10):
        """Retrieve only unigrams for quiz generation"""
        try:
            raw = list(
                ChatKeyword.objects.filter(couple_id=couple_id)
                .order_by('-frequency')[:limit]
                .values_list('keyword', flat=True)
            )
            logger.debug(f"Top general keywords for couple {couple_id}: {raw}")
            return raw
        except Exception as e:
            logger.error(f"Keyword retrieval failed: {e}")
            return []



class QuizGenerator:
    THRESHOLD = 0.75
    LOOKBACK = 10
    # MIN_KEYWORDS = 5
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
                Q(couple_id=couple_id) | Q(source_keywords__overlap=keywords),
                template__template_type=template_type
            ).order_by('-created_at')[:10]
            if cross:
                logger.info(f"Cross-couple cache hit: QuizQuestion {cross.id}")
                return cross
            
            best_match = None
            highest_score = 0.0
            for candidate in cross:
                score = jaccard_similarity(keywords, candidate.source_keywords)
                if score > highest_score and score >= QuizGenerator.THRESHOLD:
                    highest_score = score
                    best_match = candidate

            return best_match if highest_score > 0 else None

        except Exception as e:
            logger.error(f"Cache lookup error: {str(e)}")
            return None


    # @staticmethod
    # def get_cached_questions(template_type, keywords, couple_id=None):
    #     """
    #     1) Try exact match for this couple.
    #     2) If none, try exact match across all couples.
    #     """
    #     qs = QuizQuestion.objects.filter(
    #         template__template_type=template_type,
    #         source_keywords=keywords
    #     ).order_by('-created_at')

    #     if couple_id is not None:
    #         couple_hit = qs.filter(couple_id=couple_id).first()
    #         if couple_hit:
    #             logger.info(f"Exact cache hit for couple {couple_id}: QuizQuestion {couple_hit.id}")
    #             return couple_hit

    #     global_hit = qs.first()
    #     if global_hit:
    #         logger.info(f"Global cache hit: QuizQuestion {global_hit.id}")
    #         return global_hit

    #     return None

    @staticmethod
    def should_force_refresh(couple_id, keywords):
        try:
            last_quiz = QuizQuestion.objects.filter(
                couple_id=couple_id
            ).order_by('-created_at').first()
            
            if not last_quiz:
                return True
                
            new_keywords = set(keywords) - set(last_quiz.source_keywords)
            # return len(new_keywords) >= QuizGenerator.MIN_KEYWORDS
            return len(new_keywords) > 0
            
        except Exception as e:
            logger.error(f"Force refresh check failed: {str(e)}")
            return True

    @staticmethod
    def force_new_generation(couple_id, template_type, keywords, count=5):
        try:
            template = QuizTemplate.objects.get(template_type=template_type)
            prompt = f"""
            Generate FRESH questions about these NEW topics:
            {', '.join(keywords)}
            
            Avoid repeating previous themes. Focus on specific details.
            Include references to: {', '.join(keywords[:3])}
            
            Template requirements:
            {template.system_prompt}
            
            Required JSON format:
            {json.dumps(template.example_json, indent=2)}
            """

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts": [{"text": prompt}]}],
                # generation_config={"temperature": 0.8}
            )

            if not response.candidates:
                raise ValueError("Empty Gemini response")

            json_str = re.sub(r'[^\{]*({.*})[^\}]*', r'\1', response.text, flags=re.DOTALL)
            data = json.loads(json_str.strip())
            validate(data, TEMPLATE_SCHEMAS[template_type])

            return QuizQuestion.objects.create(
                couple_id=couple_id,
                template=template,
                question_data=data,
                source_keywords=keywords
            )

        except Exception as e:
            logger.error(f"Forced generation failed: {str(e)}")
            return None


    @staticmethod
    def generate_quiz(couple_id, template_type=None, count=5):
        """Generate or retrieve cached quiz questions"""
        try:
            raw_keywords = KeywordManager.get_top_keywords(couple_id)
            if not raw_keywords:
                raise ValueError("No keywords found for this couple")
            keywords = sorted(set(raw_keywords))

            # 1a) Detect dominant emotion
            lead_in = ""
            for kw in keywords:
                # emo = EMOTION_MAP.get(kw.lower())
                # if emo:
                #     lead_in = emo['lead_in']
                #     break
                if kw.lower() in EMOTION_MAP:
                    lead_in = EMOTION_MAP[kw.lower()]['lead_in']
                    break
            


            logger.debug(f"Canonical keywords for couple {couple_id}: {keywords}")
            if not keywords:
                raise ValueError("No keywords found for this couple")
            #2. Select template
            if not template_type:
                template_type = QuizGenerator.select_template(keywords)
                logger.info(f"Auto-selected template: {template_type}")
            
            if QuizGenerator.should_force_refresh(couple_id, keywords):
                logger.info("Forcing new generation due to significant changes")
                return QuizGenerator.force_new_generation(couple_id, template_type, keywords, count)

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
            # prompt = f"""
            # Generate engaging couple questions based on these conversation themes:
            # {', '.join(keywords)}
            
            # {template.system_prompt}
            
            # Important guidelines:
            # 1. Make questions personal and relationship-focused
            # 2. Ensure variety in question topics
            # 3. Keep language warm and inviting
            # 4. Use the exact JSON format below:
            
            # {json.dumps(template.example_json, indent=2)}
            # """


            themes = ', '.join(keywords)
            if lead_in:
                prompt = f"{lead_in}"
            else:
                prompt = f"Let’s explore these themes:\n"

            prompt += f"{themes}\n\n{template.system_prompt}\n\nUse this JSON format:\n{json.dumps(template.example_json)}"

            
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
    
    @staticmethod
    def assess_relationship(couple_id, payload):
        try:
            couple = Couple.objects.get(id=couple_id)
            # 1) Build LLM prompt
            questions = payload['answers']
            # Describe the seven factors and the 5-stage model:
            intro = """
You are a relationship coach. Given the couple's answers below,
assign:
  • One of the five relationship states (Honeymoon, Exploration, Adaptation, Commitment, Acceptance)
  • A 1–10 score for each health factor:
      1. Open communication
      2. Trust
      3. Individuality
      4. Curiosity
      5. Time apart
      6. Playfulness
      7. Physical intimacy

Respond ONLY with JSON like:
{
  "state": "Commitment",
  "scores": {
    "open_communication": 8,
    "trust": 9,
    "individuality": 7,
    "curiosity": 6,
    "time_apart": 5,
    "playfulness": 8,
    "physical_intimacy": 7
  }
}
"""
            # Append each Q&A:
            body = "\n".join(
                f"Q: {qa['question_text']}\nA: {qa['answer']}"
                for qa in questions
            )

            prompt = intro + "\n\n" + body

            # 2) Call Gemini
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"parts":[{"text": prompt}]}]
            )
            # text = response.candidates[0].text
            text = response.text

            # 3) Extract JSON
            import re, json
            json_str = re.sub(r'^[^{]*({.*})[^}]*$', r'\1', text, flags=re.DOTALL)
            result = json.loads(json_str)

            print(result)

            # 4) Save to DB
            return RelationshipAssessment.objects.create(
                couple_id=couple_id,
                state=result['state'],
                open_communication=result['scores']['open_communication'],
                trust=result['scores']['trust'],
                individuality=result['scores']['individuality'],
                curiosity=result['scores']['curiosity'],
                time_apart=result['scores']['time_apart'],
                playfulness=result['scores']['playfulness'],
                physical_intimacy=result['scores']['physical_intimacy'],
            )
        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            return None