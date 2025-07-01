import google.generativeai as genai
import os
import itertools  # We'll use this for efficient key rotation

# --- Step 1: Store all your keys in a list ---
# It's better to load these from environment variables for security,
# but for a direct answer, we will list them here.
API_KEYS = [
    "AIzaSyCeIamx0poSIzL7RexlBhL2FQ_r4cKvaqQ",  # key19
    "AIzaSyDooCtXo2zyX4LzQXOL2FjjRcqFL6BIHAY",  # key153
    "AIzaSyB4nXORI4pM1TUJZYC4lPCbP4FZCLoKyG8",  # key23
    "AIzaSyAz1gG4v_FE1U5M7vaVEDZfcqeyWEsOyVo",  # key54
    "AIzaSyB9W1P7irTX_QzBaSWqsBYo0CBj0xKKWEQ",  # keytest
    "AIzaSyAQ5ePnsutm1kNc59BD_orCSWo2-AX_Sgk",  # keytest39
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
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
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
"""
    response = model.generate_content(prompt)
    return response.text


def process_answer(message, question):
    model = get_model()  # Get a model with a new key
    prompt = f"""Evaluate the following student answer:
    '{message}'
    to the question:
    '{question}'

    Provide a brief evaluation of the answer, indicating if it is correct, partially correct, or incorrect.
    If incorrect or partially correct, briefly explain why. remember you have to asnwser just in arabic language , and don't include any parenthetical phrases:
    """
    response = model.generate_content(prompt)
    # Simple heuristic, can be improved
    is_correct = "correct" in response.text.lower()
    return is_correct, response.text