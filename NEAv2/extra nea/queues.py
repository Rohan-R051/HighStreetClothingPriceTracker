from arrayLib import *

class Queue(object):
	def __init__(self,length):
		self._queue = Array(length)
		self._length = length
		self._head = 0
		self._tail = 0
		
	def __isFull(self):
		return self._tail >= self._length 
		
	def _isEmpty(self):
		return self._head == self._tail
		
	def enqueue(self,item):
		if self.__isFull():
			raise QueueException("Naive Queue is full item can't be added")
		else:
			self._queue.assign(self._tail,item)
			self._tail += 1
			
	def dequeue(self):
		if self._isEmpty():
			raise QueueException("Naive Queue is Empty item can't be retrieved")
		else:
			item = self._queue.get(self._head)
			self._head += 1
			return item
			
class LinearQueue(Queue):
	def __init__(self, length):
		super().__init__(length)
		
	def dequeue(self):
		if self._isEmpty():
			raise QueueException ("Linear Queue is Empty item can't be retrieved")
		else:
			item = self._queue.get(0)
			for i in range(1,self._tail):
				self._queue.assign(i-1,self._queue.get(i))
			self._tail -= 1
			return item

class CircularQueue(Queue):
	def __init__(self, length):
		super().__init__(length)
	
	def __isFull(self):
		return self._tail - self._length == self._head
		
	def enqueue(self,item):
		if self.__isFull():
			raise QueueException("Circular Queue is full item can't be added")
		else:
			self._queue.assign(self._tail % self._length,item)
			self._tail += 1
			
	def dequeue(self):
		if self._isEmpty():
			raise QueueException("Circular Queue is Empty item can't be retrieved")
		else:
			item = self._queue.get(self._head % self._length)
			self._head += 1
			return item

			
class QueueException(Exception):
	def __init__(self, value):
		self.value = value
	def toString(self):
		return self.value



class testApp(object):
	def __init__(self):
		self.__queue = Queue(6)
		self.__linearQueue = LinearQueue(6)
		self.__circularQueue = CircularQueue(6)
		self.__loop = True
	
	def main(self):
		while self.__loop:
			x = input(">>> ")
			if x == "":
				try:
					print(self.__queue.dequeue())
				except Exception as e:
					print(e)
				try:
					print(self.__linearQueue.dequeue())
				except Exception as e:
					print(e)
				try:
					print(self.__circularQueue.dequeue())
				except Exception as e:
					print(e)
			else:
				try:
					self.__queue.enqueue(x)
				except Exception as e:
					print(e)
				try:
					self.__linearQueue.enqueue(x)
				except Exception as e:
					print(QueueException("Queue is full item can't be added"))
				try:
					self.__circularQueue.enqueue(x)
				except Exception as e:
					print(e)
"""					
a = testApp()
a.main()
"""

