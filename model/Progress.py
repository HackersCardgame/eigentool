#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# Project Progress

import os

from model.PvProject import *
from model.Positions import *

from Config import Config

class Progress:
    
    def __init__(self):
        
        self.inquiryReceived = None         # Anfrage erhalten
        self.roofMeasured = None
        self.quote1Sent = None
        self.quote2Sent = None
        self.quote3Sent = None
        self.quote4Sent = None
        self.orderReceived = None           # Auftrag erhalten
        self.orderRejected = None           # Auftrag nicht erhalten
        self.tagSent = None                 # Anschlussgesuch
        self.tagReceived = None
        self.iaSent = None                  # Installationsanzeige
        self.iaReceived = None
        self.bauSent = None                 # Solarmeldung/Baubegsuch
        self.bauReceived = None
        
        self.partialInvoiceSent = None      # Akontorechnung
        self.partialInvoiceReceived = None
        self.materialOrdered = None
        self.materialReceived = None
        self.constructionStart = None
        self.launch = None
        self.documentationCreated = None
        self.documentationPlaced = None
        self.finalInvoiceSent = None        # Schlussrechnung verschickt
        self.finalInvoiceReceived = None    # Schlussrechnung bezahlt

        self.siNaDcOrdered = None           # Sicherheitsnachweis DC (M+PP)
        self.siNaDcReceived = None

        self.siNaAcOrdered = None           # Sicherheitsnachweis AC
        self.siNaAcReceived = None

        self.eivComplete = None             # Förderung komplett
        self.eivPayed = None                # Förderung ausbezahlt
        
        self.archived = None                # Projekt archiviert

        self.inactiv = None                # Projekt inaktiv

    # returns state of the project:
    #  activ: Something needs to be done at some point
    #  inactiv: Project will probably be built or not nothing to be done
    #  archived: everything said and done
    #  rejected: project will never be built by us
    
    def getState(self):
        if self.orderRejected:
            return "9 - rejected " + self.orderRejected
        
        if self.archived:
            return "8 - archived " + self.archived

        # Auftrag abgeschlossen
        if self.eivPayed:
            return "7.2 - EIV payed " + self.eivPayed

        if self.eivComplete:
            return "7.1 - EIV complete " + self.eivComplete

        if self.launch:
            return "6 - in Betrieb " + self.launch
                
        # Auftrag erhalten und noch nicht abgeschlossen => aktiv
        if self.orderReceived:
            return "5 - building " + self.orderReceived
        
        # Auftrag noch nicht erhalten und letzte Aktion nicht älter als
        # 3? Monate => aktiv
        lastQuote = "2000-01-01"
        if self.quote1Sent and self.quote1Sent > lastQuote:
            lastQuote = self.quote1Sent
        if self.quote2Sent and self.quote2Sent > lastQuote:
            lastQuote = self.quote2Sent
        if self.quote3Sent and self.quote3Sent > lastQuote:
            lastQuote = self.quote3Sent
        if self.quote4Sent and self.quote4Sent > lastQuote:
            lastQuote = self.quote4Sent
        
        if lastQuote != "2000-01-01":
            return "4 - quoted " + lastQuote

        if self.inquiryReceived:
            return "3 - lead " + self.inquiryReceived
             
        return "1 - nothing"

    # returns what to do for the project sortable by Importance
    def getToDo(self):
        if not self.launch:
            if self.inquiryReceived and not self.quote1Sent:
                return "2 - quote"

            if self.orderReceived and not self.tagSent:
                return "3 - send TAG"

            if self.orderReceived and not self.bauSent:
                return "3 - send Bau"
            
            if not self.tagReceived and self.tagSent:
                return "4 - check TAG"

            if not self.bauReceived and self.bauSent:
                return "4 - check Bau"

            if not self.iaReceived and self.iaSent:
                return "4 - check IA"

        """
        TODO: financel stuff
        if not self.partialInvoiceReceived and self.partialInvoiceSent:
            return "4 - check partialInvoice"

        if not self.finalInvoiceReceived and self.finalInvoiceSent:
            return "4 - check finalInvoice"
        """
        
        if not self.siNaDcReceived and self.siNaDcOrdered:
            return "6 - check siNaDc"
        
        if not self.siNaAcReceived and self.siNaAcOrdered:
            return "6 - check siNaDc"
 
        if not self.orderReceived:
            return "1 - wait customer"
        
        return "0 - I dunno"
        
        
    def initFromFiles(self, basePath):
        global config
        
        # search for quotes, invoices and image dates
        # 
        invoices = []
        offers = []
        documentation_pdf = ""      # Pfad der Anlagedoku
        first_invoice = ""
        first_offer = ""
        first_picture = "20990101"
        ab_pdfs = []                 # Pfad der Auftragsbestätigung

        for dirname, dirnames, filenames in os.walk(basePath):
            for filename in filenames:
                if filename.startswith("R20"):
                    invoices.append(dirname + os.sep + filename)
                    first_invoice = filename

                if filename.startswith("O20"):
                    offers.append(dirname + os.sep + filename)
                    first_offer = filename
                    
                if filename.startswith("Dokumentation"):
                    needs_pdf = True
                    if filename.endswith(".pdf"):
                        documentation_pdf = dirname + os.sep + filename
                
                fn_date = filename.replace("IMG_", "")
                if fn_date.startswith("20") and fn_date.endswith(".jpg"):
                    arr = fn_date.split("_")
                    fn_date = arr[0]
                    if len(fn_date) == 8 and fn_date < first_picture:
                        first_picture = fn_date
                
                if filename.startswith("Auftragsbestätigung") and filename.endswith(".pdf") and not filename.endswith("us.pdf"):
                    ab_pdfs.append(dirname + os.sep + filename)
                    
                arr = filename.split("_AB_")
                if len(arr) == 2 and filename.endswith(".pdf") and not filename.endswith("us.pdf"):
                    ab_pdfs.append(dirname + os.sep + filename)
                
        # assume the first picture ist the date the roof was measured
        if self.roofMeasured is None or self.roofMeasured == "":
            if first_picture != "20990101":
                self.roofMeasured = first_picture[0:4] + "-" + first_picture[4:6] + "-" + first_picture[6:8]
        
        if first_invoice != "":
            if self.partialInvoiceSent is None or self.partialInvoiceSent == "":
                date = first_invoice[1:9] + "01"
                self.partialInvoiceSent = date

        if first_offer != "":
            if self.quote1Sent is None or self.quote1Sent == "":
                date = first_offer[1:9] + "01"
                self.quote1Sent = date

        # from documentation get the launch and documentation_created date
        if documentation_pdf != "":
            pdf_text = Config.pdfToText(documentation_pdf)

            # get launch_date
            if self.launch is None or self.launch == "":
                pat = re.compile('.*Inbetriebnahme:([^\n]*)\n', re.DOTALL)
                m = pat.match(pdf_text)
                if m:
                    launch_date = m.group(1)
                    self.launch = Config.looseDateToIso(launch_date)
                else:
                    print("Inbetriebnahme not found " + documentation_pdf)

            # get documentation date
            if self.documentationCreated is None or self.documentationCreated == "":
                pat = re.compile('.*\n([^\n]*)Seite 1.*\n', re.DOTALL)
                m = pat.match(pdf_text)
                if m:
                    doc_date = m.group(1)
                    self.documentationCreated = Config.looseDateToIso(doc_date)
                else:
                    print("Documentation not found " + documentation_pdf)

        # Von der Auftragsbestätigung lese das Material bestellt Datum raus
        if len(ab_pdfs) > 0:
            
            # get materialOrdered
            if self.materialOrdered is None or self.materialOrdered == "":
                materialOrdered = "2099-01-01"
                pos = Positions()
                for ab_pdf in ab_pdfs:
                    if pos.fromOrderConfirmationPdf(ab_pdf):
                        if pos.date < materialOrdered:
                            materialOrdered = pos.date
                if materialOrdered != "2099-01-01":
                    self.materialOrdered = materialOrdered
#                print("mat: " + materialOrdered)

        # Try to determine from Invoice, or documentation if order received and when
        if self.orderReceived is None or self.orderReceived == "":
            orderReceived = "2099-01-01"
            if self.documentationCreated and self.documentationCreated < orderReceived:
                orderReceived = self.documentationCreated
            if self.launch and self.launch < orderReceived:
                orderReceived = self.launch
            if self.partialInvoiceSent and self.partialInvoiceSent < orderReceived:
                orderReceived = self.partialInvoiceSent
            if self.materialOrdered and self.materialOrdered < orderReceived:
                orderReceived = self.materialOrdered
            if orderReceived != "2099-01-01":
                self.orderReceived = orderReceived
        
        # TODO: progressivly set milestones
        # TODO: if inquiryReceived, orderReceived, launch or archived is empty take the last action
        if not self.inquiryReceived:
            if self.roofMeasured:
                self.inquiryReceived = self.roofMeasured



