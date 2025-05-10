import nltk
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from collections import Counter

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

class TextProcessor:
    @staticmethod
    def extract_phrases(text, top_n=15):
        tokens = nltk.word_tokenize(text.lower())
        pos_tags = nltk.pos_tag(tokens)
        
        words = [
            word for word, pos in pos_tags 
            if pos.startswith('NN') or pos.startswith('JJ')
        ]
        word_counts = Counter(words).most_common(top_n)
        
        # Bigrams (2-word phrases)
        bigram_finder = BigramCollocationFinder.from_words(tokens)
        bigrams = [' '.join(b) for b in bigram_finder.nbest(BigramAssocMeasures.pmi, top_n)]
        bigram_counts = Counter(bigrams).most_common(top_n)
        

        trigram_finder = TrigramCollocationFinder.from_words(tokens)
        trigrams = [' '.join(t) for t in trigram_finder.nbest(TrigramAssocMeasures.pmi, top_n//2)]
        trigram_counts = Counter(trigrams).most_common(top_n//2)
        
        return {
            'words': word_counts,
            'bigrams': bigram_counts,
            'trigrams': trigram_counts
        }