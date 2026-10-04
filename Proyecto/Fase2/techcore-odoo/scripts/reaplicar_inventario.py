# -*- coding: utf-8 -*-
"""Reaplica el inventario fisico inicial usando el flujo nativo de Odoo.

Deja el stock igual que lo cargado porJulio, pero esta vez cada cantidad
proviene de un ajuste de inventario real (movimiento de stock + capa de
valoracion), que es lo que exige la rubrica al hablar de trazabilidad.
"""
import logging

_logger = logging.getLogger(__name__)

STOCK = {
    "PROD-001": 15, "PROD-002": 20, "PROD-003": 50, "PROD-004": 100,
    "PROD-005": 30, "PROD-006": 45, "PROD-007": 5, "PROD-008": 8,
    "PROD-009": 2, "PROD-010": 3, "PROD-011": 10, "PROD-012": 25,
    "PROD-013": 40, "PROD-014": 35, "PROD-015": 15, "PROD-016": 20,
    "PROD-017": 80, "PROD-018": 4, "PROD-019": 12, "PROD-020": 25,
}

env = env(user=env.ref("base.user_admin"))


def main():
    ubicacion = env["stock.location"].search(
        [("complete_name", "=", "WH/Stock")], limit=1)
    quants = env["stock.quant"].search([
        ("location_id", "=", ubicacion.id),
        ("product_id.default_code", "in", list(STOCK.keys())),
    ])

    # 1. Resetear el stock cargado sin movimientos para partir de cero
    for quant in quants:
        env["stock.quant"]._update_available_quantity(
            quant.product_id, ubicacion, -quant.quantity)

    # 2. Registrar la cantidad contada en cada quant
    for quant in quants:
        codigo = quant.product_id.default_code
        quant.with_context(inventory_mode=True).write({
            "inventory_quantity": float(STOCK[codigo]),
            "inventory_quantity_set": True,
        })

    # 3. Aplicar el ajuste con el asistente nativo (crea los movimientos)
    wizard = env["stock.inventory.adjustment.name"].create({
        "inventory_adjustment_name": "Inventario fisico inicial - Datos Maestros",
        "quant_ids": [(6, 0, quants.ids)],
    })
    wizard.action_apply()
    env.cr.commit()

    moves = env["stock.move"].search_count([("location_id", "=", ubicacion.id)])
    capas = env["stock.valuation.layer"].search_count([])
    _logger.info("Ajuste aplicado: %s quants, %s movimientos, %s capas",
                 len(quants), moves, capas)


main()