# -*- coding: utf-8 -*-
"""Actualiza los clientes con los datos de 2_Clientes_Odoo.xlsx y los marca
como clientes (customer_rank) para que aparezcan en Ventas/Cotizaciones.
"""
import logging

_logger = logging.getLogger(__name__)

CLIENTES = [
    # nombre, email, telefono, direccion, es_empresa, categoria
    ("Juan Pérez", "juan.perez@gmail.com", "+502 5555-1111",
     "Zona 10, Ciudad de Guatemala", False, "B2C"),
    ("María López", "mlopez@estudiante.usac.edu.gt", "+502 4444-2222",
     "Zona 1, Ciudad de Guatemala", False, "B2C"),
    ("TechCorp S.A.", "compras@techcorp.com.gt", "+502 2222-3333",
     "Zona 14, Ciudad de Guatemala", True, "B2B"),
    ("Innova Solutions", "info@innovasolutions.gt", "+502 2333-4444",
     "Zona 4, Ciudad de Guatemala", True, "B2B"),
    ("Carlos Ruiz", "cruiz99@hotmail.com", "+502 5666-7777",
     "Mixco, Guatemala", False, "B2C"),
]

env = env(user=env.ref("base.user_admin"))


def main():
    pais = env["res.country"].search([("name", "=", "Guatemala")], limit=1)
    b2c = env["res.partner.category"].search([("name", "=", "B2C")], limit=1)
    if not b2c:
        b2c = env["res.partner.category"].create({"name": "B2C"})
    b2b = env["res.partner.category"].search([("name", "=", "B2B")], limit=1)

    for nombre, email, telefono, direccion, es_empresa, categoria in CLIENTES:
        partner = env["res.partner"].search([("name", "=", nombre)], limit=1)
        if not partner:
            continue
        categoria_rec = b2b if categoria == "B2B" else b2c
        vals = {
            "email": email,
            "phone": telefono,
            "street": direccion,
            "is_company": es_empresa,
            "company_type": "company" if es_empresa else "person",
            "customer_rank": 1,
            "category_id": [(4, categoria_rec.id)],
        }
        if pais:
            vals["country_id"] = pais.id
        partner.write(vals)
        _logger.info("Cliente actualizado: %s (%s, %s)",
                     partner.name, categoria, email)
    env.cr.commit()


main()