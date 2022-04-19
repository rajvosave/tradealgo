from AlgorithmImports import *
class SampleAlgorithm(QCAlgorithm):
    stopMarketTicket1 = None
    stopMarketTicket2 = None
    stopMarketOrderFillTime = datetime.day
    HighestSellPrice = 0
    HighestBuyPrice = 0
    StopLimit = 0.97
    TradingQuantity = 10000
    BuyTicketID = 0
    SellTicketID = 0
    BuyPrice = 0
    SellPrice = 0
    
    def Initialize(self):
        self.SetStartDate(2021, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.SetCash(self.TradingQuantity*10)
        self.selleurusd = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda).Symbol
        self.buyeurusd = self.AddForex("EURUSD", Resolution.Hour, Market.FXCM).Symbol
        self.entryTicket = None
        self.stopMarketTicket = None
        #self.SetBenchmark("EURUSD")
        self.SetBrokerageModel(BrokerageName.OandaBrokerage,AccountType.Margin)
        
    def OnData(self, data):
        
        # Plot the current eurusd price to "Data Chart" on series "Asset Price"
        #self.Plot("Data Chart", "Asset Price", self.Securities['EURUSD'].Close)

        #If nothing in Portfolio, Open Long and Short positions        
        if not self.Portfolio.Invested:
            #Open Long Position
            self.buyticket = self.MarketOrder(self.buyeurusd, self.TradingQuantity, True)
            self.BuyPrice = data[self.buyeurusd].Close
            self.stopMarketTicket1 = self.StopMarketOrder(self.buyeurusd, -self.TradingQuantity, self.StopLimit*self.BuyPrice)
            self.BuyTicketID = self.stopMarketTicket1.OrderId
            self.HighestBuyPrice = self.BuyPrice
            self.Log("Buyorder @" + str(self.BuyTicketID) + " at price: " + str(self.BuyPrice))
            #Open Short Position
            self.sellticket = self.MarketOrder(self.selleurusd,-self.TradingQuantity, True)
            self.SellPrice = data[self.selleurusd].Open
            self.stopMarketTicket2 = self.StopMarketOrder(self.selleurusd, self.TradingQuantity, self.StopLimit*self.SellPrice)
            self.SellTicketID = self.stopMarketTicket2.OrderId
            self.Log("SellOrder @" + str(self.SellTicketID) + " at price: " + str(self.SellPrice))
            
        else:
            #If Long position still open
            if self.ActiveSecurities[self.buyeurusd].Invested:
                if data[self.buyeurusd].Close > self.HighestBuyPrice:
                    self.HighestBuyPrice = data[self.buyeurusd].Close
                    #self.stopMarketTicket = self.StopMarketOrder(self.buyeurusd, -self.TradingQuantity, self.HighestBuyPrice*self.StopLimit)
                    updateFields = UpdateOrderFields()
                    updateFields.StopPrice = self.HighestBuyPrice * self.StopLimit
                    self.stopMarketTicket1.Update(updateFields) 
            
            #If Short position still open
            if self.ActiveSecurities[self.selleurusd].Invested:
                if data[self.selleurusd].Open > self.HighestSellPrice:
                    self.HighestSellPrice = data[self.selleurusd].Open
                    #self.stopMarketTicket2 = self.StopMarketOrder(self.selleurusd, self.TradingQuantity, self.HighestSellPrice*self.StopLimit)
                    updateFields = UpdateOrderFields()
                    updateFields.StopPrice = self.HighestBuyPrice * self.StopLimit
                    self.stopMarketTicket2.Update(updateFields) 

            
            # Plot the moving stop price on "Data Chart" with "Stop Price" series name
            #self.Plot("Data Chart", "HighestBuyPrice", self.HighestBuyPrice)
            #self.Plot("Data Chart", "HighestSellPrice", self.HighestSellPrice)     
            
            #if self.Securities["EURUSD"].Close > self.highestPrice:    
            #    self.highestPrice = self.Securities["EURUSD"].Close
            #    updateFields = UpdateOrderFields()
            #    updateFields.StopPrice = self.highestPrice * self.stoplimit
            #    self.stopMarketTicket.Update(updateFields) 
            
    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        if orderEvent.Status != OrderStatus.Filled: 
            self.Log("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent, OrderStatus))
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        #Long position reached TAKE LOSS, increase Take loss for short position
        if orderEvent.OrderId == self.BuyTicketID: 
            self.stopMarketTicket1 = self.StopMarketOrder(self.selleurusd, self.TradingQuantity, self.SellPrice*1.04)
            self.Debug("Long position closed, Take Loss for Short position set at: " + str(self.SellPrice * 1.04))

        #Short position reached TAKE LOSS
        if orderEvent.OrderId == self.SellTicketID: 
            self.stopMarketTicket2 = self.StopMarketOrder(self.buyeurusd, self.TradingQuantity, self.BuyPrice*1.04)
            self.Debug("Short position closed, Take Loss for Long position set at: " + str(self.BuyPrice * 1.04))
        
        
