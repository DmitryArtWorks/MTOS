import matplotlib.pyplot as plt
import numpy as np

#РєРѕРЅСЃС‚Р°РЅС‚С‹
d2r = np.pi/180
r2d = 180/np.pi

class target:
    def __init__(self, init):
        self.state = {'x':0.0, 'vx':0.0, 'ax':0.0,
                      'y':0.0, 'vy':0.0, 'ay':0.0}
        for k in init.keys():
            self.state[k] = init[k]
    
        self.pn = {'sax':1.0, 'say':1.0}
        print('initial state is', self.state)

    def CV(self, dT):
        # модель движения с примерно пост скоростью
        keys = ['x','vx','y','vy'] #что нужно в векторе состояния (нужный порядок ключей)

        X = np.array([self.state[k] for k in keys])
        F = [[1, dT, 0, 0],
            [0, 1, 0, 0 ],
            [0, 0, 1, dT],
            [0, 0, 0, 1 ]]
        F = np.array(F)
        G = [[dT**2/2, 0],
            [dT, 0 ],
            [0, dT**2/2],
            [0, dT]] 
        G = np.array(G)
        W = np.array ([np.random.normal(0,self.pn['sax']),np.random.normal(0,self.pn['say'])])
        Xnew = F@X + G@W

        for i in range(4):
            self.state[keys[i]] = Xnew[i]
       # print('new state is',  self.state)


class Radar:
    #модель измерителя в виде радиолокатора с известными характеристиками
    def __init__(self, params):
        self.coords = {'x':params['x'], 'y':params['y']} #передаем параметры радиолокатора
        self.lmd = params['l']
        self.dR = 15         #метры
        self.dP = 30*d2r      #из градусов в радианы P - фи (шир дн)
        self.w = 2*np.pi/0.1   #0.1 секунда один оборот
        self.fs = 40e6       #частота дискр
        self.current_los = 0 #направление линии визирования
        self.B = 10e6
        self.tau = 1/self.B
        self.freq = 0
        self.PRF = 1/66.6e-6

    def turn(self,dt):   #поворот АС
        self.current_los = self.current_los +self.w*dt
        if self.current_los >= 2*np.pi:
            self.current_los = self.current_los - 2*np.pi #деление по модулю на 2pi

    def receive (self, target_coords):    #прием сигнала радиолокатором
        range = np.sqrt((target_coords['x']-self.coords['x'])**2+(target_coords['y']-self.coords['y']))
        tz = 2*range/3e8  #задержка сигнала

        angle =  np.arctan2(target_coords['y']-self.coords['y'],target_coords['x']-self.coords['x'])
        dangle = angle - self.current_los #м/ду ЛВ и целью
        A = np.sinc(dangle/np.pi)
        B = 10e6 #частота девиации - для ЛЧМ
        tau = 1/B #длит имп
        freq = 0
        PRF =  1/66.6e-4 #частота повторения импульсов 10 км однозначная дальность
        
        t = np.arange (0,1/self.PRF - self.tau,1/self.fs)
        signal = A*np.exp(-1J*2*np.pi*self.freq*(t-tz))*(np.heaviside(t-tz,0)-np.heaviside(t-tz-self.tau,0)) + np.random.normal (0, 1, t.shape)#принятый сигнал t.shape - размерность вектора (кол-во отсчетов)
        reference_signal = np.exp(1J*2*np.pi*self.freq*t)*(np.heaviside(t,0)-np.heaviside(t-self.tau,0)) #опорный сигнал (комплексно-сопряж)
        reference_signal = reference_signal [:int(self.tau*self.fs)] #забрали ту часть, где содержится радиоимпульс и не содерж нули
        sig_fft = np.fft.fft(signal,int(self.fs/self.PRF)) #self.fs/PRF -кол-во отсчетов БПФ
        ref_fft = np.fft.fft(reference_signal,int(self.fs/self.PRF))
        u_fft = sig_fft*ref_fft #быстрая свертка
        conv_signal= np.fft.ifft(sig_fft*ref_fft) #возвращ во врем обл, ничего не отрезаем
        self.turn(1/self.PRF) #поворачиваем радиолокатор после каждого зондирования
        return {'angle':self.current_los, 'data':conv_signal} #данные: угол из конв сигнала


if __name__ == '__main__':
    target1 = target({'x':0.0, 'y':1000.0, 'vx':50, 'vy':50})
    radar1 = Radar({'x':100,'y':100,'l':0.03}) #из класса передаем числами
    data = []
    T = 1 #время моделирования
    for t in np.arange(0,T,1/radar1.PRF):
        target1.CV(1/radar1.PRF) #шаг дискр, цель с ним перемещ
        #plt.plot(target1.state['x'],target1.state['y'],'*r')
        signal = radar1.receive (target1.state) 
        data.append(signal['data']) #передаем данные

    #plt.grid()
    plt.imshow(np.array(np.abs(data)))
    plt.show()
