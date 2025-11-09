import google.generativeai as genai
import os
import itertools  # We'll use this for efficient key rotation

# --- Step 1: Store all your keys in a list ---
# It's better to load these from environment variables for security,
# but for a direct answer, we will list them here.
API_KEYS = [
    "AIzaSyD9lXEf6MTUlxGxVQDinSs6RQYeDbUMONA",  # modlek
    "AIzaSyAAt0jH-zUoTN9qJxB7D5AdKW-Ws04Jrbk",  # univ
    "AIzaSyCGqFyOaIuNYGHCB2eih_kwNTlnMhKICE0",  # key23
    "AIzaSyAe8SiZEP1Y-BGRMkEELaAXsUdfq9JJ4q0",  # chmalek
    "AIzaSyCMqFWXOqJ9EoK0fclEZc1UO0gsCXczNIw",  # keytest
    "AIzaSyBxmr6Ft6lZWQ-E6ll2_GpapRAKkZOBnUs",  # malekch
]

# --- Step 2: Create a key cycler ---
# This creates an iterator that will cycle through your keys endlessly.
key_cycler = itertools.cycle(API_KEYS)


# --- Step 3: Create a function to get a dynamically configured model ---
def get_model():
    """
    Selects the next API key and returns a configured GenerativeModel instance.
    """
    # Get the next key from our cycler
    next_key = next(key_cycler)

    # Configure the API with this specific key
    genai.configure(api_key=next_key)

    # Return a new model instance configured with this key
    model = genai.GenerativeModel(model_name="models/gemini-2.5-flash-lite")
    return model


# --- Step 4: Update your functions to use the dynamic model getter ---
# Now, each time one of these functions is called, it will get a fresh model
# configured with the next key in the rotation.

def process_explanation(message):
    model = get_model()  # This correctly gets a model with a rotated key

    # This new prompt is more direct, lightweight, and gives strict instructions.
    prompt = f"""
أنت معالج نفسي لطالب. اشرح المفهوم التالي بأسلوب بسيط وواضح.
المفهوم: '{message}'

تعليمات صارمة:
- استخدم اللغة العربية الفصحى فقط.
- لا تستخدم أي تنسيق خاص (مثل Markdown) أو أقواس.
- يجب أن يكون الرد نصًا عاديًا فقط.
- لا تضف أي أسئلة في النهاية مثل "هل لديك أي أسئلة؟".
- لا تبدأ كل شرح بعبارات الترحيب 
- ابدأ مباشرة بشرح المفهوم دون مقدمات أو خاتمة.
"""
    response = model.generate_content(prompt)
    return response.text


def process_init_question(message):
    model = get_model()  # This correctly gets a model with a rotated key

    # This prompt follows the same optimized structure.
    prompt = f"""
أنت معالج نفسي لطالب. اطرح السؤال التالي على الطالب.
السؤال: '{message}'

تعليمات صارمة:
- استخدم اللغة العربية الفصحى فقط.
- لا تستخدم أي تنسيق خاص (مثل Markdown) أو أقواس.
- يجب أن يكون الرد نصًا عاديًا فقط.
- لا تضف مقدمات أو عبارات ترحيبية او ختامية.
"""
    response = model.generate_content(prompt)
    return response.text


def process_answer(message, question):
    model = get_model()
    prompt = f"""
قيّم إجابة الطالب التالية:
الإجابة: '{message}'
على السؤال:
'{question}'

التعليمات:
- استخدم اللغة العربية الفصحى فقط.
- لا تستخدم أي تنسيق خاص أو أقواس.
- قدّم تصحيحًا أو توضيحًا بسيطًا إذا لزم الأمر، ولكن بأسلوب مشجع ولطيف.
- لا تقل صراحة إن الإجابة غير صحيحة.
- استخدم أسلوبًا يحفّز الطالب على الفهم والتفكير دون إحباط.
- لا تضف مقدمات أو عبارات ترحيبية او ختامية.
"""
    response = model.generate_content(prompt)
    text = response.text.strip()

    # لا نحكم الآن على "صحيحة أو غير صحيحة" صراحةً
    # ولكن يمكن استخدام تحليل بسيط لاكتشاف إشارات إيجابية
    is_correct = any(word in text for word in ["جيد", "صحيح", "إجابة رائعة", "مفهوم", "أحسنت"])

    return is_correct, text
