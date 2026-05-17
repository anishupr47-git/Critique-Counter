# prefly: ignore [missing-import]
import textstat
from sklearn.feature_extraction.text import CountVectorizer

class ReadabilityProcessor:
    """Processes text to calculate readability metrics and provide feedback"""
    def process(self, text):
        if not text or len(text.strip())==0:
            return self._empty_result()
        
        #textstat
        try:
            return {
                'word_count':textstat.lexicon_count(text, removepunct=True),
                'sentence_count':textstat.sentence_count(text),
                'character_count':len(text.replace(" ", "")),
                'syllable_count':textstat.syllable_count(text),
                'grade_level':textstat.flesch_kincaid_grade(text),
                'reading_ease':textstat.flesch_reading_ease(text),
                'smog_index':textstat.smog_index(text),
                'coleman_liau_index':textstat.coleman_liau_index(text),
            }
        except Exception:
            return self._empty_result()
        
        def _empty_result(self):
            return {
                'word_count':0,
                'sentence_count':0,
                'character_count':0,
                'syllable_count':0,
                'grade_level':0.0,
                'reading_ease':0.0,
                'smog_index':0.0,
                'coleman_liau_index':0.0,
            }

class LexicalComplexityProcessor:
    """Analyzes text to determine vocabulary complexity and diversity"""
    def __init__(self):
        self.vectorizer = CountVectorizer(stop_words='english')

    def process(self, text, words):
        total_words = len(words)
        if total_words == 0:
            return {'vocab_complexity':0.0, 'lexical_diversity':0.0}
        
        unique_tokens = set([w.lower() for w in words])
        lexical_diversity = (len(unique_tokens) / total_words) * 100.0

        try:
            self.vectorizer.fit_transform([text])
            unique_high_tier_words = len(self.vectorizer.get_feature_names_out())
            vocab_complexity = (unique_high_tier_words / total_words) * 100.0
        
        except ValueError:
            vocab_complexity = 0.0

        return {
            'vocab_complexity': round(vocab_complexity, 2),
            'lexical_diversity': round(lexical_diversity, 2)
        }
    
class StylisticProcessor:
    """Analyzes text for stylistic elements like passive voice and sentence structure"""
    def process(self, readability_metrics):
        word_count = readability_metrics.get('word_count', 0)
        sentence_count = readability_metrics.get('sentence_count', 0)
        character_count = readability_metrics.get('character_count', 0)

        avg_sentence_length = (word_count / sentence_count) if sentence_count > 0 else 0.0
        avg_word_length = (character_count / word_count) if word_count > 0 else 0.0

        return {
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            
        }


        