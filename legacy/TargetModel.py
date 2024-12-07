import matplotlib as plt
import numpy


class TgtModel:
    def __init__(self, init):
    # класс модели движения цели
        self.state = {'x':0.0, 'vx':0.0, 'ax':0.0,
                      'y':0.0, 'vy':0.0, 'ay':0.0}
        for k in init.keys():
            self.state[k] = init[k]
        self.pn    = {'sax':1.0, 'say':1.0}
        print("init state:",self.state)
    
    def CV(self, dT):
    # модель движения с примерно постоянной скоростью
        keys = ['x', 'vx', 'y', 'vy']
        X = numpy.array([self.state[k] for k in keys])
        F = numpy.array(
            [[ 1, dT, 0, 0 ],
             [ 0, 1,  0, 0 ],
             [ 0, 0,  1, dT],
             [ 0, 0,  0, 1 ]])
        
        G = numpy.array(
            [[dT**2/2, 0], 
             [dT,      0],
             [0, dT**2/2],
             [0, dT     ]])
        W = numpy.array([numpy.random.normal(0, self.state['ax']), numpy.random.normal(0, self.state['ay'])])
        Xnew = F@X + G@W

        for i in range(4):
            self.state[keys[i]] = Xnew[i]
        print("new state:", self.state)



if __name__ == '__main__':
    target1 = TgtModel({'x':0.0, 'y':1000.0, 'vx':50.0, 'vy':50.0})
    print("created tgt1")
    T = 10

    for t in range(T):
        target1.CV(1)