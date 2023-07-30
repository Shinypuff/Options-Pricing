import numpy as np
import pandas as pd

from scipy.stats import norm
from scipy.optimize import minimize
from math import ceil

import warnings
warnings.filterwarnings('ignore')

class Option():
    def __init__(self, price, strike, sigma , start, end, call = True, EU = True, riskfree=0.075, divs = True, n=10):
        
        self.asset_price = price
        
        self.strike = strike
        
        self.sigma = sigma
        
        self.EU = EU
        
        self.riskfree = riskfree
        
        self.__call = call
        
        self.__n = n 
        
        self.__divs = divs 
        
        self.start = pd.to_datetime(start, dayfirst=True)
        self.end = pd.to_datetime(end, dayfirst=True)
        self.days = (self.end - self.start).days
        self.T = self.days/365
        self.dt = self.T/n
    

    
    def grow_tree(self, n_steps = None):
        
        """"
        
        Creates binomial tree in matrix form: from initial value - step to the RIGHT = step up; step DOWN = step down
        n_steps: number of steps for a tree
        opt_price: if False, returns tree only for the asset price; if True returns asset price tree AND option price tree
        
        """   
        if n_steps == None:
            n_steps = self.__n
        
        self.up = np.exp(self.sigma*np.sqrt(self.dt))
        self.down = 1/self.up 
        
        self.growth_factor = 1 if self.__divs == False else np.exp(self.riskfree*self.dt)
        self.p = (self.growth_factor-self.down)/(self.up-self.down)
        self.q = 1 - self.p
        
        ###########  Ценовое дерево ############

        first_row = [self.asset_price]

        for i in range(n_steps):
            first_row.append(first_row[-1]*self.up)

        tree = np.array(first_row).reshape(1, n_steps+1)

        for i in range(1, n_steps+1):
            temp = np.append(tree[-1, :-i]*self.down, [np.NaN]*i)
            tree = np.vstack([tree, temp])

        self.tree = pd.DataFrame(tree)

        price_diff = self.tree - self.strike if self.__call == True else self.strike - self.tree
        price_diff = np.where(price_diff > 0, price_diff, 0)
        
        ###########  Опционное дерево ############
            
        last_col = pd.DataFrame(np.diagonal(np.fliplr(price_diff)))

        for i in range(1, len(last_col)):
            last_col[i] = (last_col.iloc[:, -1]*self.p + last_col.iloc[:, -1].shift(periods=-1)*self.q)*np.exp(-self.riskfree*self.dt)
            
            if self.EU != True:
                temp = np.diagonal(np.fliplr(price_diff), i)
                temp = np.append(temp, [np.NaN]*i)
                last_col[i] = np.where(last_col[i] >= temp, last_col[i], temp) 

        last_col = last_col.iloc[:, ::-1]
        
        for i in last_col.index:
            last_col.loc[i, :] = last_col.loc[i, :].shift(periods=-i)
            
        last_col.columns = range(len(last_col))
        self.tree_opt = last_col

        return self
    
    
    
    
    def prettify(self, tree):
        
        """"
        
        Transforms tree into classical form
        
        """       
        
        pretty_tree = pd.DataFrame(columns = tree.columns)
        
        for i in tree.index:
            pretty_tree.loc[i, :] = tree.loc[i, :].shift(periods=i)
            pretty_tree.loc[i+0.5, :] = np.NaN

        pretty_tree = pretty_tree.sort_index().reset_index(drop=True)

        for i, column in enumerate(pretty_tree.columns):
            pretty_tree[column] = pretty_tree[column].shift(periods=(int(len(pretty_tree.index)/2)-i))
        
        pretty_tree = pretty_tree.fillna('')
        
        return pretty_tree
    
    
    def combine(self):
        
        """"
        
        Combines option and asset tree into one
        
        """
        
        opt = self.prettify(self.tree_opt)
        opt.index += 1
        opt.loc[0, :] = 0

        asset = self.prettify(self.tree)
        asset.loc[len(asset), :] = 0
        self.tree_comb = (opt.replace('', 10**(-100)) + asset.replace('', 0)).replace(10**(-100), '').drop(0).reset_index(drop=True)
        
        return self

    
    
    
    def BSM(self, precise = False):
        
        """"
        
        Calculate option's price according to Blasck-Scholes-Merton model
        
        precise: defines the value of n, if False: it uses value given during initialization, otherwise, it it equal to 1 mln
        
        """
        
        if self.EU == False:
            raise Exception('American options cannot be evaluated using Black-Scholes model')
        
        dt_precise = 0 if precise != False else self.dt
        
        self.d1 = (np.log(self.asset_price/self.strike) + (self.riskfree + self.sigma**2/2)*(self.T - dt_precise))/(self.sigma*np.sqrt(self.T - dt_precise))
        
        self.d2 = self.d1 - self.sigma*np.sqrt(self.T - dt_precise)
        
        if self.__call == True:
            self.BSM_price = norm.cdf(self.d1)*self.asset_price - norm.cdf(self.d2)*self.strike*np.exp(-1*self.riskfree*(self.T-dt_precise))
        else:
            self.BSM_price = norm.cdf(-self.d2)*self.strike*np.exp(-1*self.riskfree*(self.T-dt_precise)) - norm.cdf(-self.d1)*self.asset_price 

        return self.BSM_price
    
    
    
    def get_net(self, m = 30, width = None):
        
        if width == None:
            width = self.__n
        net = pd.DataFrame()
        
        max_col = list(self.tree_opt.iloc[0, :]).index(0) #if self.__call == False else list(self.tree_opt.iloc[:, 0]).index(0)
        s_max = self.tree.iloc[0, max_col]
    
        self.dS = self.asset_price/m
        k = ceil(s_max/self.dS)
        j = np.arange(k+1)[::-1]

        ###########  Columns ############

        first_col = []
        for i in j:
            first_col.append(i*self.dS)
        
        first_col = np.array(first_col)
        
        # price_diff = first_col - self.strike if self.__call == True else self.strike - first_col ####????????
        
        price_diff = self.strike - first_col    

        last_col = np.where(price_diff>0, price_diff, 0) 


        ###########  Rows ############

        first_row = ['Share Price/ Time']
        for i in range(width+1):
            time = round(i*self.T/width, 5)
            first_row.append(time)
        
        
        ###########  ABC ############
        
        div = 0 if self.__divs==False else float(input('enter dividend yield: '))
        
        abc = [0, 1 , 0]

        for num in j[1:-1]:    
            aj = 0.5*(self.riskfree-div)*num*self.dt - 0.5*self.sigma**2*num**2*self.dt

            bj = 1 + self.sigma**2*num**2*self.dt + self.riskfree*self.dt

            cj = -0.5*(self.riskfree-div)*num*self.dt - 0.5*self.sigma**2*num**2*self.dt

            abc = np.vstack([abc, [aj, bj, cj]])

        self.abc = np.vstack([abc, [0, 1, 0]]).T

        zeroes = np.zeros([len(last_col) - self.abc.shape[0], self.abc.shape[1]])
        abc_matrix = np.vstack([self.abc, zeroes])

        for i in range(len(abc_matrix)):
            abc_matrix[:, i] = np.roll(abc_matrix[:, i], i-1)

        inv = np.linalg.inv(abc_matrix)
        
        ###########  Grid ############
            
        net = pd.DataFrame()
        net[0] = last_col

        for i in range(1, width+1):
            net[i] = net.iloc[:, -1] @ inv
            
            if self.EU != True:
                net[i] = np.where(net[i]>last_col, net[i], last_col)
        
        net['Share price'] = first_col
        net = net.iloc[:, ::-1]
        net.columns = first_row
        
        return net
        
    def params(self):
        return self.__dict__