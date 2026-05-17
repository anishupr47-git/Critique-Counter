from django.db import models
import uuid
from django.utils import timezone

# Create your models here.

class EssayCategory(models.Model):
    """Helps in filtering essays and organinizing them"""
    id= models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=100, unique=True)
    description=models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Essay Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Essay(models.Model):
    """Model to store essays"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('REVIEWED', 'Reviewed'),
        ('ARCHIVED', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Title of the essay")
    prompt = models.TextField(blank=True, null=True, help_text="Prompt or question the essay is responding to")
    body_text= models.TextField(help_text="Main content of the essay")
    target_words= models.PositiveBigIntegerField(default=500, help_text="Target word count for the essay")
    author_tag= models.CharField(max_length=255, db_index=True, help_text="Tag to identify the author of the essay")
    status= models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    category= models.ForeignKey(EssayCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='essays')
    language= models.CharField(max_length=50, default='en', help_text="Language of the essay")

    created_at= models.DateTimeField(default=timezone.now)
    updated_at= models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author_tag']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author_tag}"
    
    @property
    def is_recently_updated(self):
        return (timezone.now() - self.updated_at).days < 1

class EssayMetricSnapshot(models.Model):
    """Stores the metrics for an essay at a given point in time"""
    essay= models.OneToOneField(Essay, on_delete=models.CASCADE, related_name='metrics')
    
    # Basic Counts
    word_count= models.PositiveBigIntegerField(default=0)
    sentence_count= models.PositiveBigIntegerField(default=0)
    character_count= models.PositiveBigIntegerField(default=0)
    syllable_count= models.PositiveBigIntegerField(default=0)

    #Readability Scores
    grade_level= models.FloatField(default=0.0)
    reading_ease= models.FloatField(default=0.0)
    vocab_complexity= models.FloatField(default=0.0, help_text="Average syllables per word or similar metric")
    lexical_diversity= models.FloatField(default=0.0, help_text="Unique words / total words")

    # Structural & Stylistic
    cohesion_score= models.FloatField(default=0.0)
    passive_voice_percentage= models.FloatField(default=0.0)
    avg_sentence_length= models.FloatField(default=0.0)
    avg_word_length= models.FloatField(default=0.0)

    #Feeback
    structural_feedback= models.JSONField(default=list, help_text="List of actionable feedback points related to structure")
    overall_score= models.FloatField(default=0.0, help_text="Overall quality score based on combined metrics")

    processed_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-processed_at']
        
    def __str__(self):
        return f"Metrics for {self.essay.title} ({self.overall_score:.1f}/100)"
    
    def calculate_overall_score(self):
        """Example method to calculate overall score based on metrics"""
        base_score = 70.0
        #reward good reading
        if 50<- self.reading_ease <= 80:
            base_score += 10
        #reward vocab complexity
        base_score += min(10, self.vocab_complexity/5)
        #penalize
        penalty = len(self.structural_fixes)*2

        final_score = max(0.0, min(100.0, base_score - penalty))
        return final_score
    
    def save(self, *args, **kwargs):
        if not self.overall_score:
            self.overall_score = self.calculate_overall_score()
        super().save(*args, **kwargs)
    