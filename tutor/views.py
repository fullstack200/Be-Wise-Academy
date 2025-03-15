from tokenize import Name
from datetime import date
import time
from django.shortcuts import render
from .models import *
from django.views.generic import CreateView, ListView
from django.contrib.auth.decorators import login_required

from users.forms import *

# Create your views here.
@login_required
def physicsView(request):
    docs = Resources.objects.filter(subjectName="Physics")
    return render(request, "subject.html", {'list': docs})
@login_required
def chemistryView(request):
    docs = Resources.objects.filter(subjectName="Chemistry")
    return render(request, "subject.html", {'list': docs})
@login_required
def mathematicsView(request):
    docs = Resources.objects.filter(subjectName="Mathematics")
    return render(request, "subject.html", {'list': docs})

def feeView(request):
    igcse7 = Fee.objects.filter(grade="7th IGCSE")
    igcse8 = Fee.objects.filter(grade="8th IGCSE")
    igcse9 = Fee.objects.filter(grade="9th IGCSE")
    igcse10 = Fee.objects.filter(grade="10th IGCSE")
    ib7 = Fee.objects.filter(grade="7th IB")
    ib8 = Fee.objects.filter(grade="8th IB")
    ib9 = Fee.objects.filter(grade="9th IB")
    ib10 = Fee.objects.filter(grade="10th IB")
    icse7 = Fee.objects.filter(grade="7th ICSE")
    icse8 = Fee.objects.filter(grade="8th ICSE")
    icse9 = Fee.objects.filter(grade="9th ICSE")
    icse10 = Fee.objects.filter(grade="10th ICSE")
    cbse7 = Fee.objects.filter(grade="7th CBSE")
    cbse8 = Fee.objects.filter(grade="8th CBSE")
    cbse9 = Fee.objects.filter(grade="9th CBSE")
    cbse10 = Fee.objects.filter(grade="10th CBSE")
            
    context = {
        'igcse7': igcse7,
        'igcse8': igcse8,
        'igcse9': igcse9,
        'igcse10': igcse10,
        'ib7': ib7,
        'ib8': ib8,
        'ib9': ib9,
        'ib10': ib10,
        'icse7': icse7,
        'icse8': icse8,
        'icse9': icse9,
        'icse10': icse10,
        'cbse7': cbse7,
        'cbse8': cbse8,
        'cbse9': cbse9,
        'cbse10': cbse10,

    }
    return render(request, "price.html", context=context)

class mathQuizView(CreateView):
    template_name = "test.html"
    model = mathQuizResult
    fields = ['studentName','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10']
    extra_context = {'quizQuestions':Quiz.objects.filter(subjectName="Mathematics")}
    success_url = 'mathresult'
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        # Check if student name already exists
        student_name = request.POST.get('studentName')
        if mathQuizResult.objects.filter(studentName=student_name).exists():
            # Return error message if student name exists
            return render(request, self.template_name, {
                'form': form,
                'error_message': "This student name already exists. Please enter a unique name.",
                **self.extra_context
            })

        if form.is_valid():
            self.request.session['name'] = student_name
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

        
class scienceQuizView(CreateView):
    template_name = "test.html"
    model = scienceQuizResult
    fields = ['studentName','q1','q2','q3','q4','q5','q6','q7','q8','q9','q10']
    extra_context = {'quizQuestions':Quiz.objects.filter(subjectName="Science")}
    success_url = 'scienceresult'

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        student_name = request.POST.get('studentName')
        if scienceQuizResult.objects.filter(studentName=student_name).exists():
            return render(request, self.template_name, {
                'form': form,
                'error_message': "This username already exists. Please choose a different one.",
                **self.extra_context
            })

        if form.is_valid():
            self.request.session['name'] = student_name
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

def mathResultView(request):
    name = request.session['name']
    questions = Quiz.objects.filter(subjectName="Mathematics")
    result_object = mathQuizResult.objects.get(studentName=name)
    correctAnswers = [i.correctAnswer for i in questions]
    userAnswers = [result_object.q1,result_object.q2,result_object.q3,result_object.q4,result_object.q5,result_object.q6,result_object.q7,result_object.q8,result_object.q9,result_object.q10]
    
    boolList = []
    for i in range(0,10):
        if userAnswers[i] is not None and correctAnswers[i].isalpha():
            if correctAnswers[i].lower() == userAnswers[i].lower():
                boolList.append(True)
        elif correctAnswers[i] == userAnswers[i]:
            boolList.append(True)

    correctAnswersCount = boolList.count(True)
    result_object.correctAnswersCount = correctAnswersCount
        #-----------------------Change count---------------------------------------------
    result_object.percentage = int(correctAnswersCount/10*100)
    current_date = date.today()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    result_object.quizTime = str(current_date) +" at "+ str(current_time)
    result_object.save()
    return render(request, "mathresults.html",{'result_object':result_object})

def scienceResultView(request):
    name = request.session['name']
    questions = Quiz.objects.filter(subjectName="Science")
    result_object = scienceQuizResult.objects.get(studentName=name)
    correctAnswers = [i.correctAnswer for i in questions]
    userAnswers = [result_object.q1,result_object.q2,result_object.q3,result_object.q4,result_object.q5,result_object.q6,result_object.q7,result_object.q8,result_object.q9,result_object.q10]
    
    boolList = []
    for i in range(0,10):
        if userAnswers[i] is not None and correctAnswers[i].isalpha():
            if correctAnswers[i].lower() == userAnswers[i].lower():
                boolList.append(True)
        elif correctAnswers[i] == userAnswers[i]:
            boolList.append(True)

    correctAnswersCount = boolList.count(True)
    result_object.correctAnswersCount = correctAnswersCount
        #-----------------------Change count---------------------------------------------
    result_object.percentage = int(correctAnswersCount/10*100)
    current_date = date.today()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    result_object.quizTime = str(current_date) +" at "+ str(current_time)
    result_object.save()
    
    return render(request, "scienceresults.html",{'result_object':result_object})

def mathQuestionsReview(request):
    name = request.session['name']
    questions = Quiz.objects.filter(subjectName="Mathematics")
    result_object = mathQuizResult.objects.get(studentName=name)
    correctAnswers = [i.correctAnswer for i in questions]
    userAnswers = [result_object.q1,result_object.q2,result_object.q3,result_object.q4,result_object.q5,result_object.q6,result_object.q7,result_object.q8,result_object.q9,result_object.q10]

    boolList = []
    for i in range(0,10):
        if userAnswers[i] == None:
            boolList.append(None)
        elif correctAnswers[i].isalpha():
            if correctAnswers[i].lower() == userAnswers[i].lower():
                boolList.append(True)
        elif correctAnswers[i] == userAnswers[i]:
            boolList.append(True)
        else:
            boolList.append(False)
    
    return render(request, "test-review.html",{'questions':questions,'result_object':result_object,'boolList':boolList})

def scienceQuestionsReview(request):
    name = request.session['name']
    questions = Quiz.objects.filter(subjectName="Science")
    result_object = scienceQuizResult.objects.get(studentName=name)
    correctAnswers = [i.correctAnswer for i in questions]
    userAnswers = [result_object.q1,result_object.q2,result_object.q3,result_object.q4,result_object.q5,result_object.q6,result_object.q7,result_object.q8,result_object.q9,result_object.q10]

    boolList = []
    for i in range(0,10):
        if userAnswers[i] == None:
            boolList.append(None)
        elif correctAnswers[i].isalpha():
            if correctAnswers[i].lower() == userAnswers[i].lower():
                boolList.append(True)
        elif correctAnswers[i] == userAnswers[i]:
            boolList.append(True)
        else:
            boolList.append(False)
    
    return render(request, "test-review.html",{'questions':questions,'result_object':result_object,'boolList':boolList})


class BlogListView(ListView):
    model = Blogs
    template_name = "blogList.html"
    context_object_name = 'blogs' 

    def __str__(self):
        return self.blogTitle

def blogDetailView(request,bid):
    blog = Blogs.objects.get(bid=bid)
    return render(request, "blogs.html", {'blog': blog})
