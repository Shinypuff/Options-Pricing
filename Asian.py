import numpy as np
import pandas as pd

class MonteCarlo():
    def __init__(self, S, K, r, sigma, steps=252, T=5, q=0, d=20):
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.steps = steps
        self.q = q
        self.d = round(d)

    def sims(self, sims_num=10**4):
        n_sims = sims_num
        total_steps = self.steps*self.T
        total_steps = round(total_steps)
        dt = 1/self.steps

        mu = (self.r-self.q-0.5*self.sigma**2)*dt
        sigma = self.sigma*np.sqrt(dt)

        self.simulation = np.zeros([1, n_sims]) + self.S

        for i in range(1, total_steps):
            factor = np.random.randn(n_sims)
            self.simulation = np.vstack([self.simulation, self.simulation[-1, :]*np.exp(mu+sigma*factor)])
        
        return self.simulation
            
    def price(self):
        means = self.simulation[-self.d:, :].mean(axis=0)

        call_price = (np.where(means-self.K>0, means-self.K, 0)*np.exp(-self.r*self.T)).mean()
        put_price =  (np.where(self.K - means>0, self.K - means, 0)*np.exp(-self.r*self.T)).mean()

        return call_price, put_price


def Hull(S, K, T, std, r=0.085, q=0, to_print=True):
    
    m1 = (np.exp((r-q)*T)-1)*S/((r-q)*T)
    m2 = (2*np.exp((2*(r-q)+std**2)*T)*S**2)/((r-q+std**2)*(2*r-2*q+std**2)*T**2) + 2*S**2/((r-q)*T**2)*(1/(2*(r-q)+std**2)-np.exp((r-q)*T)/(r-q+std**2))
    
    var = 1/T*np.log(m2/(m1**2))
    
    d1 = (np.log(m1/K)+var*T/2)/(np.sqrt(var*T))
    d2 = d1-np.sqrt(var*T)
    
    call_price = round(np.exp(-r*T)*(m1*norm.cdf(d1)-K*norm.cdf(d2)), 5)
    
    put_price = round(np.exp(-r*T)*(K*norm.cdf(-d2) - m1*norm.cdf(-d1)), 5)  
    
    if to_print != False:
        print('Call: ', call_price, '\n Put: ', put_price)
    
    return call_price, put_price