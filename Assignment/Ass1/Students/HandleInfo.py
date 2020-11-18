import matplotlib.pyplot as plt
class HandleInfo:
    def __init__(self):
        self.count = 0

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
    
    def writeFile(self,data):
        dt = data.split('\t')
        dt = list(map(lambda x: x + '\n',dt))
        namefile = 'describe-' + str(self.count) + '.txt'
        self.count += 1
        file1 = open(namefile,'w')
        file1.writelines(dt)
        file1.close()