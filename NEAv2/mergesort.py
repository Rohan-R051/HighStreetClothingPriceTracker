
"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

mergesort.py

Classes:
MergeSorter

Overview:
The mergeSorter class is used to sort any list or similar type data structure given as input.
It does this by following the mergesort algorithm 

METHODS: 
MergeSort.__init__ -  intialises a MergeSorter
MergeSort - is run to sort a list given as input note: this function is recursive so calls itself to help the sorting process
Merge - combines two sorted list into one sorted list with all the elements of both lists


"""




class MergeSorter(object):

	def __init__(self):
		pass


	def mergeSort(self, alist):
		"""recursive mergeSort function 

		params: takes an unsorted list of either numbers or strings or a combination of both

		returns: the sorted list of the list inputted, in order from lowest to highest

		"""

		#if the list is of length 1 it is sorted so return it
		if len(alist) == 1:
			return alist
		
		#else split the list into two smaller lists
		midpoint = len(alist)//2
		left = alist[:midpoint]
		right = alist[midpoint:]
		
		#call merge of mergesort on the two lists to order the lists when they are 'sorted'
		return self.__merge(self.mergeSort(left),self.mergeSort(right))
		

	def __merge(self, x,y):
		"""combines two sorted lists x and y into one sorted list 

		params: takes two sorted lists of any length they can contain numbers or strings or a combination of both

		returns: returns one sorted list comprised of the two inputted lists

		"""

		lp = 0 #two pointers that point to the next item in the list to be added
		rp = 0
		result = []
		while len(x) > lp and len(y) > rp: # repeat until all elements from one list have been added
			if x[lp] <= y[rp]: # compares the two elements in x and y that are being pointed to the lowest is appended to the final list and the respective pointer is incramented by 1
				result.append(x[lp])
				lp += 1
			else:
				result.append(y[rp])
				rp += 1

		#adds the remaining elements from the unfinshed list to the final list
		if lp == len(x):
			for i in range(rp,len(y)):
				result.append(y[i])
		else:
			for i in range(lp,len(x)):
				result.append(x[i])
				
		return result
		

