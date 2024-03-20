#Global Variables----------------------------------------------
TransitionStart = 600
TransitionEnd = 6*TransitionStart
TransitionMid = (TransitionStart + TransitionEnd)/2
OriginalMintRate = 1.5
#---------------------------------------------------------------


#Objects--------------------------------------------------------
class Token:
    AllTokens = []

    def __init__ (self, Amount, PredictionBool, UniqueReferenceNumber):
        self.Amount = Amount
        self.PredictionBool = PredictionBool
        self.UniqueReferenceNumber = UniqueReferenceNumber
        if PredictionBool:
            self.Name = "Positive Outcome Token"
        elif not PredictionBool:
            self.Name = "Negative Outcome Token"
        else:
            self.Name = "Null Token"
        Token.AllTokens.append(self)

    def __str__(self):
        return f"{self.Name}: {self.Amount}"


class Speculation:
    AllSpeculations = []

    def __init__ (self, UniqueReferenceName):
        self.UniqueReferenceName = UniqueReferenceName
        self.PositiveToken = Token(1, True, self.UniqueReferenceName + "001")
        self.NegativeToken = Token(1, False, self.UniqueReferenceName + "002")
        self.AllTokens = [self.PositiveToken, self.NegativeToken]
        self.TotalInvested = 0
        Speculation.AllSpeculations.append(self)

    def __str__ (self):
        return(f"{self.UniqueReferenceName} Total Invested: {self.TotalInvested}\n{self.UniqueReferenceName} Total Tokens: {self.TotalTokens()}\n{self.UniqueReferenceName} Total Positive Tokens: {self.TotalPositiveTokens()}\n{self.UniqueReferenceName} Total Negative Tokens: {self.TotalNegativeTokens()}")

    def CreateToken (self, Amount, PredictionBool):
        if len(self.AllTokens) < 10:
            number = "00"+str(len(self.AllTokens))
        elif len(self.AllTokens) < 100:
            number = "0" +str(len(self.AllTokens))
        elif len(self.AllTokens) < 1000:
            number = str(len(self.AllTokens))
        else:
            pass
        self.Token = Token(Amount,PredictionBool, self.UniqueReferenceName + number)
        self.AllTokens.append(self.Token)
        return(self.Token)

    def TotalTokens(self):
        sum = 0
        for obj in self.AllTokens:
            sum += obj.Amount
        return sum

    def TotalPositiveTokens(self):
        sum = 0
        for obj in self.AllTokens:
            if obj.PredictionBool:
                sum += obj.Amount
        return sum

    def TotalNegativeTokens(self):
        sum = 0
        for obj in self.AllTokens:
            if not obj.PredictionBool:
                sum += obj.Amount
        return sum

    def TransitionMultiplier(self, MintRunningTotal):
        Total = self.TotalTokens() + MintRunningTotal
        global TransitionStart
        global TransitionMid
        global TransitionEnd
        if Total < TransitionStart:
            return (0)
        elif Total < TransitionMid:
            return (8*((Total-TransitionStart)/(TransitionEnd-TransitionStart))**4)
        elif Total < TransitionEnd:
            return (1-(8*(((Total-TransitionStart)/(TransitionEnd-TransitionStart))-1)**4))
        else:
            return (1)

    def MintingMultiplier(self, PredictionBool, MintRunningTotal):
        Total = self.TotalTokens() + MintRunningTotal
        global OriginalMintRate
        if PredictionBool:
            PositiveTotal = self.TotalPositiveTokens() + MintRunningTotal
            return(OriginalMintRate +(((Total/PositiveTotal)-OriginalMintRate)*self.TransitionMultiplier(MintRunningTotal)))
        else:
            NegativeTotal = self.TotalNegativeTokens() + MintRunningTotal
            return(OriginalMintRate +(((Total/NegativeTotal)-OriginalMintRate)*self.TransitionMultiplier(MintRunningTotal)))

    def Mint(self,Investment,PredictionBool, MintRunningTotal):
        self.TotalInvested += Investment
        return(Investment*self.MintingMultiplier(PredictionBool, MintRunningTotal))

    def SlowMintLoop(self,Investment,PredictionBool):
        InvestmentRunningTotal = Investment
        MaxInvestment = 1
        MintRunningTotal = 0

        while InvestmentRunningTotal > MaxInvestment:
            MintRunningTotal += self.Mint(MaxInvestment,PredictionBool, MintRunningTotal)
            InvestmentRunningTotal = InvestmentRunningTotal - MaxInvestment

        MintRunningTotal += self.Mint(InvestmentRunningTotal,PredictionBool, MintRunningTotal)
        return(MintRunningTotal)


class Person:
    AllPeople = []

    def __init__ (self, Name):
        self.Name = Name
        self.Tokens = []
        self.SpeculationInstances = []
        Person.AllPeople.append(self)

    def __str__ (self):
        sentence = ""
        for SpeculationInstance in self.SpeculationInstances:
            sentence = sentence +f"{self.Name} has {self.TotalPositiveTokens(SpeculationInstance)} Positive Tokens and {self.TotalNegativeTokens(SpeculationInstance)} Negative Tokens in {SpeculationInstance.UniqueReferenceName}\n"
        return(sentence[0:-1])

    def AddTokens (self, SpeculationInstance, Investment, PredictionBool):
        Amount = SpeculationInstance.SlowMintLoop(Investment, PredictionBool)
        TokenInstance = SpeculationInstance.CreateToken(Amount, PredictionBool)
        if all(Spec != SpeculationInstance for Spec in self.SpeculationInstances):
            self.SpeculationInstances.append(SpeculationInstance)
        self.Tokens.append(TokenInstance)

    def TotalPositiveTokens(self, SpeculationInstance):
        sum = 0
        for obj in self.Tokens:
            if any(token.UniqueReferenceNumber == obj.UniqueReferenceNumber for token in SpeculationInstance.AllTokens):
                if obj.PredictionBool:
                    sum += obj.Amount
        return sum

    def TotalNegativeTokens(self, SpeculationInstance):
        sum = 0
        for obj in self.Tokens:
            if any(token.UniqueReferenceNumber == obj.UniqueReferenceNumber for token in SpeculationInstance.AllTokens):
                if not obj.PredictionBool:
                    sum += obj.Amount
        return sum

    def CashOut(self, SpeculationInstance, OutcomeBool):
        if OutcomeBool:
            return (SpeculationInstance.TotalInvested * self.TotalPositiveTokens(SpeculationInstance)/SpeculationInstance.TotalPositiveTokens())
        elif not OutcomeBool:
            return (SpeculationInstance.TotalInvested * self.TotalNegativeTokens(SpeculationInstance)/SpeculationInstance.TotalNegativeTokens())
        else:
            return(0)


#---------------------------------------------------------------


#Tests----------------------------------------------------------
'''
#Token Initialisation Test
AdamsTokens = Token(10, True)
print(AdamsTokens.Name)
'''

'''
#Speculation Initialisation Test
Providence = Speculation("PRO")
print(Providence.TotalTokens())
'''

'''
#Functionality Test
Providence = Speculation("PRO")
Adam = Person("Adam")
Bob = Person("Bob")
Charlie = Person("Charlie")
Adam.AddTokens(Providence, 1000000, True)
Adam.AddTokens(Providence,1000, False)
Bob.AddTokens(Providence, 1000, False)
Charlie.AddTokens(Providence, 1000, False)
print(Providence)
for person in Person.AllPeople:
    print(person)
for person in Person.AllPeople:
    print(f"{person.Name} earns {person.CashOut(Providence,False)}")
'''

#---------------------------------------------------------------
