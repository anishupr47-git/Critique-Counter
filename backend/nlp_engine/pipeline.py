import spacy
import spacy.cli
from .preprocessors import TextCleaner
from .metrics import ReadabilityProcessor, LexicalComplexityProcessor, StylisticProcessor
import logging

logger = logging.getLogger(__name__)

class TextEvaluationPipeline:
    """Pipeline to process text and calculate various metrics for essay evaluation"""
    def __init__(self):
        self.cleaner = TextCleaner()
        self.readability_processor = ReadabilityProcessor()
        self.lexical_processor = LexicalComplexityProcessor()
        self.stylistic= StylisticProcessor()

        try:
            self.nlp = spacy.load("en_core_web_sm")

        except OSError:
            logger.info("spaCy model 'en_core_web_sm' not found. Attempting to download...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.transition_words = {
            'addition': ['additionally', 'furthermore', 'moreover', 'also', 'in addition'],
            'contrast': ['however', 'on the other hand', 'nevertheless', 'but', 'yet'],
            'cause_effect': ['therefore', 'as a result', 'consequently', 'thus', 'hence'],
            'example': ['for example', 'for instance', 'such as', 'like'],
            'conclusion': ['in conclusion', 'to summarize', 'overall', 'in summary']
        }

        self.passive_aux = {'is', 'was', 'were', 'be', 'been', 'being', 'are'}

    def _check_passive_voice(self, doc):
        """Detects passive voice constructions in the text"""
        passive_count= 0
        for token in doc:
            if token.dep_ == 'auxpass' and token.lemma_ in self.passive_aux:
                passive_count += 1
        return passive_count
    
    def evaluate(self, text, target_words=None):
        """Main method to process text and calculate metrics"""
        logger.info("Starting text evaluation pipeline")

        clean_text = self.cleaner.clean(text)

        doc = self.nlp(clean_text)
        words = [token.text for token in doc if token.is_alpha]

        readability_metrics = self.readability.process(clean_text)
        lexical_metrics = self.lexical.process(clean_text, words)
        stylistic_metrics = self.stylistic.process(readability_metrics)
        
        word_count = readability_metrics.get('word_count')
        
        passive_count = self._check_passive_voice(doc)

        transition_count=0
        text_lower = clean_text.lower()
        for tw in self.transition_words:
            transition_count += text_lower.count(tw)

        cohesion_score = transition_count / max(1, word_count)

        structural_fixes = []

        self._generate_feedback(
            structural_fixes, word_count, target_words, transition_count,
            passive_count, readability_metrics, doc
        )

        logger.info("Text evaluation pipeline completed")

        return {
            **readability_metrics,
            **lexical_metrics,
            **self.stylistic_metrics,
            'cohesion_score': round(cohesion_score, 4),
            'passive_voice_count': passive_count,
            'structural_fixes': structural_fixes,
        }
    def _generate_feedback(self, structural_fixes, word_count, target_words, transition_count, passive_count, readability_metrics, doc):
        """Helper method to generate actionable feedback based on metrics"""
        if target_words > 0:
            deviation = abs(word_count - target_words) / target_words
            if deviation > 0.2:
                status = "overshots" if word_count > target_words else "undershoots"
                structural_fixes.append({
                    'type': 'Length Deviation',
                    'severity': 'high' if deviation > 0.4 else 'medium',
                    'message': f'Text Length ({word_count} words) {status} target ({target_words} words) by more than 20%'
                })

        if word_count > 0 and (word_count / max(1, transition_count)) > 150:
            structural_fixes.append({
                'type': 'Cohesion Vulnerability',
                'severity': 'medium',
                'message': f'Text has low cohesion with only {transition_count} transition words for {word_count} words.'
            })

        if word_count > 0 and (passive_count / word_count) > 0.05:
            structural_fixes.append({
                'type': 'Passive Voice Overuse',
                'severity': 'medium',
                'message': f'Text has a high passive voice usage with {passive_count} instances out of {word_count} words.'
            })

        for sent in doc.sents:
            sent_word_count = len([t for t in sent if not t.is_punct])
            if sent_word_count > 35:
                structural_fixes.append({
                    'type': 'Long Sentence',
                    'severity': 'low',
                    'message': f'Sentence "{sent.text[:50]}..." is quite long with {sent_word_count} words. Consider breaking it up for better readability.'
                })

    

