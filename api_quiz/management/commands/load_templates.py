# from django.core.management.base import BaseCommand
# from api_quiz.models import QuizTemplate

# TEMPLATES = [
#     {
#         'name': 'Love Knowledge Quiz',
#         'template_type': 'MCQ',
#         'system_prompt': """Generate 5 intimate multiple-choice questions about a couple's relationship. Each question should:
# 1. Focus on personal preferences, memories, or relationship dynamics
# 2. Include 4 plausible options (1 correct, 3 incorrect)
# 3. Be playful yet meaningful
# 4. Avoid sensitive topics

# Example format for each question:
# {
#     "question_text": "What was your partner's first impression of you?",
#     "options": [
#         "Thought you were funny but loud",
#         "Found you mysterious and intriguing",
#         "Was intimidated by your confidence",
#         "Immediately felt comfortable with you"
#     ],
#     "correct_answer": "Thought you were funny but loud",
#     "explanation": "This reveals how well you remember early relationship moments"
# }""",
#         'example_json': {
#             "questions": [{
#                 "question_text": "What's your partner's love language?",
#                 "options": [
#                     "Physical touch",
#                     "Words of affirmation",
#                     "Acts of service",
#                     "Quality time"
#                 ],
#                 "correct_answer": "Physical touch",
#                 "explanation": "Understanding love languages improves connection"
#             }]
#         }
#     },
#     {
#         'name': 'Relationship Wellness Check',
#         'template_type': 'SLIDER',
#         'system_prompt': """Create 5 reflective relationship assessment questions using 0-10 scales. Each should:
# 1. Measure emotional connection or relationship health
# 2. Have meaningful endpoint labels
# 3. Encourage positive reflection
# 4. Include interpretation guidance

# Example format:
# {
#     "question_text": "How fulfilled do you feel in your relationship?",
#     "min_label": "Needs work",
#     "max_label": "Completely fulfilled",
#     "interpretation": "Scores below 5 may indicate areas needing attention"
# }""",
#         'example_json': {
#             "questions": [{
#                 "question_text": "How emotionally safe do you feel sharing your thoughts?",
#                 "min_label": "Rarely comfortable",
#                 "max_label": "Always safe",
#                 "interpretation": "Emotional safety is foundation for intimacy"
#             }]
#         }
#     },
#     {
#         'name': 'Couple Personality Showdown',
#         'template_type': 'BINARY',
#         'system_prompt': """Generate 10 fun "Which Partner..." questions highlighting personality differences. Each should:
# 1. Be lighthearted but revealing
# 2. Offer binary choices (Me/Partner)
# 3. Include a playful follow-up suggestion
# 4. Avoid serious conflicts

# Example format:
# {
#     "question_text": "Who's more likely to initiate cuddling?",
#     "follow_up": "The less cuddly partner owes 5 minutes of snuggles!"
# }""",
#         'example_json': {
#             "questions": [{
#                 "question_text": "Who's more likely to suggest trying new things in bed?",
#                 "follow_up": "The other partner gets to pick one new thing to try this week!"
#             }]
#         }
#     },
#     {
#         'name': 'Memory Lane Journal',
#         'template_type': 'SHORT',
#         'system_prompt': """Create 5 reflective writing prompts about relationship milestones and feelings. Each should:
# 1. Invite personal storytelling
# 2. Focus on positive memories
# 3. Include an example response
# 4. Encourage emotional vulnerability

# Example format:
# {
#     "question_text": "Describe the moment you first realized you were in love",
#     "placeholder": "Share details about where you were, what you felt...",
#     "example_response": "We were cooking together when..."
# }""",
#         'example_json': {
#             "questions": [{
#                 "question_text": "What's your favorite inside joke and how did it start?",
#                 "placeholder": "Describe the funny moment that created this special bond",
#                 "example_response": "That time at the beach when we..."
#             }]
#         }
#     },
# ]


# class Command(BaseCommand):
#     help = 'Loads or updates quiz templates'
    
#     def handle(self, *args, **options):
#         for template in TEMPLATES:
#             QuizTemplate.objects.update_or_create(
#                 template_type=template['template_type'],
#                 defaults=template
#             )
#         self.stdout.write(self.style.SUCCESS('Successfully loaded templates'))


# from django.core.management.base import BaseCommand
# from api_quiz.models import QuizTemplate

# TEMPLATES = [
#     {
#         'name': 'Love Knowledge Quiz',
#         'template_type': 'MCQ',
#         'system_prompt': """
# Generate 5 intimate multiple-choice questions about a couple's relationship that feel fresh and conversational. Each question should:
# 1. Tap into shared experiences or lighthearted topics (e.g., favorite band, memorable date).
# 2. Offer four distinct, creative options—avoid parallel phrasing.
# 3. Include one clearly correct answer and three plausible-but-playful distractors.
# 4. End with a brief, warm explanation of why the correct answer matters.

# Example format:
# {
#     "question_text": "Which song always makes your partner sing along like nobody's watching?",
#     "options": [
#         "That 80s power ballad you danced to on your first date",
#         "Their quirky indie favorite they never admit to liking",
#         "The viral TikTok tune they know every dance move to",
#         "The classic love ballad that reminds them of you"
#     ],
#     "correct_answer": "The viral TikTok tune they know every dance move to",
#     "explanation": "This reveals their playful side and shared dance memories."
# }
# """,
#         'example_json': {
#             "questions": [{
#                 "question_text": "What quirky habit does your partner have when they’re excited?",
#                 "options": [
#                     "Tap their foot rapidly",
#                     "Speak in movie quotes",
#                     "Do a little happy dance",
#                     "Talk in rhymes for fun"
#                 ],
#                 "correct_answer": "Do a little happy dance",
#                 "explanation": "Captures their joyful energy and your shared laughter."
#             }]
#         }
#     },
#     {
#         'name': 'Relationship Wellness Check',
#         'template_type': 'SLIDER',
#         'system_prompt': """
# Create 5 reflective slider-scale questions (0–10) that encourage couples to check in on their connection. Each should:
# 1. Address universal relationship themes (e.g., communication, fun, support).
# 2. Use vivid endpoint labels (e.g., “Stone silent” vs. “Open book”).
# 3. Include a short interpretation tip to spark discussion.
# 4. Be framed in a friendly, non-judgmental tone.

# Example:
# {
#     "question_text": "On a scale from ‘Stone silent’ to ‘Open book’, how comfortable do you feel sharing worries?",
#     "min_label": "Stone silent",
#     "max_label": "Open book",
#     "interpretation": "Scores under 4 may suggest a need for more open conversations." 
# }
# """,
#         'example_json': {
#             "questions": [{
#                 "question_text": "Between ‘Cozy cocoon’ and ‘Social butterfly’, how connected do you feel in public?",
#                 "min_label": "Cozy cocoon",
#                 "max_label": "Social butterfly",
#                 "interpretation": "Helps identify comfort levels around public displays of affection."
#             }]
#         }
#     },
#     {
#         'name': 'Couple Personality Showdown',
#         'template_type': 'BINARY',
#         'system_prompt': """
# Generate 10 playful yes/no or this/that prompts that reveal personality quirks. Each should:
# 1. Feature fun scenarios (e.g., “Who’s more likely…?”).
# 2. Offer two contrasting choices with humorous follow-ups.
# 3. Avoid sensitive topics; keep it lighthearted.
# 4. End with a playful dare or reward suggestion.

# Example:
# {
#     "question_text": "Who’s more likely to start a spontaneous road trip at midnight?",
#     "follow_up": "The other partner owes them one epic playlist for the ride!"
# }
# """,
#         'example_json': {
#             "questions": [{
#                 "question_text": "Who would survive longest in a zombie apocalypse?",
#                 "follow_up": "Survivor picks the first snack for movie night!"
#             }]
#         }
#     },
#     {
#         'name': 'Memory Lane Journal',
#         'template_type': 'SHORT',
#         'system_prompt': """
# Craft 5 evocative short-answer prompts that invite storytelling about shared memories. Each should:
# 1. Focus on positive milestones or silly moments.
# 2. Provide a brief example response to guide tone.
# 3. Encourage vivid details (sights, sounds, feelings).
# 4. Be warm, nostalgic, and engaging.

# Example:
# {
#     "question_text": "Describe the funniest thing that happened on one of your early dates.",
#     "placeholder": "Recall the scene, the laughter, and how you felt.",
#     "example_response": "We both tried karaoke and ended up duetting 'Livin’ on a Prayer' off-key—but it was the best night."
# }
# """,
#         'example_json': {
#             "questions": [{
#                 "question_text": "What’s a small gesture your partner did that still makes you smile?",
#                 "placeholder": "Share the moment and why it touched you.",
#                 "example_response": "They left a sticky note saying 'You’re my sunshine' on my laptop." 
#             }]
#         }
#     },
# ]


# class Command(BaseCommand):
#     help = 'Loads or updates quiz templates'
    
#     def handle(self, *args, **options):
#         for template in TEMPLATES:
#             QuizTemplate.objects.update_or_create(
#                 template_type=template['template_type'],
#                 defaults=template
#             )
#         self.stdout.write(self.style.SUCCESS('Successfully loaded templates'))



from django.core.management.base import BaseCommand
from api_quiz.models import QuizTemplate

TEMPLATES = [
    {
        'name': 'Love Knowledge Quiz',
        'template_type': 'MCQ',
        'system_prompt': """
Generate 5 intimate multiple-choice questions about a couple's relationship in a friendly, chatty tone.
• Keep each question under 12 words.
• Provide 4 concise options, each under 6 words, clearly distinct.
• Use a natural, conversational style (like a friend asking).
• Avoid overly specific personal details.

Example:
{
  "question_text": "Which song makes you both dance most?",
  "options": ["That pop hit","Classic ballad","Indie favorite","Movie theme"],
  "correct_answer": "That pop hit",
  "explanation": "It’s your go-to dance tune together."
}
""",
        'example_json': {
            "questions": [{
                "question_text": "What snack do you share on movie night?",
                "options": ["Popcorn","Ice cream","Nachos","Chocolate"],
                "correct_answer": "Popcorn",
                "explanation": "Your cozy tradition together."
            }]
        }
    },
    {
        'name': 'Relationship Wellness Check',
        'template_type': 'SLIDER',
        'system_prompt': """
Create 5 quick slider questions (0–10) for couples check-ins.
• Questions under 10 words.
• Labels under 3 words each.
• Write conversationally, like "On a scale..."
• End with a short tip (<10 words).

Example:
{
  "question_text": "Comfort sharing ups and downs?",
  "min_label": "Shy",
  "max_label": "Open",
  "interpretation": "Low score may signal guarded chats."
}
""",
        'example_json': {
            "questions": [{
                "question_text": "Energy during date night?",
                "min_label": "Low",
                "max_label": "High",
                "interpretation": "Helps plan fun evenings."
            }]
        }
    },
    {
        'name': 'Couple Personality Showdown',
        'template_type': 'BINARY',
        'system_prompt': """
Generate 10 playful this-or-that prompts.
• Keep each question under 12 words.
• Use two very different options.
• Write casually, with a fun follow-up.

Example:
{
  "question_text": "Beach walk or mountain hike?",
  "follow_up": "Loser buys ice cream!"
}
""",
        'example_json': {
            "questions": [{
                "question_text": "Early bird or night owl?",
                "follow_up": "Night owl plans breakfast date!"
            }]
        }
    },
    {
        'name': 'Memory Lane Journal',
        'template_type': 'SHORT',
        'system_prompt': """
Write 5 short-answer prompts to spark memories.
• Questions under 10 words.
• Encourage vivid, personal stories.
• Provide a brief example response.

Example:
{
  "question_text": "Best laugh you shared?",
  "placeholder": "Describe the moment briefly...",
  "example_response": "We couldn’t stop giggling at karaoke."
}
""",
        'example_json': {
            "questions": [{
                "question_text": "First date highlight?",
                "placeholder": "Recall one detail...",
                "example_response": "Our picnic by the lake at sunset."
            }]
        }
    },
]

class Command(BaseCommand):
    help = 'Loads or updates quiz templates'
    
    def handle(self, *args, **options):
        for template in TEMPLATES:
            QuizTemplate.objects.update_or_create(
                template_type=template['template_type'],
                defaults=template
            )
        self.stdout.write(self.style.SUCCESS('Successfully loaded templates'))
