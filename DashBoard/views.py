from django.shortcuts import get_object_or_404, render
from Feedback.models import FeedbackForm, Response, Answer, Question
from collections import Counter
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
import json




@login_required(login_url='login')
def form_analytics(request, form_id):
    feedback_form = get_object_or_404(
        FeedbackForm,
        id=form_id,
        owner=request.user
    )

    responses = Response.objects.filter(form=feedback_form)
    total_responses = responses.count()

    chartable_questions = Question.objects.filter(
        form=feedback_form,
        field_type__in=["rating", "radio", "select"]
    )

    charts = []

    # Score values used for average calculation
    score_map = {
        # Rating values
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,

        # Radio values
        "Yes": 5,
        "No": 1,

        # Dropdown values
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Neutral": 3,
        "Agree": 4,
        "Strongly Agree": 5,
    }

    # Chart generation
    for question in chartable_questions:
        answers = Answer.objects.filter(
            response__form=feedback_form,
            question=question
        )

        answer_values = [
            answer.answer_text
            for answer in answers
            if answer.answer_text
        ]

        counter = Counter(answer_values)

        if question.field_type == "rating":
            actual_values = ["1", "2", "3", "4", "5"]

            labels = [
                "Very Poor",
                "Poor",
                "Average",
                "Good",
                "Excellent"
            ]

            data = [counter.get(value, 0) for value in actual_values]

        elif question.field_type == "radio":
            labels = ["Yes", "No"]
            data = [counter.get(value, 0) for value in labels]

        elif question.field_type == "select":
            labels = [
                "Strongly Disagree",
                "Disagree",
                "Neutral",
                "Agree",
                "Strongly Agree"
            ]

            data = [counter.get(value, 0) for value in labels]

        else:
            labels = []
            data = []

        charts.append({
            "question": question.question_text,
            "field_type": question.field_type,
            "labels": json.dumps(labels),
            "data": json.dumps(data),
        })

    # User-wise average calculation
    user_averages = []

    for response in responses:
        user_score_total = 0
        user_score_count = 0

        answers = Answer.objects.filter(
            response=response,
            question__field_type__in=["rating", "radio", "select"]
        )

        for answer in answers:
            value = answer.answer_text

            if value in score_map:
                user_score_total += score_map[value]
                user_score_count += 1

        if user_score_count > 0:
            user_average = user_score_total / user_score_count
            user_averages.append(user_average)

    if user_averages:
        avg_rating = round(sum(user_averages) / len(user_averages), 2)
    else:
        avg_rating = 0

    return render(request, "form_analytics.html", {
        "feedback_form": feedback_form,
        "total_responses": total_responses,
        "avg_rating": avg_rating,
        "charts": charts,
    })

@login_required(login_url='login')
def view_responses(request, form_id):
    feedback_form = get_object_or_404(
        FeedbackForm,
        id=form_id,
        owner=request.user
    )

    responses = Response.objects.filter(
        form=feedback_form
    ).prefetch_related("answers__question").order_by("-submitted_at")

    return render(request, "responses.html", {
        "feedback_form": feedback_form,
        "responses": responses,
    })

@login_required(login_url='login')
def host_dashboard(request):
    forms = FeedbackForm.objects.filter(owner=request.user)

    total_forms = forms.count()
    total_responses = Response.objects.filter(form__owner=request.user).count()

    return render(request, "host_dashboard.html", {
        "forms": forms,
        "total_forms": total_forms,
        "total_responses": total_responses,
    })