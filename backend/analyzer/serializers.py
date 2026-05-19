from rest_framework import serializers
from .models import Essay, EssayCategory, EssayMetricSnapshot
from nlp_engine.pipeline import TextEvaluationPipeline
import logging

logger= logging.getLogger(__name__)

class EssayCategorySerializer(serializers.ModelSerializer):
    """serializer for EssayCategory model"""
    class Meta:
        model = EssayCategory
        fields = ['id', 'name', 'description', 'created_at']

class EssayMetricSerializer(serializers.ModelSerializer):
    """comprehented for NLP metrics"""
    class Meta:
        model = EssayMetricSnapshot
        fields = [
            'id','word_count','sentence_count','character_count','syllable_count',
            'grade_level','reading_ease', 'vocab_complexity', 'lexical_diversity',
            'cohesion_score', 'passive_voice_percentage', 'avg_sentence_length', 'avg_word_length',
            'structural_feedback', 'overall_score', 'processed_at'
        ]
        read_only_fields = fields

class EssaySerializer(serializers.ModelSerializer):
    """main serializer for Essay model, includes nested category and metrics"""
    metrics = EssayMetricSerializer(read_only=True)
    category_detail= EssayCategorySerializer(source='category', read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model= Essay
        fields = [
            'id', 'title', 'prompt', 'body_text', 'target_words', 'author_tag',
            'status', 'category', 'category_detail', 'language', 'created_at',
            'updated_at', 'metrics', 'excerpt',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'metrics', 'category_detail',
            'excerpt',
        ]

    def get_excerpt(self, obj):
        """returns the excerpt of the essay for preview purposes"""
        return obj.body_text[:150] + '...' if len(obj.body_text) > 150 else obj.body_text
    
    def validate_title(self, value):
        """ensure the title is reasonable"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value 
    
    def validate_body_text(self, value):
        """ensure the body text is not empty"""
        words = value.split()
        if len(words)<10:
            raise serializers.ValidationError("Essay body must be at least 10 words long.")
        if len(words)>10000:
            raise serializers.ValidationError("Essay body cannot exceed 10,000 words.")
        return value
    
    def validate_target_words(self, value):
        if value <=0:
            raise serializers.ValidationError("Target words must be a positive integer.")
        return value
    
    def create(self, validated_data):
        """custom create method to handle essay creation and metric calculation"""
        logger.info("Creating essay with title: %s", validated_data.get('title'))

        #create the core essay instance
        essay = Essay.objects.create(**validated_data)

        try:
            pipeline = TextEvaluationPipeline()
            results = pipeline.evaluate(
                text= essay.body_text,
                target_words=essay.target_words
            )

            EssayMetricSnapshot.objects.create(
                essay= essay,
                word_count= results.get('word_count', 0),
                sentence_count= results.get('sentence_count', 0),
                character_count= results.get('character_count', 0),
                syllable_count= results.get('syllable_count', 0),
                grade_level= results.get('grade_level', 0.0),
                reading_ease= results.get('reading_ease', 0.0),
                vocab_complexity= results.get('vocab_complexity', 0.0),
                lexical_diversity= results.get('lexical_diversity', 0.0),
                cohesion_score= results.get('cohesion_score', 0.0),
                passive_voice_percentage= results.get('passive_voice_percentage', 0.0),
                avg_sentence_length= results.get('avg_sentence_length', 0.0),
                avg_word_length= results.get('avg_word_length', 0.0),
                structural_feedback= results.get('structural_feedback', []),
                overall_score= results.get('overall_score', 0.0)
            )

            logger.info("Metrics calculated and saved for essay id: %s", essay.id)

        except Exception as e:
            logger.exception("Error processing essay id %s: %s", essay.id, e)
            EssayMetricSnapshot.objects.get_or_create(
                essay=essay,
                defaults={
                    'word_count': len(essay.body_text.split()),
                    'structural_feedback': [{
                        'type': 'Processing Warning',
                        'severity': 'medium',
                        'message': 'The essay was saved, but automatic metrics could not be generated.'
                    }],
                    'overall_score': 0.0,
                },
            )

        return essay


# Keep the original typo as an alias so existing imports continue to work.
EssaySerialzer = EssaySerializer

