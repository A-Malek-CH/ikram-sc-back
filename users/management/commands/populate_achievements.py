from django.core.management.base import BaseCommand
from users.models import Achievement

BADGES = [
    ("goal_setting", "استراتيجية وضع الاهداف", "أكمل جلسة تحديد الأهداف.", "achievements/goal_setting.png"),
    ("problem_solving", "استراتيجية حل المشكلات", "أكمل جلسة حل المشكلات.", "achievements/problem_solving.png"),
    ("decision_making", "اتخاذ القرارات", "أكمل جلسة اتخاذ القرارات.", "achievements/decision_making.png"),
    ("decision_execution", "تنفيذ القرار", "أكمل جلسة تنفيذ القرار.", "achievements/decision_execution.png"),
    ("communication_skills", "فنيات و مهارات التواصل", "أكمل جلسة مهارات التواصل.", "achievements/communication_skills.png"),
    ("social_skills", "تنمية المهارات الاجتماعية", "أكمل جلسة المهارات الاجتماعية.", "achievements/social_skills.png"),
    ("courage_shyness", "مواجهة الخجل", "تجاوز جلسة مواجهة الخجل.", "achievements/courage_shyness.png"),
    ("discussion_lead", "قيادة جلسة حوارية", "أكمل جلسة القيادة.", "achievements/discussion_lead.png"),
    ("self_talk", "الحديث عن الذات", "أكمل جلسة الحديث عن الذات.", "achievements/self_talk.png"),
    ("responsibility_taking", "تحمل المسؤولية", "أكمل جلسة المسؤولية.", "achievements/responsibility_taking.png"),
    ("self_care", "الاهتمام بالمظهر", "أكمل جلسة الاهتمام بالمظهر.", "achievements/self_care.png"),
    ("emotional_intelligence", "الذكاء العاطفي", "أكمل جلسة الذكاء العاطفي.", "achievements/emotional_intelligence.png"),

    # Meta achievements
    ("14days", "المواظبة 14 يوم", "سجّل الدخول لمدة 14 يومًا متتالية.", "achievements/14days.png"),
    ("good_score", "نتيجة ممتازة", "احصل على أكثر من 80 في اختبار الثقة.", "achievements/good_score.png"),
    ("midium_score", "نتيجة متوسطة", "احصل على نتيجة بين 50 و 80.", "achievements/midium_score.png"),
    ("all_stages", "إكمال جميع المراحل", "أكمل جميع جلسات التدريب.", "achievements/all_stages.png"),
    ("all_badges", "جامع الأوسمة", "اجمع جميع الأوسمة المتاحة.", "achievements/all_badges.png"),
]


class Command(BaseCommand):
    help = "Populate achievement badges"

    def handle(self, *args, **kwargs):
        for key, name, desc, img in BADGES:
            Achievement.objects.get_or_create(
                key=key,
                defaults={
                    "name": name,
                    "description": desc,
                    "image": img
                }
            )
        self.stdout.write(self.style.SUCCESS("Achievements populated successfully."))
