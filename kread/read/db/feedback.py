# coding: utf-8

__all__ = [
	'MongoFeedback',
]

class MongoFeedback(object):

	def __init__(self, db):
		self.db = db
		self._feedback = db['feedback']

	def feedback(self, id):
		return self._feedback

	def add(self, id, row):
		feedback = self.feedback(id)
		feedback.update({'_id':id}, {'$set':row}, True)

	def find(self, id):
		feedback = self.feedback(id)
		return feedback.find_one({'_id':id})

