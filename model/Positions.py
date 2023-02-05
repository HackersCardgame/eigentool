#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# A position in a order, order Confirmation, quote, delivery note, ...

import re

from model.Positions import *

from Config import Config

class Positions:
    
    def __init__(self):
        self.type = None        # orderConfirmation
        
        self.date = None
        self.pdf_path = None
        
        self.postions = []
    
    
    def fromOrderConfirmationPdf(self, pdf_path):
        
        global config
        
        self.type = "orderConfirmation"

        pdf_text = Config.pdfToText(pdf_path)

        # Solarmarkt AB
        pat = re.compile('.*Aarau, ([^\n]*)\n', re.DOTALL)
        m = pat.match(pdf_text)
        if m:
            materialOrdered_date = m.group(1)
            dat = Config.looseDateToIso(materialOrdered_date)
            self.date = dat
#            print("dat: " + dat)
            return True

        # Fankhauser AB
        pat = re.compile('.*Datum: ([^\n]*)\n', re.DOTALL)
        m = pat.match(pdf_text)
        if m:
            materialOrdered_date = m.group(1)
            dat = Config.looseDateToIso(materialOrdered_date)
            self.date = dat
#            print("dat2: " + dat)
            return True

        # Krannich AB
        pat = re.compile('.*(\d\d\.\d\d\.\d\d\d\d)\n', re.DOTALL)
        m = pat.match(pdf_text)
        if m:
            materialOrdered_date = m.group(1)
            dat = Config.looseDateToIso(materialOrdered_date)
            self.date = dat
#            print("dat3: " + dat)
            return True
        else:
            print("Materialbestellung not found " + pdf_path)
            return False

        return True
        
            
