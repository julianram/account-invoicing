# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

import logging


_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        vals = {}
        for line in self.invoice_line_ids:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
            }
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
            })
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in self.invoice_line_ids:
            line.update(vals[line])
        return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
    )

    @api.multi
    @api.depends('discount2', 'discount3')
    def _compute_price(self):
        self.invalidate_cache(
            fnames=['discount2','discount3'],
            ids=self.ids)
        prev_values = dict()
        _logger.info("<<<< GUARDA CACHE >>>>>")
        for line in self:
            prev_values[line] = dict(
                price_unit=line.price_unit,
                discount= line.discount,
                discount2=line.discount2,
                discount3=line.discount3,
            )
            _logger.info(prev_values)
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line._cache.update({
                'price_unit': price_unit ,
                'discount': 0.0,
            })
            super(AccountInvoiceLine, line)._compute_price()
        self.invalidate_cache(
            fnames=['discount2', 'discount3'],
            ids=[l.id for l in list(prev_values.keys())])
        for line, prev_vals_dict in list(prev_values.items()):
            _logger.info("<<<<< ACTUALIZA CACHE >>>>>")
            _logger.info(line)
            _logger.info(prev_vals_dict)
            line._cache.update(prev_vals_dict)
           
         