
"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

stackTask.py

Classes:
Stack
StackException


Overview:
The array class is used to recreate a static array data structure which is later used to stimulate a stack

METHODS: 
Stack.__init__ - creates a stack from an array with a set length that is inputted
push - adds an item to the top of the stack
pop - removes the item at the top of the stack, if secure mode on then this item is obliterated from the array structure simulating the stack
isEmpty - checks whether the stack is empty

StackException.__init__ - initialises a stack excpetion
toString - returns the error value stored in the StackException



"""





from arrayLib import *


class Stack(object):

	def __init__(self, length):
		# a stack has an array to store data in but array methods arent callable outside the stack class.
		self.__stack = Array(length)
		self.__length = length
		self.__topOfStack = 0 # position of the top of the stack is stored


	def push(self,x):
		"""adds item x to top of stack
		
		params: takes the item to be added as a parameter

		returns: None
		"""
		if not(self.__length -1 == self.__topOfStack): # check if stack is full
			self.__stack.assign(self.__topOfStack,x)
			self.__topOfStack += 1
		else:
			raise StackException("Stack Overflow Error") # error raised if maximum capactity reached

	def pop(self, secure = False):
		"""
			removes top item from stack and returns it
			If secure then the item at top is obliterated


			params: secure optional - to obliterate the item that was last at the Top of the stack

			returns: returns the item at the top of the stack

		"""
		if not(self.__topOfStack == 0): # check if stack is empty
			if secure:
				self.__stack.assign(self.__topOfStack,None) # item obliterated if secure mode on
			self.__topOfStack -= 1
			return self.__stack.get(self.__topOfStack) # item on top of stack is returned

		else:
			raise StackException("Stack is empty. Item cannot be popped") # error raised if stack is empty

	def isEmpty(self):
		"""checks whether the stack is empty
		
		params: None

		returns: true or false depending on whether the stack is empty or not
		"""

		if self.__topOfStack == 0:
			return True
		return False


class StackException(Exception):
	# stack error that is raised when there is a stack overflow/underflow
	#error value entered when error is raised
	def __init__(self, value):
		self.value = value
	def toString(self):
		return self.value



"""
Note the TestApp object that was used when I was testing the stack has been included
this is not used in the solution
"""
class TestApp(object):
	# used to test the stats calc
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

