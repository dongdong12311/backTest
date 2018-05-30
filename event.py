# -*- coding: utf-8 -*-
"""
Created on Mon May 21 14:30:55 2018

@author: Administrator
"""


class Event(object):
    """
    Event is base class providing an interface for all subsequent 
    (inherited) events, that will trigger further events in the 
    trading infrastructure.   
    """
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with 
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'
        
        
class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    
    def __init__(self, symbol, datetime, quantity,price,direction):
        """
        Initialises the SignalEvent.

        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        direction  BUY or SELL 1 or -1
        """
        
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime      
        self.quantity = quantity
        self.price = price
        self.direction = direction
        
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity,price, direction):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        signal 1 -1
        direction - 'BUY' or 'SELL' for long or short.
        """
        
        self.type = 'ORDER'
        self.symbol = symbol
        self.price = price 
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def StrOrder(self):
        """
        Outputs the values within the Order.
        """
        return  ("Order: Symbol=%s, Type=%s, Quantity=%s, Price=%.2f ,Direction=%d" % \
            (self.symbol, self.order_type, self.quantity, self.price, self.direction))
        
        
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex, symbol, order_type, quantity,price, direction):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.price = price
        self.direction = direction
        '''
        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission
        '''
        
        
        
