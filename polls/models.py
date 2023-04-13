import datetime

from django.db import models
from django.utils import timezone

# TODO: What is this for?
datetime.timedelta(days=1)


class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published', default=timezone.now)
	approved = models.BooleanField('approve', default=False)
	vote_count = models.PositiveSmallIntegerField(default=0)

	def upvote(self):
		self.vote_count += 1
	
	def approve(self):
		self.approved = True
			
	def was_published_recently(self):
		return self.pub_date >= timezone.now()

	def __str__(self):
		return self.question_text
