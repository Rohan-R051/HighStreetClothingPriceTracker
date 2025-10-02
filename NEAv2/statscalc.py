"""
Rohan Ratnalingam
The Grammar School At Leeds

Quickfit.com
A-level Computer Science NEA 

StatsCalc.py

Classes:
statsCalc

Overview:
The StatsCalc is version of an RPN calculator with additional methods that are used to calculate key statistical data
for quickfit.com's price analysis page.

METHODS: 
statsCalc.__init__ -  initialises an instance of a stats calculator inherting all methods from the rpnCalculator
mean - calculates the mean of a set of data values (integers or floats)
standardDev - calculates both the variance and standard deviation of an inputted list of (integers or floats)
mode - calculates the most recurrent price value
median - calculates the median of a set of data values by sorting a list and finding the middle value 
###note: it does this by use of a mergesorter object from mergesort.py


"""




from rpncalculator import *
from mergesort import *
import math


class statsCalc(RpnCalc):
    def __init__(self,length):
        super().__init__(length)
        self.__sorter = MergeSorter()

    def mean(self, prices):
        """ calculates the mean of a set of data values

        params: takes a list of floats of prices

        returns: returns the mean of the list of prices

        """

        #creating RPN expression in the format "x y z + + 3 /"
        self.__expression = ""
        for price in prices:
            self.__expression += " " + str(price)

        for i in range(len(prices) - 1):
            self.__expression += " +"

        self.__expression += " " + str(len(prices)) + " /"
        self.__expression = self._removeSpaces(self.__expression.strip().split(" ")) # removes spaces in the expression to avoid creating errors


        try:
            return self.solve(self.__expression) # solves the expression and ignores error if present
        except SolveException as e:
            print(e.toString)
            

    def standardDev(self, prices):
        """calculates the varaince and standard deviation of a set of data

        params: takes a list of floats of prices

        returns: returns the variance and standard deviation of the list of prices

        """

        average = self.mean(prices) # calculates the mean for the stddev calculation

        # writes the standard deviation expression as an RPN expression
        self.__expression = ""
        for price in prices:
            self.__expression += " " + str(price) + " sq"

        for i in range(len(prices) - 1):
            self.__expression += " +"

        self.__expression += " " + str(len(prices)) + " / "
        self.__expression += str(average) + " sq" + " -"
        # saves expression as a temporary variable to  use later
        tmp = self.__expression
        self.__expression = self._removeSpaces(self.__expression.strip().split(" "))

        # calculates variance first and ignores errors
        try:
            variance = self.solve(self.__expression)
        except SolveException as e:
            print(e.toString)

        #calculates stddev next by use of RPN calculator
        self.__expression = tmp
        self.__expression += " sqrt"
        self.__expression = self._removeSpaces(self.__expression.strip().split(" "))
        try:
            standardDev = self.solve(self.__expression)
        except SolveException as e:
            print(e.toString)

        # returns both values 
        return variance, standardDev

    def mode(self, prices):
        """ calculates the mode of a list of prices

        params: takes a list of floats of prices

        returns: returns modal price of the list
        """

        # finds the different prices and the number of times they appear in the list
        #appends these to another list in the format [[price,numOfAppearances]]
        self.__vars = []
        for price in prices:
            found = False
            for var in self.__vars:
                if var[0] == price:
                    var[1] += 1
                    found = True
            if not (found):
                self.__vars.append([price, 1])

        # creates a list of modes where the prices that appear the most area appended
        highest = 0
        mode = []
        for var in self.__vars:
            if var[1] > highest:
                mode = [var[0]]
                highest = var[1]
            elif var[1] == highest:
                mode.append(var[0])

        # returns the mode of the prices which is at position 0
        return mode[0]

    def median(self, prices):
        """ calculates the median of a list of prices

        params: takes a list of floats of prices as the only parameter

        returns: returns the median price from the list

        """

        # prices are sorted using the mergesort function
        prices = self.__sorter.mergeSort(prices)
        medianPos = (len(prices) + 1) / 2 - 1 # median position calculated using the formula (n+1/2) -1
        if medianPos % 1 == 0: # if the median pos is an integer return the median
            return prices[int(medianPos)] 
        else: # otherwise average the two numbers either side using the mean funciton to calculate the median
            x = [prices[math.floor(medianPos)], prices[math.ceil(medianPos)]]
            return self.mean(x)



