# -*- coding: utf-8 -*-

from flask import Flask, render_template
import tag_reader
import card_reader
import db
import payment_processor

class Server(object):
	def __init__(self):
		self.app = Flask(__name__)
		self.tag_reader = tag_reader.PN532()
		self.card_reader = card_reader.Wiegand()
		self.db = db.DB()
		self.payment_processor = payment_processor.PaymentProcessor()

	def setup(self, sim=False):
		self.app.secret_key = 'yagabeatsTHO'
		if sim:
			self.tag_reader.sim_setup()
			self.card_reader.sim_setup()
		else:
			self.tag_reader.setup()
			self.card_reader.setup()
		self.db.setup()
		self.payment_processor.setup()

		@self.app.route('/')
		def index():
			return render_template("index.html.j2", variable="Oy")

	def start(self, sim=False):
		self.app.run(debug=True)

	def run(self, sim=False):
		"""
		run the pos_system
		"""

		# we use a dictionary to ensure the uniqueness of a tag
		tags = {}

		# cart loop
		while True:
			# check for a tag reading
			tag = self.tags.read()

			# check if the item exists
			item = self.db.get_item(tag)
			if item is not None:

				# add the item to the cart
				tags.append(tag)

				# send the tag's item to the ui
				self.ui.add_item(item)
			else:
				print("That tag can't be found in stock")

		# check for a card reading
		card = self.card.read()

		if self.db.check_card(card):
			# collect all the items
			items = self.db.get_items(tags)

			# make the sale
			sale = self.db.make_sale(card, tags)

			# update the ui
			self.ui.checkout(sale, items)

			# send invoice to the customer
			card_info = self.db.get_buyer(card)
			name = card_info.get("name")
			email = card_info.get("email")
			charge_id = self.payment_processor.send_invoice(name, email, items)

			# print(self.payment_processor.get_charge(charge_id))

			# FIXME - check if it's paid
			# realistically would check it later
			if self.payment_processor.is_paid(charge_id):
				print(name, "has paid")

			# FIXME - add logic to update the stock after an item is purchased
		else:
			self.ui.card_error();
