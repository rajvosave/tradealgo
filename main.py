from AlgorithmImports import *
class SampleAlgorithm(QCAlgorithm):
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    highestSPYPrice = -1
    
    def Initialize(self):
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2022, 1, 4)
        self.SetCash(100000)
        spy = self.AddForex("EURUSD", Resolution.Minute)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        # Plot the current SPY price to "Data Chart" on series "Asset Price"
        self.Plot("Data Chart", "Asset Price", self.Securities['EURUSD'].Close)
        
        
        if not self.Portfolio.Invested:
            self.ticket = self.MarketOrder("EURUSD", 100000)
            self.stopMarketTicket = self.StopMarketOrder("EURUSD", -100000, 0.98 * self.Securities["EURUSD"].Close)
            
        else:
        
            # Plot the moving stop price on "Data Chart" with "Stop Price" series name
            self.Plot("Data Chart", "Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))     
            
            if self.Securities["EURUSD"].Close > self.highestSPYPrice:    
                self.highestSPYPrice = self.Securities["EURUSD"].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestSPYPrice * 0.99
                self.stopMarketTicket.Update(updateFields) 
            
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
