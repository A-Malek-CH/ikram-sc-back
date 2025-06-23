import google.generativeai as genai
import os


GOOGLE_API_KEY = "AIzaSyDAsH31KhZ4_bN1RRgAsLhnVQlW2EVVmBA"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def process_explanation(message):
    prompt = f""" as a therapist for students , Explain the following concept in a way that is easy for a student to understand , remember you have to asnwser just in arabic language , and don't include any parenthetical phrases:
    '{message}'
    """
    response = model.generate_content(prompt)
    return response.text

def process_init_question(message):
    prompt = f"""As a therapist , ask the following question to the student , remember you have to asnwser just in arabic language , and don't include any parenthetical phrases :
    '{message}'
    """
    response = model.generate_content(prompt)
    return response.text

def process_answer(message, question):
    prompt = f"""Evaluate the following student answer:
    '{message}'
    to the question:
    '{question}'

    Provide a brief evaluation of the answer, indicating if it is correct, partially correct, or incorrect.
    If incorrect or partially correct, briefly explain why. remember you have to asnwser just in arabic language , and don't include any parenthetical phrases:
    """
    response = model.generate_content(prompt)
    is_correct = "correct" in response.text.lower() # Simple heuristic, can be improved
    return is_correct, response.text
