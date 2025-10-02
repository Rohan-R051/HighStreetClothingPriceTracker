import matplotlib.pyplot as plt

def makeGraph(productName,x,y):

    plt.plot(x, y)

    plt.title(productName)
    plt.xlabel('Time')
    plt.ylabel('Price')

    plt.savefig('plot.png')


    plt.close()

