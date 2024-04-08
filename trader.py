from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            print("PRODUCT: ",product)
            order_depth: OrderDepth = state.order_depths[product]
            try: position: int = state.position[product]
            except: position = 0
            # if product == "AMETHYSTS": result[product] = self.handleAmethysts(order_depth=order_depth, product=product, position=position)
            if product == "STARFRUIT": result[product],state.traderData = self.handleStarfruit(order_depth=order_depth, product=product, position=position, state=state)
            

        # String value holding Trader state data required. 
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 

        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData

    def handleAmethysts(self, order_depth: OrderDepth, product: string, position: int):
        LIMIT = 20
        print("POSITION: ",position)
        
        orders: List[Order] = []
        acceptable_price = 10000  # Participant should calculate this value
        # print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        max_buy_amount = LIMIT - position
        max_sell_amount = LIMIT + position 

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            print("Best bid: ",best_bid)
            if int(best_bid) > acceptable_price:
                bid_amount = min(best_bid_amount, max_sell_amount)
                print("SELL", str(bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -bid_amount))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            print("Best ask: ",best_ask)
            if int(best_ask) < acceptable_price:
                ask_amount = min(best_ask_amount,max_buy_amount)
                print("BUY", str(-ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -ask_amount))

        return orders
 
    def handleStarfruit(self, order_depth: OrderDepth, product: string, position: int, state: TradingState):
        LIMIT = 20
        print("POSITION: ",position)
        
        mid_price_ma_info = list(state.traderData.split(","))
        if len(mid_price_ma_info) < 2: mid_price_ma_info = [5000, 25000]
        else: mid_price_ma_info = [int(item) for item in mid_price_ma_info]

        acceptable_price = int(mid_price_ma_info[1])/5  # Participant should calculate this value

        orders: List[Order] = []
        mid_price: int = 0

        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        max_buy_amount = LIMIT - position
        max_sell_amount = LIMIT + position 

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            mid_price+=best_bid

            print("Best bid: ",best_bid)
            if int(best_bid) > acceptable_price:
                bid_amount = min(best_bid_amount, max_sell_amount)
                print("SELL", str(bid_amount) + "x", best_bid)
                orders.append(Order(product, best_bid, -bid_amount))

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            mid_price += best_ask

            print("Best ask: ",best_ask)
            if int(best_ask) < acceptable_price:
                ask_amount = min(best_ask_amount,max_buy_amount)
                print("BUY", str(-ask_amount) + "x", best_ask)
                orders.append(Order(product, best_ask, -ask_amount))

        mid_price = mid_price / 2
        mid_price_ma_info[1] = mid_price_ma_info[1] - mid_price_ma_info[0] + mid_price
        mid_price_ma_info[0] = mid_price
        my_state = ",".join([str(item) for item in mid_price_ma_info])

        return orders,my_state