def mergeSort(alist):
	if len(alist) == 1:
		return alist
	
	midpoint = len(alist)//2
	left = alist[:midpoint]
	right = alist[midpoint:]
	
	return merge(mergeSort(left),mergeSort(right))
	

def merge(x,y):
	lp = 0
	rp = 0
	result = []
	while len(x) > lp and len(y) > rp:
		if x[lp] <= y[rp]:
			result.append(x[lp])
			lp += 1
		else:
			result.append(y[rp])
			rp += 1
	if lp == len(x):
		for i in range(rp,len(y)):
			result.append(y[i])
	else:
		for i in range(lp,len(x)):
			result.append(x[i])
	return result
	
print(merge([1,2,5],[3,4,6]))
	
print(mergeSort([1,2,5,4,6,3,8,7]))
	
