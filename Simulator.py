import math
import random
#Global Variables-----------------------------------------------
#None
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
        return f"Token {self.UniqueReferenceNumber} is a {self.Name} with Amount: {self.Amount}"

    def ReduceAmount (self, Reduction):
        CurrentAmount = self.Amount
        if self.Amount<Reduction:
            self.Amount=0
            return(Reduction-CurrentAmount)
        else:
            self.Amount=self.Amount-Reduction
            return(0)


class Speculation:
    AllSpeculations = []

    def __init__ (self, UniqueReferenceName, DurationLength):
        self.UniqueReferenceName = UniqueReferenceName
        self.DurationLength = DurationLength
        self.PositiveToken = Token(1, True, self.UniqueReferenceName + "001")
        self.NegativeToken = Token(1, False, self.UniqueReferenceName + "002")
        self.AllTokens = [self.PositiveToken, self.NegativeToken]
        self.TotalInvested = 0
        Speculation.AllSpeculations.append(self)

    def __str__ (self):
        return(f"{self.UniqueReferenceName} Total Invested: {self.TotalInvested}\n{self.UniqueReferenceName} Total Tokens: {self.TotalTokens()}\n{self.UniqueReferenceName} Total Positive Tokens: {self.TotalPositiveTokens()}\n{self.UniqueReferenceName} Total Negative Tokens: {self.TotalNegativeTokens()}")

    def MintToken (self, Time, Amount, PredictionBool, Person):
        if self.SwappingMultiplier(Time, PredictionBool)<=1 or self.TotalTokens()==2:
            return(self.CreateToken(Amount, PredictionBool))

        elif self.SwappingMultiplier(Time, PredictionBool)>1:
            OppositePredictionBool = not PredictionBool
            Person.AddTokens(Time, self, Amount, OppositePredictionBool)
            Output = Person.SwapTokens(self, Time, Amount, PredictionBool)

            #below is here because the output above is none but i can't work out why
            if Output == None:
                Output = self.AllTokens[-1]
            return(Output)

        else:
            return(False)

    def CreateToken (self, Amount, PredictionBool):
        if len(self.AllTokens) < 10:
            number = "00"+str(len(self.AllTokens)+1)
        elif len(self.AllTokens) < 100:
            number = "0" +str(len(self.AllTokens)+1)
        else:
            number = str(len(self.AllTokens)+1)

        self.Token = Token(Amount,PredictionBool, self.UniqueReferenceName + number)
        self.AllTokens.append(self.Token)
        return(self.Token)

    def FindToken (self, UniqueReferenceNumber):
        target_token = None
        for token in self.AllTokens:
            if token.UniqueReferenceNumber == UniqueReferenceNumber:
                target_token = token
                return target_token

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

    def Sigmoid (self, Time):
        if Time<0:
            return("Invalid Time")
        elif Time<self.DurationLength/2:
            return(1-8*(Time/self.DurationLength)**4)
        elif Time<=self.DurationLength:
            return(8*((Time/self.DurationLength)-1)**4)
        else:
            return("Invalid Time")

    def SwappingMultiplier(self, Time, PredictionBool):
        CurrentExchangeRate = max(self.TotalPositiveTokens()/self.TotalNegativeTokens(),self.TotalNegativeTokens()/self.TotalPositiveTokens())
        p = 1/CurrentExchangeRate
        a = 2*(1-p+math.sqrt(1-p))
        TimeDampeningFunction = p + a*(Time/self.DurationLength) - (a+p)*(Time/self.DurationLength)**2
        if PredictionBool:
            if self.TotalNegativeTokens() <= self.TotalPositiveTokens():
                return(self.Sigmoid(Time)*p/TimeDampeningFunction)
            else:
                return(self.Sigmoid(Time)*TimeDampeningFunction/p)
        elif not PredictionBool:
            if self.TotalPositiveTokens() <= self.TotalNegativeTokens():
                return(self.Sigmoid(Time)*p/TimeDampeningFunction)
            else:
                return(self.Sigmoid(Time)*TimeDampeningFunction/p)
        else:
            return("Invalid PredictionBool")

    def SwapTokens (self, Person, Time, SwapAmount, NewPredictionBool):
        OldPredictionBool = not NewPredictionBool
        if OldPredictionBool:
            if Person.TotalPositiveTokens(self)<SwapAmount:
                return(False)
            else:
                MintAmount = self.SwappingMultiplier(Time, NewPredictionBool)*SwapAmount
                Person.BurnTokens(self, SwapAmount, OldPredictionBool)
                Output = self.CreateToken( MintAmount, NewPredictionBool)
                #print(Output)
                return(Output)
        else:
            if Person.TotalNegativeTokens(self)<SwapAmount:
                return(False)
            else:
                MintAmount = self.SwappingMultiplier(Time, NewPredictionBool)*SwapAmount
                Person.BurnTokens(self, SwapAmount, OldPredictionBool)
                Output = self.CreateToken( MintAmount, NewPredictionBool)
                #print(Output)
                return(Output)

    def Quotient(self):
        return (self.TotalPositiveTokens()/self.TotalNegativeTokens())


class Person:
    AllPeople = []

    def __init__ (self, Name):
        self.Name = Name
        self.Tokens = []
        self.SpeculationInstances = []
        self.InvestmentStrategies = []
        Person.AllPeople.append(self)

    def __str__ (self):
        sentence = ""
        for SpeculationInstance in self.SpeculationInstances:
            sentence = sentence +f"{self.Name} has {self.TotalPositiveTokens(SpeculationInstance)} Positive Tokens and {self.TotalNegativeTokens(SpeculationInstance)} Negative Tokens in {SpeculationInstance.UniqueReferenceName}\n"
        return(sentence[0:-1])

    def AddTokens (self, Time, SpeculationInstance, Amount, PredictionBool,):
        TokenInstance = SpeculationInstance.MintToken(Time, Amount, PredictionBool, self)
        if all(Spec != SpeculationInstance for Spec in self.SpeculationInstances):
            self.SpeculationInstances.append(SpeculationInstance)
        self.Tokens.append(TokenInstance)

    def MintTokens (self, Time, SpeculationInstance, Investment, PredictionBool):
        self.AddTokens (Time, SpeculationInstance, Investment, PredictionBool)
        SpeculationInstance.TotalInvested += Investment

    def AddInvestmentStrategy(self, SpeculationInstance, PerceivedOdds, RiskLevel):
        self.InvestmentStrategies.append(InvestingStrategy(RiskLevel, PerceivedOdds, self, SpeculationInstance))

    def TotalPositiveTokens(self, SpeculationInstance):
        sum = 0
        if len(self.Tokens)>0:
            for obj in self.Tokens:
                if any(token.UniqueReferenceNumber == obj.UniqueReferenceNumber for token in SpeculationInstance.AllTokens):
                    if obj.PredictionBool:
                        sum += obj.Amount
        return sum

    def TotalNegativeTokens(self, SpeculationInstance):
        if len(self.Tokens)>0:
            sum = 0
            for obj in self.Tokens:
                if any(token.UniqueReferenceNumber == obj.UniqueReferenceNumber for token in SpeculationInstance.AllTokens):
                    if not obj.PredictionBool:
                        sum += obj.Amount
        return sum

    def FindToken (self, UniqueReferenceNumber):
        target_token = None
        for token in self.Tokens:
            if token.UniqueReferenceNumber == UniqueReferenceNumber:
                target_token = token
                return target_token

    def BurnTokens (self, SpeculationInstance, BurnAmount, PredictionBool):
        RunningTotal = BurnAmount
        if PredictionBool:
            if self.TotalPositiveTokens(SpeculationInstance)<BurnAmount:
                return("Not enough tokens")
            else:
                for token in self.Tokens:
                    if token.PredictionBool == PredictionBool:
                        RunningTotal = token.ReduceAmount(RunningTotal)
        elif  not PredictionBool:
            if self.TotalNegativeTokens(SpeculationInstance)<BurnAmount:
                return("Not enough tokens")
            else:
                for token in self.Tokens:
                    if token.PredictionBool == PredictionBool:
                        RunningTotal = token.ReduceAmount(RunningTotal)
        else:
            return("Incorrect outcome selection")

    def CashOut(self, SpeculationInstance, OutcomeBool):
            if OutcomeBool:
                return (SpeculationInstance.TotalInvested * self.TotalPositiveTokens(SpeculationInstance)/SpeculationInstance.TotalPositiveTokens())
            elif not OutcomeBool:
                return (SpeculationInstance.TotalInvested * self.TotalNegativeTokens(SpeculationInstance)/SpeculationInstance.TotalNegativeTokens())
            else:
                return(0)

    def SwapTokens (self, SpeculationInstance, Time, SwapAmount, NewPredictionBool):
        TokenInstance = SpeculationInstance.SwapTokens(self, Time, SwapAmount, NewPredictionBool)

    def FindInvestmentStrategy (self, SpeculationInstance):
        TargetStrategy = None
        for Strategy in self.InvestmentStrategies:
            if Strategy.SpeculationInstance.UniqueReferenceName == SpeculationInstance.UniqueReferenceName:
                TargetStrategy = Strategy
                return(TargetStrategy)


class InvestingStrategy:
    AllInvestingStrategies = []

    def __init__(self, RiskLevel, PerceivedOdds, Person, SpeculationInstance):
        self.RiskLevel = RiskLevel # 1 Low risk picking right at the end  2 Wait and see strategy (mid)  3 Assertive to manage the portfolio throughout
        self.PerceivedOdds = PerceivedOdds #Yes/No Yes more likely over 1 No more likely under 1
        self.Person = Person
        self.SpeculationInstance = SpeculationInstance
        self.UniqueReferenceName = str(Person.Name +SpeculationInstance.UniqueReferenceName)
        InvestingStrategy.AllInvestingStrategies.append(self)

    def __str__ (self):
        return(f"{self.Person} has a Risk Level of {self.RiskLevel} in {self.SpeculationInstance} with Perceived Odds of {self.PerceivedOdds}")

    def Investment(self, Time):
        PriceRatio = max(self.SpeculationInstance.SwappingMultiplier(Time, False),1)/max(self.SpeculationInstance.SwappingMultiplier(Time, True),1)
        InitialPhase = self.SpeculationInstance.SwappingMultiplier(Time, False)>1 or self.SpeculationInstance.SwappingMultiplier(Time, True)>1
        TokenRatio = self.SpeculationInstance.TotalPositiveTokens()/self.SpeculationInstance.TotalNegativeTokens()
        if self.RiskLevel == 1:
            if InitialPhase:
                if PriceRatio < self.PerceivedOdds:
                    return(1)
                elif PriceRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)

            else:
                if TokenRatio < self.PerceivedOdds:
                    return(1)
                elif TokenRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)
        elif self.RiskLevel == 2:
            if InitialPhase:
                if PriceRatio < self.PerceivedOdds:
                    return(1)
                elif PriceRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)
            else:
                if TokenRatio < self.PerceivedOdds:
                    return(1)
                elif TokenRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)
        elif self.RiskLevel == 3:
            if InitialPhase:
                #print(f"PriceRatio: {PriceRatio}")
                if PriceRatio < self.PerceivedOdds:
                    return(1)
                elif PriceRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)

            else:
                #print(f"TokenRatio: {TokenRatio}")
                if TokenRatio < self.PerceivedOdds:
                    return(1)
                elif TokenRatio > self.PerceivedOdds:
                    return(-1)
                else:
                    return(0)
        else:
            return(False)

    def MintingStrategy (self, Time, Amount):
        InvestmentAmount = self.Investment(Time)*Amount
        #print(f"InvestmentAmount: {InvestmentAmount}")
        if InvestmentAmount == 0:
            pass
        elif InvestmentAmount>0:
            self.Person.MintTokens(Time, self.SpeculationInstance, InvestmentAmount, True)
        elif InvestmentAmount<0:
            self.Person.MintTokens(Time, self.SpeculationInstance, abs(InvestmentAmount), False)
        else:
            return("Invalid InvestmentAmount")


#---------------------------------------------------------------


#Tests----------------------------------------------------------

def FunctionalityTest():
    Providence = Speculation("PRO", 100)
    Adam = Person("Adam")
    Bob = Person("Bob")
    Charlie = Person("Charlie")
    Adam.MintTokens(1, Providence, 100, True)
    Bob.MintTokens(2, Providence, 100, True)
    Charlie.MintTokens(3, Providence, 20, False)
    Bob.MintTokens(4, Providence, 100, True)

    print(Adam)
    print(Bob)
    print(Charlie)

def NormalcyTesting ():
    Providence = Speculation("PRO", 100)
    AverageUsers = Person("AverageUsers")
    Duration = Providence.DurationLength
    CurrentTime = 0
    # early stage still needs work
    while CurrentTime < Duration:
        QuotientNumber = 2
        CurrentTime += 1
        #PositiveToken
        AverageUsers.MintTokens(Providence, 100*QuotientNumber/(QuotientNumber+1), True)
        #NegativeTokens
        if Providence.SwappingMultiplier(CurrentTime,False)>=1:
            AverageUsers.MintTokens(Providence, 100/(QuotientNumber+1), True)
            if Providence.Quotient()>QuotientNumber:
                SwapAmount = (Providence.TotalPositiveTokens()-Providence.TotalNegativeTokens())/(QuotientNumber + 1)
                Providence.SwapTokens(AverageUsers,CurrentTime,SwapAmount,False)
        else:
            AverageUsers.MintTokens(Providence, 100/(QuotientNumber+1), False)
        print(CurrentTime)
        print(Providence)
    for person in Person.AllPeople:
        print(person)
    for person in Person.AllPeople:
        print(f"{person.Name} earns {person.CashOut(Providence,True)}")

def NormalcyTesting2 ():
    Providence = Speculation("PRO", 100)
    CautiousUsers = Person("CautiousUsers")
    AverageUsers = Person("AverageUsers")
    AgressiveUsers = Person("AgressiveUsers")
    CautiousUsers.AddInvestmentStrategy(Providence, 0.25, 1)
    AverageUsers.AddInvestmentStrategy(Providence, 0.25, 2)
    AgressiveUsers.AddInvestmentStrategy(Providence, 0.25, 3)
    Duration = Providence.DurationLength
    CurrentTime = 0
    while CurrentTime < Duration-1:
        CurrentTime += 1
        #print(Providence.UniqueReferenceName)
        CautiousUsers.FindInvestmentStrategy(Providence).MintingStrategy(CurrentTime, 100)
        AverageUsers.FindInvestmentStrategy(Providence).MintingStrategy(CurrentTime, 100)
        AgressiveUsers.FindInvestmentStrategy(Providence).MintingStrategy(CurrentTime, 100)
        print(f"CurrentTime: {CurrentTime}")
        for person in Person.AllPeople:
            print(person)
        print(" ")
    for person in Person.AllPeople:
        print(f"{person.Name} earns {person.CashOut(Providence,True)}")

#---------------------------------------------------------------
#FunctionalityTest()
#NormalcyTesting()
NormalcyTesting2()
