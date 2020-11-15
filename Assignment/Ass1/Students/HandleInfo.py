import matplotlib.pyplot as plt
class HandleInfo:
    def __init__(self):
        pass

    def drawBytetoScnd(self,time,data,label):
        lb = label.split('\n')
        plt.plot(time,data)
        plt.xlabel(lb[0])
        plt.ylabel(lb[1])
        plt.show()
    
    def drawByte(self,time,data,label):
        lb = label.split('\n')
        plt.plot(time,data)
        plt.xlabel(lb[0])
        plt.ylabel(lb[1])
        plt.show()