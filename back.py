import numpy as np
import pandas as pd
import plotly.express as px

from scipy.stats import norm
from math import ceil

import warnings
warnings.filterwarnings('ignore')


class Option():
    def __init__(self, price, strike, sigma , start, end, riskfree, EU = True, divs = True, n=10):
        
        self.asset_price = price
        
        self.strike = strike
        
        self.sigma = sigma/100
        self.riskfree = riskfree/100
        
        self.EU = EU
        
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
        
        self.pretty_tree = self.prettify(self.tree)
        self.pretty_opt = self.prettify(self.tree_opt)
        
        return self.pretty_tree, self.pretty_opt
    
    
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
        
        self.deriv = np.exp(-0.5*(self.d1)**2)/np.sqrt(2*np.pi)
        
        
        self.BSM_call = norm.cdf(self.d1)*self.asset_price - norm.cdf(self.d2)*self.strike*np.exp(-1*self.riskfree*(self.T-dt_precise))
        
        self.BSM_put = norm.cdf(-self.d2)*self.strike*np.exp(-1*self.riskfree*(self.T-dt_precise)) - norm.cdf(-self.d1)*self.asset_price 

        return round(self.BSM_call, 5), round(self.BSM_put, 5)
    
    
    def get_theta(self):
        self.theta_call = -self.asset_price*self.deriv*self.sigma/(2*np.sqrt(self.T)) - self.riskfree*self.strike*np.exp(-self.riskfree*self.T)*norm.cdf(self.d2)
            
        self.theta_put = -self.asset_price*self.deriv*self.sigma/(2*np.sqrt(self.T)) + self.riskfree*self.strike*np.exp(-self.riskfree*self.T)*norm.cdf(-1*self.d2)
            
        return round(self.theta_call/365, 5), round(self.theta_put/365, 5)
    
    def get_vega(self):
        self.vega = round(self.asset_price*np.sqrt(self.T)*self.deriv/100, 5)
        return self.vega, self.vega
    
    def get_delta(self):
        self.delta_call = norm.cdf(self.d1)
        self.delta_put = norm.cdf(self.d1)-1
            
        return round(self.delta_call, 5), round(self.delta_put, 5)
    
    def get_gamma(self):
        self.gamma = round(self.deriv/(self.asset_price*self.sigma*np.sqrt(self.T)), 5)
        return self.gamma, self.gamma
    
    def get_rho(self):
        self.rho_call = self.strike*self.T*np.exp(-1*self.riskfree*self.T)*norm.cdf(self.d2)/100
        self.rho_put= -1*self.strike*self.T*np.exp(-1*self.riskfree*self.T)*norm.cdf(-1*self.d2)/100
        
        return round(self.rho_call, 5), round(self.rho_put, 5)
    
    def full_calc(self):
        self.greeks_df = pd.DataFrame(columns = [' ', 'Колл', 'Пут'])
        
        self.greeks_df[' '] = ['Стоимость опциона', 'Дельта', 'Гамма', 'Вега', 'Тета', 'Ро']
        self.greeks_df[['Колл', 'Пут']] = [self.BSM(True),
                                           self.get_delta(), 
                                           self.get_gamma(), 
                                           self.get_vega(), 
                                           self.get_theta(), 
                                           self.get_rho()] 
        
        return self.greeks_df


def get_board(asset):
    cols = ['Тикер', 'BOARDID (string:12)', 'Страйк', 'Теор. Цена', 'IV, %', 'Посл. Цена', 'Bid', 'Offer', 'VOLTODAY (int64)', 'OPENPOSITION (double)']
    sequence = ['Тикер', 'Теор. Цена', 'Посл. Цена', 'Bid', 'Offer', 'Страйк', 'IV, %']
    
    url = f'https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/{asset}/optionboard.html'

    call, put, tmp = pd.read_html(url)
    
    ### Данные для заполнения ###
    
    centr_strike, price = tmp['CENTRALSTRIKE (double)'][0], tmp['UNDERLYINGSETTLEPRICE (double)'][0]
    
    ### Доска опционов ###
    
    call.columns, put.columns = cols, cols
    tab = pd.concat([call[sequence], put[sequence].iloc[:, ::-1].iloc[:, 2:]], axis=1).fillna(' ')
    
    ### График ###
    
    plot = px.line(tab, 
                   x = 'Страйк', 
                   y = 'IV, %',
                   labels={'Страйк':'Цена Базового Актива', 'IV, %':'Волатильность, %'},
                   width=600, height=400)

    
    volatility = tab[tab['Страйк']==centr_strike]['IV, %'].values[0]
    
    return tab, [centr_strike, price, volatility], plot
