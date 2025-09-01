# users/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Session, ConfidenceTestResult
from users.utils import check_and_award_achievements  # <-- update path if you named it differently

# Track prior is_completed to detect the moment of completion
@receiver(pre_save, sender=Session)
def _session_pre_save(sender, instance: Session, **kwargs):
    if instance.pk:
        old = sender.objects.filter(pk=instance.pk).values('is_completed').first()
        instance._was_completed_before = old['is_completed'] if old is not None else False
    else:
        instance._was_completed_before = False

@receiver(post_save, sender=Session)
def _session_post_save(sender, instance: Session, created, **kwargs):
    # If it just transitioned to completed, check + award
    if instance.is_completed and not getattr(instance, "_was_completed_before", False):
        check_and_award_achievements(instance.user)

@receiver(post_save, sender=ConfidenceTestResult)
def _confidence_result_post_save(sender, instance: ConfidenceTestResult, created, **kwargs):
    # On any new/updated score, re-check achievements (good_score / midium_score / all_badges, etc.)
    check_and_award_achievements(instance.user)
