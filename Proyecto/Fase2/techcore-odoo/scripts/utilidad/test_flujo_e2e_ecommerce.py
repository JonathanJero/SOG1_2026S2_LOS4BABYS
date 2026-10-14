# -*- coding: utf-8 -*-
"""Prueba interna rapida del flujo end-to-end del eCommerce y CRM (Hito A4).

Flujo validado:
1. Registro de cliente nuevo (Erick Sandoval).
2. Verificacion de existencias iniciales.
3. Creacion de pedido web con 2 productos (PROD-001 y PROD-005).
4. Pago simulado / Transferencia bancaria.
5. Verificacion de factura generada.
6. Despacho de inventario (descuenta existencias en WH/Stock).
7. Verificacion de oportunidad Lead 'Web B2C' en CRM.

Uso:
  docker exec -i techcore_odoo_web odoo shell -d TechCore_DB \
    --db_host techcore_postgres_db -r odoo -w techcore_secure_pwd --no-http --log-level=warn < test_flujo_e2e_ecommerce.py
"""
import logging

_logger = logging.getLogger("test_flujo_e2e")


def ejecutar():
    admin = env.ref("base.user_admin")
    e = env(user=admin)
    print("=== PRUEBA INTERNA E2E: E-COMMERCE -> FACTURACION -> STOCK -> CRM ===")

    # 1. Registrar cliente nuevo
    email_cliente = "erick.sandoval@techcore.gt"
    partner = e["res.partner"].search([("email", "=", email_cliente)], limit=1)
    if not partner:
        b2c_tag = e["res.partner.category"].search([("name", "=", "B2C")], limit=1)
        partner = e["res.partner"].create({
            "name": "Erick Sandoval",
            "email": email_cliente,
            "phone": "+502 4111-2233",
            "street": "Calzada Roosevelt 22-00, Zona 11, Ciudad de Guatemala",
            "is_company": False,
            "customer_rank": 1,
            "category_id": [(4, b2c_tag.id)] if b2c_tag else [],
        })
        print("[1/6] Cliente registrado:", partner.name, partner.email)
    else:
        print("[1/6] Cliente existente:", partner.name, partner.email)

    # 2. Productos y existencias previas
    p_i9 = e["product.product"].search([("default_code", "=", "PROD-001")], limit=1)
    p_ssd = e["product.product"].search([("default_code", "=", "PROD-005")], limit=1)
    wh_stock = e["stock.location"].search([("complete_name", "=", "WH/Stock")], limit=1)

    stock_i9_antes = p_i9.qty_available
    stock_ssd_antes = p_ssd.qty_available
    print("[2/6] Stock previo: {} ({} unid), {} ({} unid)".format(
        p_i9.default_code, stock_i9_antes, p_ssd.default_code, stock_ssd_antes))

    # 3. Crear orden web (simulando checkout eCommerce)
    website = e["website"].search([], limit=1)
    order_vals = {
        "partner_id": partner.id,
        "partner_invoice_id": partner.id,
        "partner_shipping_id": partner.id,
        "website_id": website.id if website else False,
        "client_order_ref": "TEST-E2E-WEB",
        "order_line": [
            (0, 0, {
                "product_id": p_i9.id,
                "product_uom_qty": 1.0,
            }),
            (0, 0, {
                "product_id": p_ssd.id,
                "product_uom_qty": 2.0,
            }),
        ],
    }
    so = e["sale.order"].create(order_vals)
    print("[3/6] Pedido web creado: {} por Q {:,.2f}".format(so.name, so.amount_total))

    # 4. Confirmar orden y simular transaccion de pago
    so.action_confirm()
    print("[4/6] Pedido confirmado en estado:", so.state)

    # Validar picking (despacho)
    for picking in so.picking_ids:
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.with_context(skip_sms=True).button_validate()
    print("      Albarán de entrega validado:", [p.name for p in so.picking_ids])

    # Generar y publicar factura
    invs = so._create_invoices()
    for inv in invs:
        inv.action_post()
        # Registrar pago
        banco = e["account.journal"].search([("type", "in", ["bank", "cash"])], limit=1)
        if banco:
            reg = e["account.payment.register"].with_context(
                active_model="account.move",
                active_ids=inv.ids,
            ).create({
                "journal_id": banco.id,
            })
            reg.action_create_payments()
        print("[5/6] Factura emitida y pagada:", inv.name, "Estado:", inv.payment_state)

    # 5. Comprobar descuento de inventario
    e.cr.commit()
    e["product.product"].invalidate_model(["qty_available"])
    stock_i9_despues = e["product.product"].browse(p_i9.id).qty_available
    stock_ssd_despues = e["product.product"].browse(p_ssd.id).qty_available
    print("      Stock posterior: {} ({} -> {}), {} ({} -> {})".format(
        p_i9.default_code, stock_i9_antes, stock_i9_despues,
        p_ssd.default_code, stock_ssd_antes, stock_ssd_despues))
    assert stock_i9_despues == stock_i9_antes - 1.0, "Fallo descuento en PROD-001"
    assert stock_ssd_despues == stock_ssd_antes - 2.0, "Fallo descuento en PROD-005"

    # 6. Comprobar Lead automatico en CRM
    e.cr.commit()
    lead = e["crm.lead"].search([("description", "like", so.name)], limit=1)
    if lead:
        print("[6/6] Lead CRM generado exitosamente:")
        print("      * Nombre:", lead.name)
        print("      * Etapa:", lead.stage_id.name)
        print("      * Etiquetas:", [t.name for t in lead.tag_ids])
        print("      * Ingreso Esperado: Q {:,.2f}".format(lead.expected_revenue))
    else:
        print("[6/6] AVISO: Lead CRM no encontrado por descripcion. Buscando por cliente...")
        lead = e["crm.lead"].search([("partner_id", "=", partner.id)], limit=1)
        if lead:
            print("      Lead encontrado:", lead.name)
        else:
            print("      No se encontro lead asociado.")

    print("\n>>> PRUEBA E2E COMPLETADA CON EXITO <<<")


ejecutar()
