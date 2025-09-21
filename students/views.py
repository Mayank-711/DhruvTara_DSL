from django.shortcuts import render,redirect
from django.contrib import messages
from tensorflow.keras.models import load_model
import os
import joblib
from .models import StudentAssessment
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'students', 'model', 'classification_model.keras')
SCALER_PATH = os.path.join(BASE_DIR, 'students', 'model', 'scaler.pkl')
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'students', 'model', 'label_encoder.pkl')

# Load once when Django starts
model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)


feature_columns = [
    'math_interest', 'science_interest', 'literature_interest', 'coding_interest',
    'teamwork', 'creativity', 'helping_interest', 'leadership',
    'travel_interest', 'stable_job_interest', 'business_interest', 'communication_skills'
]

def dashboard(request):
    return render(request, 'students/dashboard.html')


@login_required
def assessment(request):
    if request.method == "POST":
        # Collect all form inputs
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

        # Convert to DataFrame
        student_df = pd.DataFrame([student_data])

        print("Student DataFrame before scaling:\n", student_df)  # Debug print

        # Scale data
        scaled_data = scaler.transform(student_df)

        # Predict
        predictions = model.predict(scaled_data)
        top_3_indices = predictions[0].argsort()[-3:][::-1]

        top_3_careers = []
        for i in top_3_indices:
            career_label = label_encoder.inverse_transform([i])[0]
            confidence = predictions[0][i] * 100
            top_3_careers.append((career_label, round(confidence, 2)))

        print("Top 3 career recommendations:", top_3_careers)  # Debug print

        # Save to database
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

        # Redirect to dashboard
        return redirect('dashboard')

    # GET request
    return render(request, 'authapp/assessment.html')