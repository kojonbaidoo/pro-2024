from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle

class Trader:
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        my_trader_data = {"STARFRUIT":[], "AMETHYSTS":[]}

        if len(state.traderData) != 0:
            my_trader_data = jsonpickle.decode(state.traderData)

        for product in state.order_depths:
            print("PRODUCT: ",product)
            order_depth: OrderDepth = state.order_depths[product]
            try: position: int = state.position[product]
            except: position = 0
            if product == "AMETHYSTS": result[product] = self.handleAmethysts(order_depth=order_depth, product=product, position=position)
            if product == "STARFRUIT":
                result[product],my_trader_data["STARFRUIT"] = self.handleStarfruit(order_depth=order_depth, product=product, position=position, mid_price_ma_info=my_trader_data["STARFRUIT"])
            

        # String value holding Trader state data required. 
        # It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(my_trader_data) 

        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData

    def handleAmethysts(self, order_depth: OrderDepth, product: string, position: int):
        LIMIT = 10
        print("POSITION: ",position)
        
        orders: List[Order] = []
        acceptable_price = 10000  # Participant should calculate this value
        acceptable_sell = 10002
        acceptable_buy = 9998
        # print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        max_buy_amount = min(LIMIT - position, LIMIT)
        max_sell_amount = min(LIMIT + position, LIMIT) 


        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        print("Best bid: ",best_bid)

        bid_amount = min(best_bid_amount, max_sell_amount)
        print("SELL", str(max_sell_amount) + "x", acceptable_sell)
        orders.append(Order(product, acceptable_sell, -max_sell_amount))


        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        print("Best ask: ",best_ask)

        ask_amount = min(best_ask_amount,max_buy_amount)
        print("BUY", str(max_buy_amount) + "x", acceptable_buy)
        orders.append(Order(product, acceptable_buy, max_buy_amount))

        return orders
 
    def handleStarfruit(self, order_depth: OrderDepth, product: string, position: int, mid_price_ma_info: List):
        LIMIT = 20
        MA_DAYS = 6
        print("POSITION: ",position)
        
        orders: List[Order] = []
        mid_price: int = 0

        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        max_buy_amount = LIMIT - position
        max_sell_amount = LIMIT + position

        best_bid, best_bid_amount = None, None
        best_ask, best_ask_amount = None, None

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            mid_price += best_bid * 0.5
            print("Best bid: ",best_bid)
            
        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            mid_price += best_ask * 0.5
            print("Best ask: ",best_ask)
            
        if len(mid_price_ma_info) == MA_DAYS:

            acceptable_price = sum(mid_price_ma_info) / MA_DAYS

            print("Acceptable price : " + str(acceptable_price))

            if int(best_ask) < acceptable_price:
                ask_amount = min(best_ask_amount,max_buy_amount)
                print("BUY", str(-ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -ask_amount))

            if int(best_bid) > acceptable_price:
                bid_amount = min(best_bid_amount, max_sell_amount)
                print("SELL", str(bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -bid_amount))

            mid_price_ma_info = mid_price_ma_info[1:]

        mid_price_ma_info.append(mid_price)

        return orders, mid_price_ma_info
