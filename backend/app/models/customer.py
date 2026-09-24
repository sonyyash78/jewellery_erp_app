"""Compatibility shim — Stack B modules import Customer from here.
Use the CRM/MySQL Customer model so invoices FKs resolve against the live table.
"""
from app.models.crm import Customer

__all__ = ["Customer"]
