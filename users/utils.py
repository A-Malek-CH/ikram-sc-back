# users/achievements_utils.py
from django.apps import apps
from users.rules import ACHIEVEMENT_RULES

def check_and_award_achievements(user):
    Achievement = apps.get_model('users', 'Achievement')
    UserAchievement = apps.get_model('users', 'UserAchievement')

    for key, rule in ACHIEVEMENT_RULES.items():
        try:
            if rule(user):
                ach = Achievement.objects.get(key=key)
                UserAchievement.objects.get_or_create(user=user, achievement=ach)
        except Achievement.DoesNotExist:
            # Badge not populated yet
            continue
