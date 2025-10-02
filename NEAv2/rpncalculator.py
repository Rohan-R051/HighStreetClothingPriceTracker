
"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

rpncalculator.py

Classes:
RpnCalc
SolveException

Overview:
The array class is used to recreate a static array data structure which is later used to stimulate a stack

METHODS: 
RpnCalc.__init__ -  intialises an instance of an array object
solve - solves an RPN expression that is passed as input and returns the answer
removeSpaces - removes all spaces from an poorly formatted RPN expression



SolveException.__init__ - initialises a solve excpetion
toString - returns the error value stored in the solveException



"""





from stackTask import *

class RpnCalc(object):
	"""An instance of an RPN calculator
	only parameter past is the length of the stack required which is determined by the length of the expression needed to be solved
	"""
	def __init__(self,length):
		self._stack = Stack(length)

	def solve(self, equation):
		"""solves an rpn expression when one is passed in as a list
		
		params: takes a string that is a correctly formmated rpn expression and solves it

		returns: returns the integer result of the RPN expression
		"""

		"""all errors raised are raised as an invalid rpn expression inputted"""


		for i in range(len(equation)): # loop through each item in list
			if not(equation[i] in "+-*/sqrt"):
				try:
					self._stack.push(equation[i]) #item added to stack if not a operator
				except StackException as e:
					raise SolveException("Invalid rpn expression")
			elif equation[i] =="sq" or equation[i] == "sqrt":
				try:
					a = float(self._stack.pop())
				except StackException as e:
					raise SolveException("Invalid rpn expression")
				else:
					if equation[i] == "sq":
						ans = a**2
					else:
						ans = a**(1/2)
					self._stack.push(ans)

			else: #if item is an operator last two items are popped from stack
				try:
					b = str(self._stack.pop())
				except StackException as e:
					raise SolveException("Invalid rpn expression")
				else:
					try:
						a = str(self._stack.pop())
					except StackException as e:
						raise SolveException("Invalid rpn expression")
					ans = eval(a+equation[i]+b) #the last two items and operator are performed
					self._stack.push(ans) #the result is added to the top of the stack

		return self._stack.pop()#the final answer is the only item left on the stack

	def _removeSpaces(self,alist):
		""" removes all internal spaces from a list of strings"""
		newlist = []
		for item in alist:
			if item != "":
				newlist.append(item)#all valid numbers/operators are appended to a newlist
		return newlist #the newlist is returned


"""
Test App for the RPN calculator used to test that it works as required 
note this is never used in my solution
"""
class App(object):
	def __init__(self):
		self.__rpncalc = None
		self.__loop = True

	def _removeSpaces(self,alist):
		""" removes all internal spaces from a list of strings"""
		newlist = []
		for item in alist:
			if item != "":
				newlist.append(item)#all valid numbers/operators are appended to a newlist
		return newlist #the newlist is returned

	def main(self):
		while self.__loop:
			self.__equation = self._removeSpaces(input(">>> ").strip().split(" "))#rpn expression is inputted and formatted into a list
			self.__rpncalc = RpnCalc(len(self.__equation))#an instance of the Rpn Calc is made with a large enough stack to perform the calculation
			try:
				print(self.__rpncalc.solve(self.__equation))#the equation is solved and printed
			except SolveException as e:
				print(e.toString())#any errors are displayed




class SolveException(Exception):
	def __init__(self,value):
		self.__value = value
	def toString(self):
		""" returns the error of your choice"""
		return self.__value

