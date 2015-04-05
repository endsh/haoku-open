# coding: utf-8
from contextlib import contextmanager

__all__ = [
	"PQDict",
]


class _AbstractEntry(object):

	def __init__(self, pos=None, value=None):
		self.pos = pos
		self.value = value
		self.update()

	def __eq__(self, other):
		return self.score == other.score

	def __lt__(self, other):
		return self.score < other.score

	def __repr__(self):
		return self.__class__.__name__ + \
			"(%s: %d)" % (repr(self.value), self.score)

	@property
	def key(self):
		return self.value

	def update(self):
		self.score = self.get_score()

	def get_score(self):
		if hasattr(self.value, 'get_score'):
			return self.value.get_score()
		if type(self.value) == dict and 'score' in self.value:
			return self.value['score']
		return self.value


def new_entry_class(key=None, score=None, cmp_lt=None):

	class _CustomEntry(_AbstractEntry):
		pass

	if key:
		_CustomEntry.key = property(key)

	if score:
		_CustomEntry.get_score = score

	if cmp_lt:
		_CustomEntry.__lt__ = cmp_lt			

	return _CustomEntry


class PQDict(object):

	def __init__(self, values=None, key=None, score=None, cmp_lt=None):
		self._heap = []
		self._dict = {}
		self._entry_class = new_entry_class(key, score, cmp_lt)

		pos = 0
		if values:
			for value in values:
				entry = self._entry_class(pos, value)
				self._heap.append(entry)
				self._dict[entry.key] = entry
				pos += 1
		self.heapify()

	def __len__(self):
		return len(self._heap)

	def __contains__(self, dkey):
		return dkey in self._dict

	def __iter__(self):
		for entry in self._heap:
			yield entry.value

	def __getitem__(self, dkey):
		return self._dict[dkey].value

	def __setitem__(self, dkey, value):
		if dkey in self:
			raise KeyError('%s is already in the PQDict' % dkey)

		pos = len(self._heap)
		entry = self._entry_class(pos, value)
		if dkey != entry.key:
			raise KeyError('dkey is not equal key(value)')
		
		self._heap.append(entry)
		self._dict[dkey] = entry
		self._siftdown(0, pos)

	def __delitem__(self, dkey):
		heap = self._heap
		entry = self._dict.pop(dkey)
		pos = entry.pos
		end = heap.pop()
		if end is not entry:
			heap[pos] = end
			heap[pos].pos = pos
			self._sift(pos)
		del entry

	def __nonzero__(self):
		return len(self) > 0

	def __copy__(self):
		from copy import copy
		other = self.__class__(self._dkey)
		other._heap = [copy(entry) for entry in self._heap]
		other._dict = copy(self._dict)
		return other
	copy = __copy__

	def __repr__(self):
		things = ',\n'.join(['%s: %s' % (repr(entry.value), entry.score)
				for entry in self._heap])
		return self.__class__.__name__ + '({\n' + things + '})'

	__marker = object()
	def pop(self, dkey=__marker, default=__marker):
		heap = self._heap
		if dkey is self.__marker:
			if not heap:
				raise KeyError('PQDict is empty')
			entry = heap[0]
			del self[entry.key]
			return entry.value
		try:
			entry = self._dict.pop(dkey)
			pos = entry.pos
		except KeyError:
			if default is self.__marker:
				raise
			return default
		else:
			end = heap.pop()
			if end is not entry:
				heap[pos] = end
				heap[pos].pos = pos
				self._sift(pos)
			return entry.value

	def popitem(self):
		heap = self._heap
		if not heap:
			raise KeyError('PQDict is empty')
		entry = heap[0]
		del self[entry.key]
		return entry.key, entry.value

	def iterkeys(self):
		try:
			while True:
				yield self.popitem()[0]
		except KeyError:
			return

	def itervalues(self):
		try:
			while True:
				yield self.popitem()[1]
		except KeyError:
			return

	def iteritems(self):
		try:
			while True:
				yield self.popitem()
		except KeyError:
			return

	def get(self, n=1):
		if n == 1:
			return self.pop()
		values = []
		try:
			for i in xrange(n):
				values.append(self.pop())
		except KeyError:
			pass
		return values

	@contextmanager
	def get2do(self, dkey=None):
		entry = None
		try:
			try:
				entry = self._dict[dkey] if dkey is not None else self._heap[0]
			except KeyError:
				pass

			yield entry.value

			entry.update()
			self._siftup(entry.pos)
		except:
			pass

	def tail(self, count):
		values = []
		heap = self._heap
		for _ in xrange(min(count, len(self))):
			entry = heap.pop()
			del self._dict[entry.key]
			values.append(entry.value)
		return values

	def put(self, value):
		pos = len(self._heap)
		entry = self._entry_class(pos, value)
		if entry.key in self:
			raise KeyError('%s is already in the PQDict' % entry.key)
		
		self._heap.append(entry)
		self._dict[entry.key] = entry
		self._siftdown(0, pos)

	def extend(self, values):
		for value in values:
			self.put(value)

	def heapify(self):
		for entry in self._heap:
			entry.update()
		self._heapify()

	def _heapify(self):
		n = len(self._heap)
		for i in reversed(range(n//2)):
			self._siftup(i)

	def _sift(self, pos):
		heap = self._heap
		parent_pos = (pos - 1) >> 1
		child_pos = 2 * pos + 1
		if parent_pos > -1 and heap[pos] < heap[parent_pos]:
			self._siftdown(0, pos)
		elif child_pos < len(heap):
			right_pos = child_pos + 1
			if right_pos < len(heap) and not heap[child_pos] < heap[right_pos]:
				child_pos = right_pos
			if heap[child_pos] < heap[pos]:
				self._siftup(pos)

	def _siftup(self, pos):
		heap = self._heap
		end_pos = len(heap)
		start_pos = pos
		entry = heap[pos]
		child_pos = 2 * pos + 1
		while child_pos < end_pos:
			right_pos = child_pos + 1
			if right_pos < end_pos and not heap[child_pos] < heap[right_pos]:
				child_pos = right_pos
			heap[pos] = heap[child_pos]
			heap[pos].pos = pos
			pos = child_pos
			child_pos = 2 * pos + 1
		heap[pos] = entry
		heap[pos].pos = pos
		self._siftdown(start_pos, pos)

	def _siftdown(self, start_pos, pos):
		heap = self._heap
		entry = heap[pos]
		while pos > start_pos:
			parent_pos = (pos - 1) >> 1
			parent = heap[parent_pos]
			if entry < parent:
				heap[pos] = parent
				heap[pos].pos = pos
				pos = parent_pos
				continue
			break
		heap[pos] = entry
		heap[pos].pos = pos
