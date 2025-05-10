import re
import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from collections import Counter

class TextProcessor:
    MEANINGFUL_POS = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'VBG', 'VBN'}
    STOP_WORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'we'}
    
    @staticmethod
    def extract_phrases(text, top_n=15):
        """Enhanced phrase extraction with POS filtering and cleanup"""
        
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        tokens = nltk.word_tokenize(cleaned)
        pos_tags = nltk.pos_tag(tokens)
        
        words = [
            word for word, pos in pos_tags 
            if pos[:2] in TextProcessor.MEANINGFUL_POS
            and word not in TextProcessor.STOP_WORDS
        ]
        word_counts = Counter(words).most_common(top_n)
        
        bigrams, trigrams = [], []
        if len(tokens) >= 2:
            bigram_finder = BigramCollocationFinder.from_words(tokens)
            bigrams = [
                ' '.join(b) for b in bigram_finder.nbest(BigramAssocMeasures.pmi, top_n)
                if TextProcessor.is_meaningful(' '.join(b))
            ]

        if len(tokens) >= 3:
            trigram_finder = TrigramCollocationFinder.from_words(tokens)
            trigrams = [
                ' '.join(t) for t in trigram_finder.nbest(TrigramAssocMeasures.pmi, top_n//2)
                if TextProcessor.is_meaningful(' '.join(t))
            ]

        return {
            'words': word_counts,
            'bigrams': Counter(bigrams).most_common(top_n),
            'trigrams': Counter(trigrams).most_common(top_n//2)
        }

    @staticmethod
    def is_meaningful(phrase):
        """Improved phrase validation with multiple checks"""
        if len(phrase) < 4:
            return False
            
        if any(sw in phrase.split() for sw in TextProcessor.STOP_WORDS):
            return False
            
        tags = [pos[:2] for _, pos in nltk.pos_tag(nltk.word_tokenize(phrase))]
        if tags[0] not in {'NN', 'JJ'} or tags[-1] not in {'NN', 'JJ'}:
            return False
            
        return True