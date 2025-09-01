from django.apps import apps

def _stage_completed(user, stage_name: str) -> bool:
    Stage = apps.get_model('users', 'Stage')
    Session = apps.get_model('users', 'Session')
    try:
        stage = Stage.objects.get(name=stage_name)
    except Stage.DoesNotExist:
        return False
    return Session.objects.filter(user=user, stage=stage, is_completed=True).exists()

def _all_stages_completed(user) -> bool:
    Stage = apps.get_model('users', 'Stage')
    Session = apps.get_model('users', 'Session')
    total = Stage.objects.count()
    done = Session.objects.filter(user=user, is_completed=True).values('stage').distinct().count()
    return total > 0 and done == total

def _all_badges_collected(user) -> bool:
    Achievement = apps.get_model('users', 'Achievement')
    UserAchievement = apps.get_model('users', 'UserAchievement')
    total = Achievement.objects.count()
    have = UserAchievement.objects.filter(user=user).count()
    return total > 0 and have == total

def _login_streak_14(user) -> bool:
    # You’ll need to maintain user.login_streak (int) somewhere (e.g., on successful login).
    return getattr(user, "login_streak", 0) >= 14

def _score_good(user) -> bool:
    ConfidenceTestResult = apps.get_model('users', 'ConfidenceTestResult')
    latest = ConfidenceTestResult.objects.filter(user=user).order_by('-created_at').first()
    return bool(latest and latest.score >= 80)

def _score_medium(user) -> bool:
    ConfidenceTestResult = apps.get_model('users', 'ConfidenceTestResult')
    latest = ConfidenceTestResult.objects.filter(user=user).order_by('-created_at').first()
    return bool(latest and 50 <= latest.score < 80)

ACHIEVEMENT_RULES = {
    # per-stage
    "goal_setting":              lambda user: _stage_completed(user, "استراتيجية وضع الاهداف"),
    "problem_solving":           lambda user: _stage_completed(user, "استراتيجية حل المشكلات لتعزيز الثقة بالنفس"),
    "decision_making":           lambda user: _stage_completed(user, "اتخاذ القرارات"),
    "decision_execution":        lambda user: _stage_completed(user, "تنفيذ القرار"),
    "communication_skills":      lambda user: _stage_completed(user, "فنيات و مهارات التواصل"),
    "social_skills":             lambda user: _stage_completed(user, "تنمية المهارات الاجتماعية"),
    "courage_shyness":           lambda user: _stage_completed(user, "مواجه الخجل"),
    "discussion_lead":           lambda user: _stage_completed(user, "قيادة جلسة حوارية"),
    "self_talk":                 lambda user: _stage_completed(user, "الحديث عن الذات و مع الذات"),
    "responsibility_taking":     lambda user: _stage_completed(user, "تحمل المسؤولية"),
    "self_care":                 lambda user: _stage_completed(user, "الاهتمام بالمظهر"),
    "emotional_intelligence":    lambda user: _stage_completed(user, "الذكاء العاطفي"),

    # meta
    "14days":        _login_streak_14,
    "good_score":    _score_good,
    "midium_score":  _score_medium,  # (spelling kept as you named the badge)

    # collections
    "all_stages":    _all_stages_completed,
    "all_badges":    _all_badges_collected,
}