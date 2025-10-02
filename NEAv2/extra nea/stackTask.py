from arrayLib import *

class Stack(object):
	
	def __init__(self, length):
		self.__stack = Array(length)
		self.__length = length
		self.__topOfStack = 0
		
		
	def push(self,x):
		"""adds item x to top of stack"""
		if not(self.__length -1 == self.__topOfStack): # check if stack is full
			self.__stack.assign(self.__topOfStack,x)
			self.__topOfStack += 1
		else:
			raise StackException("Stack Overflow Error") # error raised if maximum capactity reached
	
	def pop(self, secure = False):
		"""
			removes top item from stack and returns it
			If secure then the item at top is obliterated
		"""
		if not(self.__topOfStack == 0): # check if stack is empty
			if secure:
				self.__stack.assign(self.__topOfStack,None) # item obliterated if secure mode on
			self.__topOfStack -= 1 
			return self.__stack.get(self.__topOfStack) # item on top of stack is returned
			
		else:
			raise StackException("Stack is empty. Item cannot be popped") # error raised if stack is empty
			
	def isEmpty(self):
		if self.__topOfStack == 0:
			return True
		return False
		

class StackException(Exception):
	def __init__(self, value):
		self.value = value
	def toString(self):
		return self.value


class TestApp(object):
	def __init__(self):
		self.__S = Stack(5)
	
	def main(self):
		while True:
			x = input(">>> ")
			if x != "":
				try:
					self.__S.push(x)
				except Exception as e:
					print(e)
			else:
				try:
					print(self.__S.pop())
				except Exception as e:
					print(e)

