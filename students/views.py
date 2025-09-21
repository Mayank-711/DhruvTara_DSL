import os
import joblib
import json
import asyncio
import pandas as pd
import numpy as np
import google.generativeai as genai

from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from asgiref.sync import sync_to_async

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentAssessment

# --- 1. SETUP AND MODEL LOADING ---
# Load environment variables for API keys
load_dotenv()

# Define base directory and paths to ML model files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'students', 'model', 'classification_model.keras')
SCALER_PATH = os.path.join(BASE_DIR, 'students', 'model', 'scaler.pkl')
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'students', 'model', 'label_encoder.pkl')

# Load ML models and tools once when the server starts
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
genai.configure(api_key=GOOGLE_API_KEY)


# --- 2. SYNCHRONOUS VIEWS (Dashboard and Assessment) ---

def dashboard(request):
    """
    Displays the user's dashboard. If the user has completed an assessment,
    it shows the results. Otherwise, it prompts them to take it.
    """
    if not request.user.is_authenticated:
        return redirect('login') # Or your login page name

    try:
        assessment = StudentAssessment.objects.get(user=request.user)
        
        # NOTE: The confidence scores (92, 88, 85) are placeholders.
        # To show real scores, you would need to save them in the StudentAssessment model.
        assessment_results = [
            (assessment.career_choice_1, 92),
            (assessment.career_choice_2, 88),
            (assessment.career_choice_3, 85)
        ]
        top_match_score = assessment_results[0][1] if assessment_results else 0
        user_responses = {
            'math_interest': assessment.math_interest * 10,
            'science_interest': assessment.science_interest * 10,
            'literature_interest': assessment.literature_interest * 10,
            'coding_interest': assessment.coding_interest * 10,
            'teamwork': assessment.teamwork * 10,
            'creativity': assessment.creativity * 10,
        }
        
        context = {
            'has_completed_assessment': True,
            'assessment_results': assessment_results,
            'assessment_date': assessment.created_at.strftime("%B %d, %Y"),
            'top_match_name': assessment.career_choice_1,
            'top_match_score': top_match_score,
            **user_responses
        }
    
    except StudentAssessment.DoesNotExist:
        context = {
            'has_completed_assessment': False
        }
        
    return render(request, 'students/dashboard.html', context)


@login_required
def assessment(request):
    """
    Handles the student assessment form.
    - If the user has already taken it, redirect to the dashboard.
    - On GET, displays the form.
    - On POST, processes the form data, makes a prediction, saves it, and redirects.
    """
    if StudentAssessment.objects.filter(user=request.user).exists():
        return redirect('dashboard')

    if request.method == "POST":
        # --- THIS IS THE FIX ---
        # The dictionary keys have been changed back to PascalCase to match your trained model.
        student_data = {
            'Math_Interest': int(request.POST.get('math_interest', 0)),
            'Science_Interest': int(request.POST.get('science_interest', 0)),
            'Literature_Interest': int(request.POST.get('literature_interest', 0)),
            'Coding_Interest': int(request.POST.get('coding_interest', 0)),
            'Teamwork': int(request.POST.get('teamwork', 0)),
            'Creativity': int(request.POST.get('creativity', 0)),
            'Helping_Interest': int(request.POST.get('helping_interest', 0)),
            'Leadership': int(request.POST.get('leadership', 0)),
            'Travel_Interest': int(request.POST.get('travel_interest', 0)),
            'StableJob_Interest': int(request.POST.get('stable_job_interest', 0)),
            'Business_Interest': int(request.POST.get('business_interest', 0)),
            'Communication_Skills': int(request.POST.get('communication_skills', 0)),
        }

        # Convert to DataFrame. Pandas will use the dictionary keys as column names.
        student_df = pd.DataFrame([student_data])
        
        # Scale the data and make predictions
        # This will now work because the DataFrame columns match the scaler's expectations.
        scaled_data = scaler.transform(student_df)
        predictions = model.predict(scaled_data)
        
        # Get the top 3 career predictions
        top_3_indices = np.argsort(predictions[0])[-3:][::-1]
        
        top_3_careers = []
        for i in top_3_indices:
            career_label = label_encoder.inverse_transform([i])[0]
            confidence = predictions[0][i] * 100
            top_3_careers.append((career_label, round(confidence, 2)))

        # Save the assessment results to the database
        # Here, we map from the PascalCase keys to your lowercase model fields.
        StudentAssessment.objects.create(
            user=request.user,
            math_interest=student_data['Math_Interest'],
            science_interest=student_data['Science_Interest'],
            literature_interest=student_data['Literature_Interest'],
            coding_interest=student_data['Coding_Interest'],
            teamwork=student_data['Teamwork'],
            creativity=student_data['Creativity'],
            helping_interest=student_data['Helping_Interest'],
            leadership=student_data['Leadership'],
            travel_interest=student_data['Travel_Interest'],
            stable_job_interest=student_data['StableJob_Interest'],
            business_interest=student_data['Business_Interest'],
            communication_skills=student_data['Communication_Skills'],
            career_choice_1=top_3_careers[0][0],
            career_choice_2=top_3_careers[1][0],
            career_choice_3=top_3_careers[2][0],
        )

        return redirect('dashboard')

    return render(request, 'students/assessment.html')


# Synchronous helper function to access the database
def get_careers_for_user(user):
    """Synchronously fetches career choices from the database for a given user."""
    assessment = StudentAssessment.objects.get(user=user)
    # Filter out any empty or null career choices
    careers = [
        assessment.career_choice_1,
        assessment.career_choice_2,
        assessment.career_choice_3
    ]
    return [career for career in careers if career]

# NOTE: This is now a standard SYNCHRONOUS function
def get_career_info_from_gemini(career_name: str) -> dict:
    """Synchronously fetches detailed career information from the Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Analyze the career: '{career_name}'.
        Respond ONLY with a valid JSON object. Do not include any text, explanation,
        or markdown formatting like ```json before or after the JSON object.
        The JSON object must have these exact keys:
        - "id": a slug-friendly version of the career name.
        - "title": The properly capitalized career name.
        - "description": A concise paragraph explaining the career.
        - "responsibilities": A list of 3-5 key responsibilities.
        - "skills": A list of 3-5 essential skills.
        - "education": A brief description of the typical educational path.
        - "salary_range": An estimated annual salary range for this career in India (e.g., "₹6,00,000 - ₹20,00,000").
        """
        # NOTE: Using the standard 'generate_content' instead of 'generate_content_async'
        response = model.generate_content(prompt)
        
        cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)

    except Exception as e:
        print(f"Error calling Gemini API for '{career_name}': {e}")
        # Return a fallback dictionary if the API call fails
        return {
            "id": career_name.lower().replace(" ", "_"),
            "title": career_name,
            "description": "Information could not be loaded at this time. Please try again later.",
            "responsibilities": [],
            "skills": [],
            "education": "N/A",
            "salary_range": "N/A"
        }

@login_required
# NOTE: This is now a standard SYNCHRONOUS view
def careerpath(request):
    """
    Synchronous view to fetch a user's career recommendations and enrich
    them with detailed information from the Gemini API.
    """
    try:
        # 1. Directly fetch the user's career choices from the database.
        careers = get_careers_for_user(request.user)
        
        if not careers:
            raise StudentAssessment.DoesNotExist

        # 2. Call the Gemini API for each career one by one in a simple loop.
        # This is simpler and avoids the event loop conflict.
        career_results = []
        for career in careers:
            details = get_career_info_from_gemini(career)
            career_results.append(details)
        
        # 3. Structure the final data for the template.
        career_data = {
            "status": "success",
            "careers": career_results
        }
    
    except StudentAssessment.DoesNotExist:
        career_data = {"status": "error", "message": "You must complete the assessment first to view career paths."}
        
    except Exception as e:
        print(f"An unexpected error occurred in careerpath view: {e}")
        career_data = {"status": "error", "message": "An unexpected error occurred while fetching career details."}

    # 4. Pass the final JSON object to the template.
    return render(request, 'students/careerpath.html', {
        'career_data_json': json.dumps(career_data)
    })