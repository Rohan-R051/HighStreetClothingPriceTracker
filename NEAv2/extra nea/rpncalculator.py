from stackTask import *

class RpnCalc(object):
	"""An instance of an RPN calculator"""
	def __init__(self,length):
		self.__stack = Stack(length)
	
	def solve(self, equation):
		"""solves an rpn expression when one is passed in as a list"""
		"""all errors raised are raised as an invalid rpn expression inputted"""
		for i in range(len(equation)): # loop through each item in list
			if not(equation[i] in "+-*/"): 
				try:
					self.__stack.push(equation[i]) #item added to stack if not a operator
				except StackException as e:
					raise SolveException("Invalid rpn expression")
				
			else: #if item is an operator last two items are popped from stack
				try:
					b = str(self.__stack.pop())
				except StackException as e:
					raise SolveException("Invalid rpn expression")
				else:
					try:
						a = str(self.__stack.pop())
					except StackException as e:
						raise SolveException("Invalid rpn expression")
					ans = eval(a+equation[i]+b) #the last two items and operator are performed
					self.__stack.push(ans) #the result is added to the top of the stack
		
		return self.__stack.pop()#the final answer is the only item left on the stack
				
		
class App(object):
	def __init__(self):
		self.__rpncalc = None
		self.__loop = True
	
	def __removeSpaces(self,alist):
		""" removes all internal spaces from a list of strings"""
		newlist = []
		for item in alist:
			if item != "":
				newlist.append(item)#all valid numbers/operators are appended to a newlist
		return newlist #the newlist is returned
		
	def main(self):
		while self.__loop:
			self.__equation = self.__removeSpaces(input(">>> ").strip().split(" "))#rpn expression is inputted and formatted into a list
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
	
	
a = App()
a.main()
