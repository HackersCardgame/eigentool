#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# A position in a order, order Confirmation, quote, delivery note, ...

class Position:
    
    def __init__(self):
        self.enum = None
        self.artNo = None
        self.title = None
        self.description = None
        self.quantity = None
        self.unit = None
        self.pricePerUnit = None
        self.weightPerUnit = None
        self.rabatt = None
        self.price = None
        self.weight = None
