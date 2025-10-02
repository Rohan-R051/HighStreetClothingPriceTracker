"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

Classes:
Array
ArrayException

Overview:
The array class is used to recreate a static array data structure which is later used to stimulate a stack

METHODS: 
__init__ -  intialises an instance of an array object
getSize - returns the size of an array
get - gets the value stored at index position of input
assign - assigns a value into index position of input



"""



# coded based off work done in class


class Array(object):
	#an array object with a finite size 
	def __init__(self, length):
		self.__size = length
		self.__array = []
		for i in range(length):
			self.__array.append(None)

	def getSize(self):
		# returns the size of the array
		return self.__size

	def get(self, index):
		#gets element at position n in the array

		#if the element is outside the length of the array return an error
		if index>= self.__size or index<0:
			raise ArrayException("Index "+str(index)+" out of bounds.")
		return self.__array[index]

	def assign(self, index, value):
		# assigns a value to position n in the array

		# if n is outside the length of the array raise an error
		if index>= self.__size or index<0:
			raise ArrayException("Index "+str(index)+" out of bounds.")
		self.__array[index] = value


class ArrayException(Exception):
	# Array exception with a value inputted when the array error is raised
	def __init__(self, value):
		self.value = value
	def toString(self):
		return self.value 



	

