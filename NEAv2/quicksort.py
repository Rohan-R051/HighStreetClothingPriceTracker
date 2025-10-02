

"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

quicksort.py

Classes:
MergeSorter

Overview:
The QuickSorter class is used to sort any list or similar type data structure given as input.
It does this by following the quicksort algorithm 

METHODS: 
QuickSorter.__init__ -  intialises a QuickSorter
swap - swaps two elements in a list where the two index positions are given as inputs
partition - divides the list into two sub lists about a pivot element all elements smaller than the pivot are placed left of it and all elements greater than the pivot are placed to the right of it
quicksort - sorts any given unordered list by use of recursion



"""



class QuickSorter(object):
    def __init__(self):
        pass



    def __swap(self, arr, i, j):
        """ swap function to swap two items in a list by use of a temporary variable

        params: takes a list and two indexes as parameters

        returns: the list is altered and returned

        """
        temp = arr[i]
        arr[i] = arr[j]
        arr[j] = temp

    def __partition(self, arr, start, end, key, reverse):
        #the key function gets the value of the price of the product stored in the array alternatively it could also get the name of the product when sorting alphabetically

        #partition moves all items less than the pivot to the left and all items greater than the pivot to the right

        #the pivot is chosen to be at the end of the array
        pivot = key(arr[end])

        i = start - 1

        #gets a true/false value depending on whether the item is greater than the pivot and depending on if you want the sorted list from highest to lowest
        for j in range(start, end):
            if reverse:
                condition = key(arr[j]) > pivot
            else:
                condition = key(arr[j]) < pivot

            if condition:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[end] = arr[end], arr[i + 1]
        return i + 1


    def quicksort(self, arr, start, end, key, reverse=False):
        #the parameter reverse is used to reverse the order of the expected sorted list --> by default it is set to false
        #base case if the start pointer is not less than the end pointer then the array is of length 1
        if start < end:
            pi = self.__partition(arr, start, end, key, reverse)
            self.quicksort(arr, start, pi - 1, key, reverse)
            self.quicksort(arr, pi + 1, end, key, reverse)




"""
def insertionsort(arr, key, reverse=False):
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        if reverse:
            while j >= 0 and key(arr[j]) < key(current):
                arr[j + 1] = arr[j]
                j -= 1
        else:
            while j >= 0 and key(arr[j]) > key(current):
                arr[j + 1] = arr[j]
                j -= 1
        arr[j + 1] = current
"""