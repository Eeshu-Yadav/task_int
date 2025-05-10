from django.core.management.base import BaseCommand
from api_quiz.models import QuizTemplate

TEMPLATES = [
    {
        'name': 'Love Knowledge Quiz',
        'template_type': 'MCQ',
        'system_prompt': """Generate 5 intimate multiple-choice questions about a couple's relationship. Each question should:
1. Focus on personal preferences, memories, or relationship dynamics
2. Include 4 plausible options (1 correct, 3 incorrect)
3. Be playful yet meaningful
4. Avoid sensitive topics

Example format for each question:
{
    "question_text": "What was your partner's first impression of you?",
    "options": [
        "Thought you were funny but loud",
        "Found you mysterious and intriguing",
        "Was intimidated by your confidence",
        "Immediately felt comfortable with you"
    ],
    "correct_answer": "Thought you were funny but loud",
    "explanation": "This reveals how well you remember early relationship moments"
}""",
        'example_json': {
            "questions": [{
                "question_text": "What's your partner's love language?",
                "options": [
                    "Physical touch",
                    "Words of affirmation",
                    "Acts of service",
                    "Quality time"
                ],
                "correct_answer": "Physical touch",
                "explanation": "Understanding love languages improves connection"
            }]
        }
    },
    {
        'name': 'Relationship Wellness Check',
        'template_type': 'SLIDER',
        'system_prompt': """Create 5 reflective relationship assessment questions using 0-10 scales. Each should:
1. Measure emotional connection or relationship health
2. Have meaningful endpoint labels
3. Encourage positive reflection
4. Include interpretation guidance

Example format:
{
    "question_text": "How fulfilled do you feel in your relationship?",
    "min_label": "Needs work",
    "max_label": "Completely fulfilled",
    "interpretation": "Scores below 5 may indicate areas needing attention"
}""",
        'example_json': {
            "questions": [{
                "question_text": "How emotionally safe do you feel sharing your thoughts?",
                "min_label": "Rarely comfortable",
                "max_label": "Always safe",
                "interpretation": "Emotional safety is foundation for intimacy"
            }]
        }
    },
    {
        'name': 'Couple Personality Showdown',
        'template_type': 'BINARY',
        'system_prompt': """Generate 10 fun "Which Partner..." questions highlighting personality differences. Each should:
1. Be lighthearted but revealing
2. Offer binary choices (Me/Partner)
3. Include a playful follow-up suggestion
4. Avoid serious conflicts

Example format:
{
    "question_text": "Who's more likely to initiate cuddling?",
    "follow_up": "The less cuddly partner owes 5 minutes of snuggles!"
}""",
        'example_json': {
            "questions": [{
                "question_text": "Who's more likely to suggest trying new things in bed?",
                "follow_up": "The other partner gets to pick one new thing to try this week!"
            }]
        }
    },
    {
        'name': 'Memory Lane Journal',
        'template_type': 'SHORT',
        'system_prompt': """Create 5 reflective writing prompts about relationship milestones and feelings. Each should:
1. Invite personal storytelling
2. Focus on positive memories
3. Include an example response
4. Encourage emotional vulnerability

Example format:
{
    "question_text": "Describe the moment you first realized you were in love",
    "placeholder": "Share details about where you were, what you felt...",
    "example_response": "We were cooking together when..."
}""",
        'example_json': {
            "questions": [{
                "question_text": "What's your favorite inside joke and how did it start?",
                "placeholder": "Describe the funny moment that created this special bond",
                "example_response": "That time at the beach when we..."
            }]
        }
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for t in TEMPLATES:
            QuizTemplate.objects.update_or_create(
                template_type=t['template_type'],
                defaults=t
            )