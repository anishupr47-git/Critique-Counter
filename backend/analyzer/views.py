from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import Essay, EssayCategory
from .serializers import EssaySerialzer, EssayCategorySerializer
# Create your views here.

class EssayCategoryViewSet(viewsets.ModelViewSet):
    """Viewset for managing essay categories"""
    queryset= EssayCategory.objects.all().order_by('name')
    serializer_class= EssayCategorySerializer

class EssayViewSet(viewsets.ModelViewSet):
    """Viewset for managing essays, includes filtering and metrics"""
    queryset= Essay.objects.select_related('metrics', 'category').all().order_by('-created_at')
    serializer_class= EssaySerialzer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author_tag', 'prompt', 'body_text']
    ordering_fields = ['created_at', 'target_words']
    
    def get_queryset(self):
        """optional restrctions based on query params"""
        quertyset = super().get_queryset()
        author = self.request.query_params.get('author')
        if author is not None:
            quertyset = quertyset.filter(author_tag__ixact=author)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            quertyset = quertyset.filter(status__iexact=status_filter)

        return quertyset
    
    @action(detail=False, methods=['get'])
    def historical_trends(self,request):
        """returns the last 20 metric tracking points for the most recent essays"""
        limit = int(request.query_params.get('limit', 20))
        essays = self.get_queryset()[:limit]

        timeline = []
        for essay in reversed(essays):
            if hasattr(essay, 'metrics'):
                timeline.append({
                    'id': str(essay.id),
                    'title': essay.title,
                    'created_at': essay.created_at,
                    'word_count': essay.metrics.word_count,
                    'grade_level': essay.metrics.grade_level,
                    'reading_ease': essay.metrics.reading_ease,
                    'vocab_complexity': essay.metrics.vocab_complexity,
                    'passive_voice_count': getattr(essay.metrics, 'passive_voice_count', 0),
                    'overall_score': getattr(essay.metrics, 'overall_score', 0),
                    'grade_level': essay.metrics.grade_level,
                    'reading_ease': essay.metrics.reading_ease,
                })

        return Response(timeline)
    
    @action(detail=False, methods=['get'])
    def aggregate_stats(self, request):
        """returns aggregate stats across all essays for dashboard purposes"""
        stats = qs.aggregate(
            total_essays=Count('id'),
            avg_word_count=Avg('metrics__word_count'),
            avg_grade_level=Avg('metrics__grade_level'),
            avg_reading_ease=Avg('metrics__reading_ease'),
            avg_vocab_complexity=Avg('metrics__vocab_complexity'),
            avg_overall_score=Avg('metrics__overall_score'),
            max_score=Max('metrics__overall_score'),
            min_score=Min('metrics__overall_score'),
        )
        #calculate recent activity
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_count = qs.filter(created_at__gte=seven_days_ago).count()
        stats['recent_sumbissions'] = recent_count

        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """custom action to archive an essay instead of deleting it"""
        essay = self.get_object()
        essay.status = 'archived'
        essay.save(updated_fields=['status', 'updated_at'])
        return Response({'status': 'essay archived', 'id': str(essay.id)}, status=status.HTTP_200_OK)

