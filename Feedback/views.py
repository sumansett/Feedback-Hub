from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Answer, FeedbackForm, Question, Response



def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@login_required(login_url='login')
def create_form(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if title:
            feedback_form = FeedbackForm.objects.create(
                owner=request.user,
                title=title,
                description=description
            )

            messages.success(request, "Feedback form created successfully. Now add questions.")
            return redirect("add_question", form_id=feedback_form.id)

        messages.error(request, "Form title is required.")

    return render(request, "create_form.html")

@login_required(login_url='login')
def add_question(request, form_id):
    feedback_form = get_object_or_404(
        FeedbackForm,
        id=form_id,
        owner=request.user
    )

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        field_type = request.POST.get("field_type")
        required = request.POST.get("required") == "on"

        if question_text and field_type:
            Question.objects.create(
                form=feedback_form,
                question_text=question_text,
                field_type=field_type,
                required=required
            )

            messages.success(request, "Question added successfully.")
            return redirect("add_question", form_id=feedback_form.id)

        messages.error(request, "Question text and field type are required.")

    questions = Question.objects.filter(form=feedback_form)

    return render(request, "add_question.html", {
        "feedback_form": feedback_form,
        "questions": questions,
    })


def public_form(request, slug):
    feedback_form = get_object_or_404(FeedbackForm, slug=slug)
    questions = Question.objects.filter(form=feedback_form)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")

        response = Response.objects.create(
            form=feedback_form,
            name=name,
            email=email
        )

        for question in questions:
            answer_text = request.POST.get(f"question_{question.id}")

            if answer_text:
                Answer.objects.create(
                    response=response,
                    question=question,
                    answer_text=answer_text
                )

        messages.success(request, "Feedback submitted successfully.")
        return redirect("thank_you")

    return render(request, "public_form.html", {
    "feedback_form": feedback_form,
    "questions": questions,
    "public_feedback_page": True,
})


def thank_you(request):
    return render(request, "thank_you.html", {
        "public_feedback_page": True,
    })


@login_required(login_url='login')
def edit_question(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        form__owner=request.user
    )

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        field_type = request.POST.get("field_type")
        required = request.POST.get("required") == "on"

        if question_text and field_type:
            question.question_text = question_text
            question.field_type = field_type
            question.required = required
            question.save()

            messages.success(request, "Question updated successfully.")
            return redirect("add_question", form_id=question.form.id)

        messages.error(request, "Question text and field type are required.")

    return render(request, "edit_question.html", {
        "question": question,
    })


@login_required(login_url='login')
def delete_question(request, question_id):
    question = get_object_or_404(
        Question,
        id=question_id,
        form__owner=request.user
    )

    form_id = question.form.id
    question.delete()

    messages.success(request, "Question deleted successfully.")
    return redirect("add_question", form_id=form_id)