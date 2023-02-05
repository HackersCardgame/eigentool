#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# an abstraction of Kev application

import sys
import os.path
import subprocess
import re
import requests
import json
import time

from datetime import date
from datetime import timedelta

from Config import Config

class Kev:
    

    def __init__(self):
        # class members
        
        #### KEV Application info start ####
        # Anlagetyp 
        # "HydroPower", "Biomass", "GeothermalPower", "WindPower", "Photovoltaic"
        self.plantType = None

        # Produzentenkategorie
        # "EnergySupplyCompany", "PublicSector", "PrivateEnterprise", "Farm", "PrivatePerson", "Misc"
        self.producerCategory = None          # [128]

        # Projektbezeichnung
        self.designation = None               # [20] Bezeichnung des Projektes
        
        ## KEV-Empfänger
        self.beneficiaryCompany = None        # [1]
        self.beneficiaryTitle = None          # [130]
        self.beneficiaryFirstName = None      # [2]
        self.beneficiaryLastName = None       # [3]
        self.beneficiaryStreet = None         # [4]
        self.beneficiaryHouseNumber = None    # [5]
        self.beneficiaryZip = None            # [6]
        self.beneficiaryCity = None           # [7]
        self.beneficiaryPoBox = None          # [8]?
        self.beneficiaryPhone = None          # [9]
        self.beneficiaryFax = None            # [10]?
        self.beneficiaryEmail = None          # [11]
        self.beneficiaryEmailConfirm = None   # [12]
        
        # Eigentumsverhältniss
        # "Owner", "ApprovalOwner" 
        self.ownershipStructure = None   # [246]   
        
        # Anlagenstandort abweichend zu den Adressdaten des KEV-Empfängers*
        self.plantLocationSameAsBeneficiary = None   # [13]
        self.plantLocationPropertyNumber = None      # [158]  Grundstücknummer
        
        # Die Anmeldung wird durch eine vom KEV-Empfänger bevollmächtigte
        # Drittperson/Drittfirma ausgefüllt.*
        self.completedThirdPerson = None    # [22]
        
        ## Autorisierte Drittperson
        # nur falls self.completedThirdPerson == True
        self.authorisedCompany = None         # [14]
        self.authorisedTitle = None           # [56]
        self.authorisedFirstName = None       # [57]
        self.authorisedLastName = None        # [58]
        self.authorisedStreet = None          # [59]
        self.authorisedHouseNumber = None     # [153]
        self.authorisedZip = None             # [84]
        self.authorisedCity = None            # [90]
        self.authorisedPoBox = None           # [91]
        self.authorisedPhone = None           # [92]
        self.authorisedFax = None             # []
        self.authorisedEmail = None           # [96]

        ## Anlagenstandort
        # nur falls self.plantLocationSameAsBeneficiary == False
        self.plantLocationStreet = None       # [16]
        self.plantLocationHouseNumber = None  # [17]
        self.plantLocationZip = None          # [18]
        self.plantLocationCity = None         # [19]
                
        ## Anlagendetails
        # (Konstruktions-)Art der Anlage
        # "FreeStanding", "BuiltOn", "Integrated"
        self.constructionType = None   # [60]

        # Status der Anlage
        # "New", "Extended"
        self.plantState = None            # [24]

        # Anlagedaten gibt es 3 mal:
        # Felder: Inbetriebnahmedatum, Leistung, jährliche Produktion, Grösse
        # - Projektierte Anlagedaten bisher: Felder 38, 40, 36, 61
        # - Anlagedaten gebaut: Felder 238, 240, 234, 62
        # - geplante Anlagedaten neu: Felder 237, 239, 233, 61

        # Projektierte Anlagedaten 
        # Geplantes/erfolgtes Inbetriebnahmedatum*
        self.plannedCommissioningDate = None  # [38]
        # Projektierte Ausbauleistung ab Generator (Photovoltaik: Solarmodulleistung)* [kWp]
        self.projectedGeneratorCapacity = None # [40]
        # Projektierte jährliche Bruttostromerzeugung [kWh/a]
        self.projectedAnualProduction = None   # [36]
        # Projektierte zukünftige Anlagengrösse* [m2]
        self.projectedPlantArea = None         # [61]
        
        # gebaute Anlagedaten
        # Inbetriebnahmedatum
        self.builtCommissioningDate = None  # [238]
        # gebaute Ausbauleistung ab Generator (Photovoltaik: Solarmodulleistung)* [kWp]
        self.builtGeneratorCapacity = None # [240]
        # gebaute jährliche Bruttostromerzeugung [kWh/a]
        self.builtAnualProduction = None   # [234]
        # gebaute Anlagengrösse* [m2]
        self.builtPlantArea = None         # [62]

        # geplannte Anlagedaten neu
        # Inbetriebnahmedatum
        self.plannedNewCommissioningDate = None  # [237]
        # gebaute Ausbauleistung ab Generator (Photovoltaik: Solarmodulleistung)* [kWp]
        self.plannedNewGeneratorCapacity = None # [239]
        # gebaute jährliche Bruttostromerzeugung [kWh/a]
        self.plannedNewAnualProduction = None   # [233]
        
        # Datum, an welchem das Projekt dem zuständigen Netzbetreiber gemeldet wurde*
        self.notificationDateGridOperator = None  # [15]
        
        
        # Zustimmung Grundeigentümer vorhanden*
        # "Owner", "Agreement"
        self.consentLandowner = None     # [46]
        
        # Art des Förderprogramms:
        # - Kleine Einmalvergütung (KLEIV)
        # - Grosse Einmalvergütung (GREIV)
        # - Einspeisevergütungssystem (EVS), bisher Kostendeckende Einspeisevergütung KEV
        self.fundingType = None     # [215]     KLEIV | GREIV | EVS
        
        ## Anlageerweiterung
        # Year of construction of the original plant *
        self.originalConstructionDate = None

        # Power rating of the original plant * [kW]
        self.originalPowerRating = None
        
        # Current size of the plant * [m2]
        self.currentPlantArea = None
        
        # Planned investments which can be or have been transacted * [CHF]
        self.plannedInvestments = None

        # Die Teilnahmebedingungen für die Projektanmeldungen wurden gelesen und akzeptiert*
        self.contractAccepted = None      # [82]
        
        #### KEV Application info end ####
        
        self.number = None                # KEV Nummer

        # KEV Status:
        #   "NoKev"         : Keine Kev Anmeldung
        #   "New"           : Kev Anmeldung neu erstellt
        #   "WaitingList"   : Warteliste entscheid
        #   "KevPending"    : 'Angemeldet', positiver KEV entscheid
        #   "KevRunning"    : Kev Anlage in Betrieb, KEV wird ausgezahlt
        #   "KevLeft"       : ausgetreten aus der KEV
        #   "EivIntent"     : Einmalvergütung vorgesehen
        #   "EivAppeal"     : Einmalvergütung Einsprachefrist
        #   "EivCleared"    : EIV abgerechnet
        #   "Imported"      : ?
        #   "KevCanceled"   : ?
        self.state = None

        # Guarantees of origin online fetch state
        # "MissingCredentials", "WrongCredentials", "Ok"
        self.fetchState = None 
        
        
        
        self.registrationDate = None      # Anmeldedatum (Datum Poststempel)
        
        self.ibmComplete = None        # Inbetriebnahmemeldung Komplett
        self.ibmForm = None            # Formular IBM
        self.notarisation = None       # Beglaubigung
        self.plantPhoto = None         # Foto der Anlage
        
        self.targetIbm = None             # Frist Inbetriebnahme
        self.waitingListPosition = None   # Wartelisteposition
        
        # Einmalvergütung
        self.optionEivForm = None           # Formular Wahlrecht zugunsten EIV
        self.optionKevForm = None           # Formular Wahlrecht zugunsten KEV
        self.ibanForm = None                # Formular IBAN
        
        self.landRegisteryExtract = None	# Grundbuchauszug
        self.powerDismissal = None			# Leistungsverzicht

        self.fetchHistory = {}

    def initFromFiles(self, projectPath):            
        # scan Folder for OnlineAnmeldung
        # print("initFromFiles")
        registrationPdfs = []
        mandatePdfs = []
        for dirname, dirnames, filenames in os.walk(projectPath):
            for filename in filenames:
                if filename.startswith("OnlineAnmeldung") and filename.endswith("pdf") and not filename.endswith("_us.pdf"):
                    registrationPdfs.append(dirname + os.sep + filename)
                if filename.startswith("Vollmachtsformular") and filename.endswith("pdf") and not filename.endswith("_us.pdf"):
                    mandatePdfs.append(dirname + os.sep + filename)

        if len(registrationPdfs) >= 2:
            print("Kev.initFromFiles: found " + str(len(registrationPdfs)) + " OnlineAnmeldungen")
            print(registrationPdfs)

        if len(mandatePdfs) >= 2:
            print("Kev.initFromFiles: found " + str(len(registrationPdfs)) + " Vollmachtformulare")
            print(mandatePdfs)

        if len(registrationPdfs) == 1:
            ret = self.fromRegistrationPdf(registrationPdfs[0])
            if ret and self.state == "NoKev":
                self.state = "New"
            return ret

        if len(mandatePdfs) == 1:
            ret = self.fromMandatePdf(mandatePdfs[0])
            if ret and self.state == "NoKev":
                self.state = "New"
            return ret
        
        return False        

    # Fill class members from an KEV Registration PDF (KEV Anmeldung)
    def fromRegistrationPdf(self, file_name):
        global config
        # print("fromRegistrationPdf('" + file_name + "')")
        
        members = {
            "0"   : ("number"                        , "text"),                  # special value

            "128" : ("producerCategory"              , "producerCategory"),
            "20"  : ("designation"                   , "text"),

            "130" : ("beneficiaryTitle"              , "text"),
            "1"   : ("beneficiaryCompany"            , "text"),
            "2"   : ("beneficiaryFirstName"          , "text"),
            "3"   : ("beneficiaryLastName"           , "text"),
            "4"   : ("beneficiaryStreet"             , "text"),
            "5"   : ("beneficiaryHouseNumber"        , "text"),
            "6"   : ("beneficiaryZip"                , "text"),
            "7"   : ("beneficiaryCity"               , "text"),
            "8"   : ("beneficiaryPoBox"              , "text"),
            "9"   : ("beneficiaryPhone"              , "text"),
            "10"  : ("beneficiaryFax"                , "text"),
            "11"  : ("beneficiaryEmail"              , "text"),
            "12"  : ("beneficiaryEmailConfirm"       , "text"),
            "246" : ("ownershipStructure"            , "ownershipStructure"),
            
            "13"  : ("plantLocationSameAsBeneficiary", "boolInverted"),
            "158" : ("plantLocationPropertyNumber"   , "text"),
            "16"  : ("plantLocationStreet"           , "text"),
            "17"  : ("plantLocationHouseNumber"      , "text"),
            "18"  : ("plantLocationZip"              , "text"),
            "19"  : ("plantLocationCity"             , "text"),

            "22"  : ("completedThirdPerson"          , "bool"),
            "14"  : ("authorisedCompany"             , "text"),
            "56"  : ("authorisedTitle"               , "text"),
            "57"  : ("authorisedFirstName"           , "text"),
            "58"  : ("authorisedLastName"            , "text"),
            "59"  : ("authorisedStreet"              , "text"),
            "153" : ("authorisedHouseNumber"         , "text"),
            "84"  : ("authorisedZip"                 , "text"),
            "90"  : ("authorisedCity"                , "text"),
            "91"  : ("authorisedPoBox"               , "text"),
            "92"  : ("authorisedPhone"               , "text"),
            "96"  : ("authorisedEmail"               , "text"),

            "60"  : ("constructionType"              , "constructionType"),
            "215" : ("fundingType"                   , "fundingType"),
            "24"  : ("plantState"                    , "plantState"),
 
            "38"  : ("plannedCommissioningDate"      , "date"),
            "40"  : ("projectedGeneratorCapacity"    , "number"),
            "36"  : ("projectedAnualProduction"      , "text"),
            "61"  : ("projectedPlantArea"            , "number"),

            "238" : ("builtCommissioningDate"        , "date"),
            "240" : ("builtGeneratorCapacity"        , "number"),
            "234" : ("builtAnualProduction"          , "text"),
            "62"  : ("builtPlantArea"                , "number"),
 
            "237" : ("plannedNewCommissioningDate"   , "date"),
            "239" : ("plannedNewGeneratorCapacity"   , "number"),
            "233" : ("plannedNewAnualProduction"     , "text"),

            "15"  : ("notificationDateGridOperator"  , "date"),
            "46"  : ("consentLandowner"              , "consentLandowner"),
            "82"  : ("contractAccepted"              , "text")
        }
        
        # first fill attributes with number => raw values
        attributes = {}
        
        pdf_txt = Config.pdfToText(file_name)

        # replace * with space to get more space between field description and field value
        pdf_txt = pdf_txt.replace("*", " ")
        
        # hack to match Anschlussgesuch datum
        pdf_txt = pdf_txt.replace("gemeldet", "gemeldet ")
        
        # print(pdf_txt)
        # get KEV-Number
        pat = re.compile('.*Projekt: (\d{5,9})', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            attributes["0"] = m.group(1)
        else:
            print("WARNING: KEV Number not found")


        # now every field with number
        pat = re.compile('(\d+)\s{1}[^\d]*\s{2}([^\[]*)')
        lines = pdf_txt.split("\n")
        for line in lines:
            line = line.strip()
            if line == "":
                continue

            m = pat.match(line)
            if not m:
                continue
            
            key = m.group(1).strip()
            val = m.group(2).strip()
            
            if key in attributes.keys():
                raise Exception("key already in attributes key=" + key)
                
            attributes[key] = val
        
        # contractAccepted is always true
        if "82" in attributes:
            del(attributes["82"])
        
        # now take the raw_value dict and apply it to the object
        for key, value_raw in attributes.items():
            # print(key + ": " + value_raw)

            if not key in members:
                print("fromRegistrationPdf " + key + " not in members")
                continue
            
            attrName = members[key][0]
            attrFormat = members[key][1]
            
            # format input
            if attrFormat == "text":
                value = value_raw
            
            elif attrFormat == "date":
                # TODO
                value = value_raw

            elif attrFormat == "number":
                # TODO
                value = value_raw

            elif attrFormat == "boolInverted":
                d = {
                    "Ja"   : False,
                    "Nein" : True
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

            elif attrFormat == "bool":
                d = {
                    "Ja"   : True,
                    "Nein" : False
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

            elif attrFormat == "consentLandowner":
                d = {
                    "Antragsteller ist selbst Grundeigent\u00fcmer"   : False,
                    "Antragsteller ist nicht selbst Grundeigent\u00fcmer und die" : True,
                    "Nein" : True
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

            elif attrFormat == "plantState":
                d = {
                    "Neuanlage"   : "New",
                    "Nein" : "Extended"
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

                
            elif attrFormat == "producerCategory":
                d = {
                    "Neuanlage"              : "EnergySupplyCompany",
                    "\u00d6ffentliche Hand"  : "PublicSector",
                    "Privatunternehmen"      : "PrivateEnterprise",
                    "Landwirtschaftsbetrieb" : "Farm",
                    "Privatperson"           : "PrivatePerson",
                    "Privatinvestor"         : "PrivatePerson",
                    "Sonstiges"              : "Misc"
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

        # "FreeStanding", "BuiltOn", "Integrated"
            elif attrFormat == "constructionType":
                d = {
                    "Neuanlage"   : "FreeStanding",
                    "Angebaute Anlage" : "BuiltOn",
                    "Integrierte Anlage"   : "Integrated"
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]

        # "Owner", "ApprovalOwner"
            elif attrFormat == "ownershipStructure":
                d = {
                    "Ich bin selbst Grundeigentümer"   : "Owner",
                    "Ich habe die Zustimmung des Grundeigentümers" : "ApprovalOwner"
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]
                
         # "KLEIV", "GREIV", "EVS"
            elif attrFormat == "fundingType":
                d = {
                    "ich möchte mich für die KLEIV anmelden"   : "KLEIV",
                    "ich möchte mich für die GREIV anmelden"   : "GREIV",
                    "ich möchte mich für die EVS anmelden"     : "EVS"
                }
                if value_raw not in d.keys():
                    print("fromRegistrationPdf: malformed format='" + attrFormat + "' val='" + value_raw + "'")
                    continue
                value = d[value_raw]
                
            else:
                print("fromregistrationPdf: unkown attrFormat:" + attrFormat)
                value = value_raw
                
            #if self.__dict__[attrName] != None and self.__dict__[attrName] != value:
            #    print(attrName + " '" +str(self.__dict__[attrName]) + "'<>'" + str(value) + "'")
            
            # hack: overwritte everything except kev fetch stuff
            #if attrName != "number" and attrName != "registrationDate" and attrName != "beneficiaryZip":
            #    self.__dict__[attrName] = value                
                
            # only set it if its default. because reimport
            if self.__dict__[attrName] == None:
                self.__dict__[attrName] = value

        self.contractAccepted = True
        
        return True

    # Fill class members from DF (KEV Vollmachtsformular)
    def fromMandatePdf(self, file_name):
        global config
        
        pdf_txt = Config.pdfToText(file_name)

        # get KEV-Number
        pat = re.compile('.*?Projekt Nummer\W*(\d{5,9})', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.number = m.group(1)
        else:
            print("WARNING: KEV Number not found")

        pat = re.compile('.*?Vorname Name\W*(\w*)\W(\w*)', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.beneficiaryFirstName = m.group(1)
            self.beneficiaryLastName = m.group(2)

        pat = re.compile('.*?Strasse Nr.\W*(\w*)\W(\d*)', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.beneficiaryStreet = m.group(1)
            self.beneficiaryHouseNumber = m.group(2)

        pat = re.compile('.*?PLZ Ort\W*(\d*)\W(\w*)', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.beneficiaryZip = m.group(1)
            self.beneficiaryCity = m.group(2)

        pat = re.compile('.*?Telefon\W*([0-9 ]*)', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.beneficiaryPhone = m.group(1)
 
        pat = re.compile('.*?E-Mail für Korrespondenz\W*(\S*)', re.DOTALL)
        m = pat.match(pdf_txt)
        if m:
            self.beneficiaryEmail = m.group(1)
 
        return True


        
    def fetchOrderTracking(self, kevNumber, zipCode, registrationDate=""):
        
        if kevNumber==None or zipCode==None:
            return False
        
        url = "https://shkn.pronovo.ch/inc/portal/order_tracking.asp?Kundenvorgangsnummer="+kevNumber+"&PlzCode="+zipCode+"&fDatum="+registrationDate+"&absenden=Weiter"
        
        failed = False
        try:
            r = requests.get(url, timeout=2)
        except:
            failed = True

        if failed:
            try:
                r = requests.get(url, timeout=10)
            except:
                print("fetchOrderTracking timed out")
                return False
        
        cont = r.content.decode("iso-8859-1")
        
        return cont

    def tryRegistrationDates(self):
        # Erhoehe Datum vom Anschlussgesuchsdatum bis es klappt
        max_days = 300
        print(self.notificationDateGridOperator)
        tokens = self.notificationDateGridOperator.split(".")
        
        d = date(int(tokens[2]), int(tokens[1]), int(tokens[0]))
        td = timedelta(1)   # one day
        d = d - td - td
        for i in range(0, max_days):
            registrationDate = d.strftime("%d.%m.%Y")
            print(registrationDate)
            d = d + td
            
            cont = self.fetchOrderTracking(self.number, self.beneficiaryZip, registrationDate)
            if "status_KEV" in cont:
                print("found: " + registrationDate)
                self.registrationDate = registrationDate
                self.checkState()
                return True
        
        return False

    def tryZipCodes(self):
        # testet alle plz durch, bis gefunden

        for i in range(4000, 9999):
            zipCode = str(i)
            print(zipCode)
                        
            cont = self.fetchOrderTracking(self.number, zipCode)
            if "status_KEV" in cont:
                print("found: zipCode=" + zipCode)
                self.beneficiaryZip = zipCode
                self.checkState()
                return True
        
        return False

    # Fetches the order_tracking website of guarantees-of-origin.ch
    # and updates the object with the info
    # returns an array of the fetched info
    def checkState(self):
        cont = self.fetchOrderTracking(self.number, self.beneficiaryZip)
        if not cont:
            return False

        # First fetchState
        if not "status_KEV" in cont:
            self.fetchState = "WrongCredentials"
            print("WrongCredentials")
            return False

        self.fetchState = "Ok"
        

        ret = {
            "state"                : None,    # Status KEV
            "targetIbm"            : None,    # Frist Inbetriebnahmemeldung
            "ibmComplete"          : None,    # Inbetriebnahme komplett
            "ibmForm"              : None,    # Formular IBM
            "notarisation"         : None,    # Beglaubigung
            "plantPhoto"           : None,    # Foto der Anlage
            "waitingPos"           : None,    # Optional Wartelisteposition
            "optionEivForm"        : None,    # Formular Wahlrecht zugunsten EIV
            "optionKevForm"        : None,    # Formular Wahlrecht zugunsten KEV
            "ibanForm"             : None,    # Formular IBAN
            "landRegisteryExtract" : None,    # Grundbuchauszug
            "powerDismissal"       : None     # Leistungsferzicht
        }

        # Status KEV
        kevStates = {
            "Warteliste"                      : "WaitingList",
            "Angemeldet"                      : "KevPending",
            "in Betrieb"                      : "KevRunning",
            "KEV ausgetreten"                 : "KevLeft",
            "Einmalvergütung vorgesehen"      : "EivIntent",
            "Einmalvergütung Einsprachefrist" : "EivAppeal",
            "EIV abgerechnet"                 : "EivCleared",
            "Importiert"                      : "Imported",
            "KEV Widerruf"                    : "KevCanceled",
        }

        pat = re.compile('.*<input type="text" name="status_KEV" class="textbox" id="Text2" value="(.*?)" disabled>', re.DOTALL)
        m = pat.match(cont)
        if not m:
            raise Exception("No status_KEV")
        
        key = m.group(1)
        if not key in kevStates:
            raise Exception("Unknown Kev Status: '" + key + "'")
        
        kevState = kevStates[key]
        ret["state"] = kevState

        # Frist Inbetriebnahmemeldung is optional
        pat = re.compile('.*<input type="text" name="Soll_IBM" class="textboxright" id="Text11" value="(.*?)" disabled>', re.DOTALL)
        m = pat.match(cont)
        if m:
            ret["targetIbm"] = m.group(1)

        # readout mandatory checkboxes
        matchesChecked = {
            "ibmComplete"          : '.*<input type="checkbox" name="IBMKomplett" value=""\s*(checked)?\s*id="CheckboxIBMKomplett" disabled>',
            "ibmForm"              : '.*<input type="checkbox" name="IBM" value=""\s*(checked)?\s*id="Checkbox2" disabled />\s*<td height="3">&nbsp;\s*Formular IBM',
            "notarisation"         : '.*<input type="checkbox" name="IBM" value=""\s*(checked)?\s*id="Checkbox2" disabled />\s*<td height="3">&nbsp;\s*Beglaubigung',
            "plantPhoto"           : '.*<input type="checkbox" name="IBM" value=""\s*(checked)?\s*id="Checkbox2" disabled />\s*<td height="3">&nbsp;\s*<label onmouseleave="javascript:tooltiphide\(tooltip3\);" onmouseover="javascript:tooltipshow\(tooltip3\);">\s*Foto der Anlage',
            "landRegisteryExtract" : '.*<input type="checkbox" name="IBM" value=""\s*(checked)?\s*id="Checkbox2" disabled />\s*<td height="3">&nbsp;\s*Grundbuchauszug',
            "powerDismissal"       : '.*<input type="checkbox" name="IBM" value=""\s*(checked)?\s*id="Checkbox2" disabled />\s*<td height="3">&nbsp;\s*Leistungsverzicht'
        }

        for var, regex in matchesChecked.items():
            pat = re.compile(regex, re.DOTALL)
            m = pat.match(cont)
            
            # must match otherwise there's some error
            if not m:
                raise Exception("Should match: " + var + "  " + regex)

            if m.group(1) == "checked":
                ret[var] = True
            else:
                ret[var] = False

        # readout optional checkboxes
        matchesChecked = {
            "optionEivForm"  : '.*<input type="checkbox" name="FormWahlrechtEIV" value=""\s*(checked)?\s*id="Checkbox3" disabled>',
            "optionKevForm"      : '.*<input type="checkbox" name="FormWahlrechtKEV" value=""\s*(checked)?\s*id="Checkbox4" disabled>',
            "ibanForm" : '.*<input type="checkbox" name="FormIBAN" value=""\s*(checked)?\s*id="Checkbox5" disabled>',
        }

        for var, regex in matchesChecked.items():
            pat = re.compile(regex, re.DOTALL)
            m = pat.match(cont)
            
            if not m:
                continue

            if m.group(1) == "checked":
                ret[var] = True
            else:
                ret[var] = False
                
                
        # Wartelistenposition is optional
        pat = re.compile('.*Wartelistenposition&nbsp;</div></td>\s*<td align="left" width="40%">\s*<input type="text" name="status_KEV" class="textboxright" id="Text6" value="([0-9\']*)" disabled>', re.DOTALL)
        m = pat.match(cont)
        if m:
            pos = m.group(1).replace("'", "")       # remove thousends separator
            ret["waitingPos"] = pos
 
        # print (ret)
        # now update the object
        self.state  = ret["state"]
        self.targetIbm = ret["targetIbm"]
        self.ibmComplete = ret["ibmComplete"]
        self.ibmForm = ret["ibmForm"]
        self.notarisation = ret["notarisation"]
        self.plantPhoto = ret["plantPhoto"]
        self.waitingListPosition = ret["waitingPos"]
        self.optionEivForm = ret["optionEivForm"]
        self.optionKevForm = ret["optionKevForm"]
        self.ibanForm = ret["ibanForm"]
        self.landRegisteryExtract = ret["landRegisteryExtract"]
        self.powerDismissal = ret["powerDismissal"]

        # add to fetchhistory
        # only add if something has changed
        add = False
        if len(self.fetchHistory) == 0:
            add = True
        else:
            maxKey = max(self.fetchHistory.keys(), key=int)
            arr = self.fetchHistory[maxKey]
            if arr != ret:
                add = True
        
        if add:
            ts = int(time.time())
            self.fetchHistory[ts] = ret
        
        return ret
    
    # from fetchHistory return the date the state first appeared
    def getStateDate(self, state):
        # search the first timestamp the state appeared
        first = "4000000000"
        for ts, hist in self.fetchHistory.items():
            if hist["state"] == state and str(ts) < first:
                first = ts
        
        if first != "4000000000":
            # convert timestamp to iso Format
            dat = date.fromtimestamp(int(first))
            ret = dat.isoformat()

            return ret
        else:
            return False


    def __str__(self):
        ret = "KEV project " + self.number + " Plant Zip:" + self.beneficiaryZip + " Date:" + self.registrationDate + " ibmComplete:" + str(self.ibmComplete)
        return ret
