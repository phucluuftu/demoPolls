from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, VoteHistory, Employee
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import *


# Json response for API
@require_http_methods(["GET"])
def user_get(request):
    if not request.user:
        data = {
            'error_code': 'require login'
        }
        return api_response_data({
            data
        })
    else:
        user = User.objects.get(username=request.user.get_username())
        user_to_list = serialize('json', [user])
        return api_response_data({
            "user": user_to_list,
        }, SUCCESSFUL)


@require_http_methods(["POST"])
def user_vote_post(request):
    body = json.loads(request.body.decode("utf-8"))
    question = Question.objects.get(id=body["pk"])
    selected_choice = question.choice_set.get(pk=body['choice'])
    newrecord = VoteHistory.objects.create(question=question, user_voted=request.user.get_username(),
                                           choice_text=selected_choice.choice_text)
    data = json.loads(serialize('json', [newrecord]))
    return api_response_data({
            "VoteHistory": data,
        }, SUCCESSFUL)


@require_http_methods(["GET"])
def question_get(request):
    datas = Question.objects.filter(status=True).order_by('pub_date')
    return api_response_data({
        "question": turn_objects_into_list(datas),
    }, SUCCESSFUL)

@require_http_methods(["GET"])
def question_search(request):
    query = request.GET.get("question_text")
    results = Question.objects.filter(question_text__icontains=query)
    item_list = []
    for data in results:
        item = data.as_json()
        choice = data.choice_set.all()
        x = turn_objects_into_list(choice)
        y = get_item_in_list(x, "choice_text")
        item.update({"choice_text": y})
        item_list.append(item)
    return api_response_data({
        "question": item_list,
    }, SUCCESSFUL)

@require_http_methods(["POST", "PUT", "DELETE"])
def question_create(request):
    body = json.loads(request.body.decode("utf-8"))
    # question_text = Question.objects.get(id=body["question_text"])
    x = create_question(body["question_text"])
    return api_response_data({
        "questionID": x,
    }, SUCCESSFUL)


@require_http_methods(["GET"])
def result_get(request, pk):
    question = Question.objects.get(pk=pk)
    vote_history = VoteHistory.objects.filter(question=question)
    return api_response_data({
        "question_info": question.as_json(),
        "vote_info": turn_objects_into_list(vote_history)
    }, SUCCESSFUL)

# View for template
def index(request):
    active_question_list = Question.objects.filter(status=True)
    template = loader.get_template('polls/index.html')
    context = {
        'active_question_list': active_question_list,
    }
    return HttpResponse(template.render(context, request))


def search(request):
    template = loader.get_template('polls/search.html')
    query = request.GET.get("q")
    result = Question.objects.filter(question_text__icontains=query)
    context = {
        'result': result,
    }
    return HttpResponse(template.render(context, request))


@login_required
def detail(request, question_id):
    try:
        num_visits = request.session.get('num_visits', 0)
        request.session['num_visits'] = num_visits + 1
        question = Question.objects.get(pk=question_id)
        question.num_visits = num_visits
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})


def result(request, pk):
    template = loader.get_template('polls/results.html')
    try:
        question = Question.objects.get(pk=pk)
        vote_history = VoteHistory.objects.filter(question=question)
        print(vote_history)
        context = {
            'question': question,
            'vote_history': vote_history,
        }
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return HttpResponse(template.render(context, request))


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        if VoteHistory.objects.filter(question=question, user_voted=request.user.get_username).exists():
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You voted a choice already.",
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            VoteHistory.objects.create(question=question, user_voted=request.user.get_username(),
                                       choice_text=selected_choice.choice_text)
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
