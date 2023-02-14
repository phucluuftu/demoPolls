import datetime
from datetime import date as date_type, time as time_type
from django.db.models.fields.related import ManyToManyField
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.fields.files import FieldFile

class BaseModel(models.Model):
    class Meta:
        abstract = True

    def as_dict(self, fields=None, exclude=None):
        opts = self._meta
        data = {}
        fs = list(opts.fields) + list(opts.many_to_many)
        for f in fs:
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(self)
        return data

    def as_json(self, fields=None, exclude=None, **kwargs):
        """
        Return a JSON-dumpable dict
        """
        data = self.as_dict(fields, exclude)
        for attr in data:
            if isinstance(data[attr], time_type):
                data[attr] = data[attr].strftime(kwargs.get('time_format', '%H:%M:%S'))
            elif isinstance(data[attr], date_type):
                data[attr] = data[attr].strftime(kwargs.get('date_format', '%Y-%m-%d %H:%M:%S'))
            elif isinstance(data[attr], FieldFile):
                file_data = {}
                for k in kwargs.get('file_attributes', ('url',)):
                    file_data[k] = data[attr].__getattribute__(k) if hasattr(data[attr], k) else ''
                data[attr] = file_data
        return data

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        return super()._do_update(base_qs, using, pk_val, values, update_fields, forced_update)

class Employee(BaseModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

class Question(BaseModel, models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class VoteHistory(BaseModel, models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_voted = models.CharField(max_length=100)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return (self.question.question_text + ' ' + self.user_voted + ' ' + self.choice_text)

    def who_voted(self):
        return self.user_voted

class Choice(BaseModel, models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text