# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

from erpnext.stock.doctype.stock_entry import stock_entry

from real_fitness.controllers import overrides

class StockEntry(stock_entry.StockEntry):
	@overrides
	def on_submit(self):
		# keep the original behavior
		super(StockEntry, self).on_submit()

		# do something else
		self.validate_correct_transfer_to_cabins()
		self.create_second_stock_entry()

	def validate_correct_transfer_to_cabins(self):
		"""Ensure that Transfers sent to cabins go 
		through a Transit Warehouse (transit warehouse specified in 
		the Warehouse profile must be used here as well)"""
		if self.purpose != "Material Transfer":
			return # validate only material transfers for now

		self._validate_correct_transfer_to_cabins(
			self.from_warehouse,
			self.to_warehouse,
		)

		self._validate_correct_transfer_to_cabins(
			self.to_warehouse,
			self.from_warehouse,
		)

	def _validate_correct_transfer_to_cabins(self, cabin_warehouse, other_warehouse):
		warehouse_details = self.get_cabin_warehouse_details(
			cabin_warehouse
		)

		if warehouse_details.get("warehouse_type") != "Cabin":
			return # don't validate for non-cabin warehouses

		if not warehouse_details.get("default_in_transit_warehouse"):
			frappe.throw(
				"El almacén de tránsito no está configurado para la cabina",
				title="Error",
			)

		if other_warehouse != warehouse_details.get("default_in_transit_warehouse"):
			frappe.throw(
				f"Se ha detectado que no esta usando el almacén de tránsito configurado para la cabina {cabin_warehouse!r}",
				title="Error",
			)

	@staticmethod
	def get_cabin_warehouse_details(warehouse):
		"""Get the Transit Warehouse for a Cabin"""
		doctype = "Warehouse"
		name = warehouse
		fields = (
			"default_in_transit_warehouse",
			"warehouse_type",
		)

		return frappe.get_value(
			doctype, name, fields, as_dict=True
		)

	def create_second_stock_entry(self):
		"""Create a second Stock Entry 
		if this is a Material Transfer for a Cabin"""

		# EXECUTION PLAN
		# 1. check if this is a Material Transfer for a Cabin
		# 2. if it is, create a second Stock Entry
		# 3. set the second Stock Entry is created as draft

		# a Material Transfer for a Cabin is identified as mix of values
		# from the following fields:
		# 1. stock_entry_type must be equals "Transferencia a Cabina"
		# 2. target_cabin must be set
		# 3. relates_to must be empty (because if it set, it means it is the second Stock Entry)

		if not self.is_transfer_to_cabin():
			return # nothing to do here

		# create a new Stock Entry
		doc = frappe.copy_doc(self)

		doc.from_warehouse = self.to_warehouse
		doc.to_warehouse = self.target_cabin
		doc.relates_to = self.name
		doc.target_cabin = None
		doc.outgoing_stock_entry = None

		# update the items table
		for d in doc.get("items"):
			d.s_warehouse = doc.from_warehouse
			d.t_warehouse = doc.to_warehouse

		doc.save()
		doc.add_comment(
			"Edit",
			"Este documento ha sido creado automáticamente por el sistema",
		)

	def is_transfer_to_cabin(self):
		"""Check if this is a Material Transfer for a Cabin"""
		return self.stock_entry_type == "Transferencia a Cabina" \
			and self.target_cabin and not self.relates_to
