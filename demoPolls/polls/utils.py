from django import http
import json
from .models import Choice, Question, VoteHistory, Employee
import datetime

CURRENT_TIME = datetime.datetime.now()
SUCCESSFUL = 'successful'
FAIL = 'fail'


def to_json(data, ensure_ascii=False, ensure_bytes=False, default=None):
    result = json.dumps(data, ensure_ascii=ensure_ascii, separators=(',', ':'), default=default)
    if ensure_bytes and isinstance(result, str):
        result = result.encode('utf-8')
    return result


def api_response_data(data, status=FAIL):
    if status == SUCCESSFUL:
        data = {
            'status': SUCCESSFUL,
            'payload': data
        }
    else:
        data['status'] = FAIL
    return http.HttpResponse(to_json(data), content_type='application/json; charset=utf-8')


def turn_objects_into_list(datas):
    item_list = []
    for data in datas:
        item = data.as_json()
        item_list.append(item)
    return item_list


def get_item_in_list(lists, key):
    push_key_into_list = []
    for item in lists:
        list_item = item[key]
        push_key_into_list.append(list_item)
    return push_key_into_list

def create_question(question_text):
    question = Question.objects.create(question_text=question_text, pub_date=CURRENT_TIME, status=True)
    return question.id
