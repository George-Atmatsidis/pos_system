# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pn532
import wiegand
import store
import payment_processor


class Controller(object):
    def __init__(self):
        self.wiegand = wiegand.Wiegand26()
        self.pn532 = pn532.PN532()
        self.db = db.DB()
        self.payment_processor = payment_processor.Payment_Processor()

    def setup(self):
        print("controller is setting up")

        self.wiegand.setup()
        self.pn532.setup()
        self.db.setup()
        self.payment_processor.setup()

    def run(self):
        """run the system sequentially (only for demo purposes)
           return False whenever an error is occured to end the session
        """
        print("controller is running")

        # tap a bennington card to start a check out session
        bennington_card = self.wiegand.read()

        # if the card is invalid (not in the db), end the session
        if not self.db.check_card(bennington_card):
            return False

        # scan a number of nfc tags and add them to a cart
        # FIXME - run sequentially, get 3 items for now
        cart = []
        for i in range(3):
            cart.append(self.pn532.read())

        # tap the bennington card again to end the checkout session
        # if the card is not the same card as before, end the session
        if not bennington_card == self.wiegand.read():
            return False

        # get informations for available items in the cart
        items = self.db.get_items(cart)

        if len(items) == 0:
            return False

        # send an invoice to the person
        if not self.payment_processor.send_invoice(bennington_card, items):
            return False

        # create a pending transaction
        # TODO - need to verify transaction once it's paid then update the
        # database again
        transaction_id = self.db.make_sale(bennington_card, items)

        # print out the transaction information
        print("transaction: ", self.db.get_sale(transaction_id))

        # check the availability of the item in the cart again
        # since all of them are sold, there should be no item left to be purchased
		# deprecated!
#        if len(self.db.get_stock(cart)) != 0:
#            return False

        return True
