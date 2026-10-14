# -*- coding: utf-8 -*-
"""Siembra de datos historicos de ventas y compras para Business Intelligence (Fase 3).

Este script ejecuta el Hito A3 de forma 100% idempotente:
1. Verifica si ya existen ordenes con referencia 'DEMO-SEED'. Si ya existen, sale sin duplicar.
2. Siembra compras historicas (~15 ordenes de compra) distribuidas en los ultimos 90 dias
   con los 4 proveedores para alimentar v_bi_compras y mantener stock saludable.
3. Siembra ventas historicas (~75 ordenes de venta) distribuidas a lo largo de las ultimas
   12 semanas (90 dias) hasta el dia de hoy:
   - Clientes B2B (TechCorp S.A., Innova Solutions) y B2C (Juan Pérez, María López, Carlos Ruiz, Pedro Gómez).
   - Canales Web (website_id asignado) y Cotización tradicional.
   - Cadena ERP completa y consistente:
     * Orden de venta confirmada
     * Albarán de entrega validado (descuenta stock real)
     * Factura generada, publicada y registrada como pagada
   - Fechas historicas ajustadas hacia atras (date_order, date_done, invoice_date, payment_date).
   - Top 5 de productos claramente diferenciado (PROD-001, PROD-002, PROD-005, PROD-003, PROD-011).
   - Mantiene a proposito los productos de servidores y switches (PROD-009, PROD-010, PROD-018, PROD-007)
     en estado 'Bajo' para activar las alertas de stock bajo del BI.

Uso:
  docker exec -i techcore_odoo_web odoo shell -d TechCore_DB \
    --db_host techcore_postgres_db -r odoo -w techcore_secure_pwd --no-http --log-level=warn < sembrar_ventas_demo.py
"""
import datetime
import logging
import random

_logger = logging.getLogger("sembrar_ventas_demo")

REFERENCIA_DEMO = "DEMO-SEED"


def ejecutar():
    admin = env.ref("base.user_admin")
    e = env(user=admin)
    print("=== SIEMBRA DE DATOS HISTORICOS PARA BUSINESS INTELLIGENCE (HITO A3) ===")

    # 1. Comprobacion de idempotencia
    so_existentes = e["sale.order"].search_count([("client_order_ref", "=", REFERENCIA_DEMO)])
    if so_existentes >= 50:
        print("Ya existen {} ordenes de venta con referencia {}. Omitiendo siembra para mantener idempotencia.".format(
            so_existentes, REFERENCIA_DEMO))
        return

    hoy = datetime.date.today()
    website = e["website"].search([], limit=1)
    diario_banco = e["account.journal"].search([("type", "in", ["bank", "cash"])], limit=1)
    wh_stock = e["stock.location"].search([("complete_name", "=", "WH/Stock")], limit=1)

    # Cache de clientes
    clientes_b2b = list(e["res.partner"].search([("name", "in", ["TechCorp S.A.", "Innova Solutions"])]))
    clientes_b2c = list(e["res.partner"].search([("name", "in", ["Juan Pérez", "María López", "Carlos Ruiz", "Pedro Gómez"])]))
    todos_clientes = clientes_b2b + clientes_b2c
    if not todos_clientes:
        raise ValueError("No se encontraron clientes para sembrar ventas.")

    # Cache de proveedores
    proveedores = {
        p.name: p for p in e["res.partner"].search([("supplier_rank", ">", 0)])
    }

    # Cache de productos
    productos = {
        p.default_code: p for p in e["product.product"].search([("default_code", "=like", "PROD-%")])
    }
    if len(productos) < 20:
        raise ValueError("No se encontraron los 20+ productos en product.product.")

    # 2. Siembra de Compras Historicas (para nutrir v_bi_compras y reponer stock)
    print("\n--- PASO 1: Sembrando 16 compras historicas ---")
    plan_compras = [
        # (dias_atras, proveedor, [(codigo, cant, precio)])
        (88, "Ingram Micro Guatemala", [("PROD-001", 30, 494.40), ("PROD-002", 25, 474.62), ("PROD-013", 25, 247.20)]),
        (82, "Intcomex", [("PROD-008", 10, 832.32), ("PROD-017", 40, 24.48)]),
        (75, "Ingram Micro Guatemala", [("PROD-003", 50, 98.88), ("PROD-004", 60, 39.55), ("PROD-015", 20, 197.76)]),
        (68, "PC Mayorista", [("PROD-005", 40, 141.40), ("PROD-006", 40, 80.80), ("PROD-020", 30, 252.10)]),
        (61, "Ingram Micro Guatemala", [("PROD-011", 20, 444.96), ("PROD-012", 25, 177.98), ("PROD-019", 15, 375.82)]),
        (54, "Distribuidora Tecno S.A.", [("PROD-021", 30, 70.00)]),
        (48, "Ingram Micro Guatemala", [("PROD-001", 25, 494.40), ("PROD-002", 20, 474.62)]),
        (42, "PC Mayorista", [("PROD-016", 25, 191.90), ("PROD-005", 25, 141.40)]),
        (35, "Ingram Micro Guatemala", [("PROD-003", 40, 98.88), ("PROD-004", 50, 39.55)]),
        (28, "Intcomex", [("PROD-017", 30, 24.48)]),
        (22, "Ingram Micro Guatemala", [("PROD-014", 25, 217.54), ("PROD-013", 20, 247.20)]),
        (16, "Distribuidora Tecno S.A.", [("PROD-021", 25, 70.00)]),
        (12, "PC Mayorista", [("PROD-006", 30, 80.80), ("PROD-020", 20, 252.10)]),
        (8, "Ingram Micro Guatemala", [("PROD-001", 20, 494.40), ("PROD-011", 15, 444.96)]),
        (4, "Ingram Micro Guatemala", [("PROD-005", 20, 138.43), ("PROD-003", 30, 98.88)]),
        (2, "Intcomex", [("PROD-008", 6, 832.32)]),
    ]

    ordenes_compra_creadas = 0
    for dias_atras, prov_nom, lineas in plan_compras:
        prov = proveedores.get(prov_nom)
        if not prov:
            continue
        fecha_po = hoy - datetime.timedelta(days=dias_atras)
        fecha_po_dt = datetime.datetime.combine(fecha_po, datetime.time(10, 0, 0))

        lineas_po = []
        for code, cant, precio in lineas:
            p = productos.get(code)
            if not p:
                continue
            lineas_po.append((0, 0, {
                "product_id": p.id,
                "name": p.name,
                "product_qty": cant,
                "price_unit": precio,
                "date_planned": fecha_po_dt,
            }))

        po = e["purchase.order"].create({
            "partner_id": prov.id,
            "date_order": fecha_po_dt,
            "order_line": lineas_po,
        })
        po.button_confirm()

        # Validar recepciones de compra
        for picking in po.picking_ids:
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
                move.picked = True
            picking.button_validate()

        # Ajustar fecha en SQL
        e.cr.execute("UPDATE purchase_order SET date_order = %s, date_approve = %s WHERE id = %s",
                     (fecha_po_dt, fecha_po_dt, po.id))
        for picking in po.picking_ids:
            e.cr.execute("UPDATE stock_picking SET date_done = %s, scheduled_date = %s WHERE id = %s",
                         (fecha_po_dt, fecha_po_dt, picking.id))
            e.cr.execute("UPDATE stock_move SET date = %s WHERE picking_id = %s",
                         (fecha_po_dt, picking.id))
            e.cr.execute("UPDATE stock_move_line SET date = %s WHERE picking_id = %s",
                         (fecha_po_dt, picking.id))

        ordenes_compra_creadas += 1

    print("Ordenes de compra creadas y recibidas: {}".format(ordenes_compra_creadas))

    # 3. Siembra de Ventas Historicas (75 ordenes repartidas en 90 dias)
    print("\n--- PASO 2: Sembrando 75 ventas historicas ---")
    random.seed(20261012)

    # Ponderacion para top 5 fuerte
    # (codigo, probabilidad_aparicion, min_cant, max_cant)
    catalogo_ponderado = [
        ("PROD-001", 18, 1, 3),   # Top 1 ingresos (Intel i9)
        ("PROD-002", 15, 1, 3),   # Top 2 ingresos (Ryzen 9)
        ("PROD-005", 22, 1, 4),   # Top 3 ingresos (SSD Samsung 2TB)
        ("PROD-003", 25, 2, 5),   # Top 4 ingresos (Corsair DDR5)
        ("PROD-011", 12, 1, 2),   # Top 5 ingresos (ASUS Hero Z790)
        ("PROD-006", 18, 1, 3),   # SSD WD 1TB
        ("PROD-004", 25, 2, 6),   # Kingston DDR4
        ("PROD-013", 14, 1, 2),   # i5-13600K
        ("PROD-014", 12, 1, 2),   # Ryzen 5 7600X
        ("PROD-012", 12, 1, 2),   # MSI B650
        ("PROD-015", 10, 1, 2),   # G.Skill 64GB
        ("PROD-016", 10, 1, 2),   # Crucial 4TB
        ("PROD-020", 10, 1, 2),   # Seagate 18TB
        ("PROD-019", 8, 1, 2),    # Gigabyte X670E
        ("PROD-021", 16, 1, 4),   # Logitech MX Keys
        ("PROD-017", 14, 1, 4),   # TP-Link Switch
        ("PROD-008", 4, 1, 1),    # Ubiquiti Switch
    ]

    total_ventas = 75
    # Distribuir ordenes a lo largo de 88 dias (hace 88 dias a hace 1 dia)
    intervalos_dias = sorted([random.randint(1, 88) for _ in range(total_ventas)], reverse=True)

    ordenes_venta_creadas = 0
    facturas_creadas = 0

    for idx, dias_atras in enumerate(intervalos_dias):
        fecha_so = hoy - datetime.timedelta(days=dias_atras)
        hora = random.randint(9, 18)
        minuto = random.randint(0, 59)
        fecha_so_dt = datetime.datetime.combine(fecha_so, datetime.time(hora, minuto, 0))

        # Determinar canal y cliente
        es_web = (random.random() < 0.60)  # 60% canal Web, 40% Cotizacion
        if es_web:
            cliente = random.choice(clientes_b2c)
            website_id = website.id if website else False
        else:
            # Cotizaciones tipicamente B2B
            cliente = random.choice(clientes_b2b if random.random() < 0.70 else clientes_b2c)
            website_id = False

        # Seleccionar 1 a 3 productos por orden
        num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        items_candidatos = random.sample(catalogo_ponderado, num_items)

        lineas_so = []
        for code, _prob, min_c, max_c in items_candidatos:
            p = productos.get(code)
            if not p:
                continue
            cant = random.randint(min_c, max_c)
            lineas_so.append((0, 0, {
                "product_id": p.id,
                "product_uom_qty": cant,
            }))

        if not lineas_so:
            continue

        vals_so = {
            "partner_id": cliente.id,
            "date_order": fecha_so_dt,
            "client_order_ref": REFERENCIA_DEMO,
            "order_line": lineas_so,
        }
        if website_id:
            vals_so["website_id"] = website_id

        so = e["sale.order"].create(vals_so)
        so.action_confirm()

        # Validar despacho
        for picking in so.picking_ids:
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
                move.picked = True
            picking.button_validate()

        # Crear y publicar factura
        invoices = so._create_invoices()
        for inv in invoices:
            inv.action_post()
            # Registrar pago
            if diario_banco:
                reg = e["account.payment.register"].with_context(
                    active_model="account.move",
                    active_ids=inv.ids,
                ).create({
                    "journal_id": diario_banco.id,
                    "payment_date": fecha_so,
                })
                reg.action_create_payments()
            facturas_creadas += 1

        # Ajuste de fechas historicas en cascada
        e.cr.execute("UPDATE sale_order SET date_order = %s WHERE id = %s",
                     (fecha_so_dt, so.id))
        for picking in so.picking_ids:
            e.cr.execute("UPDATE stock_picking SET date_done = %s, scheduled_date = %s WHERE id = %s",
                         (fecha_so_dt, fecha_so_dt, picking.id))
            e.cr.execute("UPDATE stock_move SET date = %s WHERE picking_id = %s",
                         (fecha_so_dt, picking.id))
            e.cr.execute("UPDATE stock_move_line SET date = %s WHERE picking_id = %s",
                         (fecha_so_dt, picking.id))

        for inv in invoices:
            e.cr.execute("UPDATE account_move SET date = %s, invoice_date = %s WHERE id = %s",
                         (fecha_so, fecha_so, inv.id))
            e.cr.execute("UPDATE account_move_line SET date = %s WHERE move_id = %s",
                         (fecha_so, inv.id))

        ordenes_venta_creadas += 1

    e.cr.commit()
    print("Ordenes de venta sembradas: {}".format(ordenes_venta_creadas))
    print("Facturas pagadas: {}".format(facturas_creadas))

    print("\n=== VERIFICACION VISTAS BI ===")
    e.cr.execute("SELECT count(*), round(sum(subtotal), 2) FROM v_bi_ventas_detalle;")
    total_det, total_ingresos = e.cr.fetchone()
    print("v_bi_ventas_detalle: {} lineas, Total Ingresos: Q {:,.2f}".format(total_det, total_ingresos or 0))

    e.cr.execute("SELECT canal, count(DISTINCT orden), round(sum(subtotal), 2) FROM v_bi_ventas_detalle GROUP BY canal;")
    print("Distribucion por Canal:")
    for c, cnt, subt in e.cr.fetchall():
        print("  * Canal {}: {} ordenes, Q {:,.2f}".format(c, cnt, subt))

    e.cr.execute("SELECT segmento, count(DISTINCT orden), round(sum(subtotal), 2) FROM v_bi_ventas_detalle GROUP BY segmento;")
    print("Distribucion por Segmento:")
    for s, cnt, subt in e.cr.fetchall():
        print("  * Segmento {}: {} ordenes, Q {:,.2f}".format(s, cnt, subt))

    e.cr.execute("SELECT count(DISTINCT semana), min(fecha), max(fecha) FROM v_bi_ventas_detalle;")
    semanas, f_min, f_max = e.cr.fetchone()
    print("Cobertura temporal: {} semanas distintas (desde {} hasta {})".format(semanas, f_min, f_max))

    e.cr.execute("SELECT ranking, codigo_producto, producto, unidades_vendidas, ingresos FROM v_bi_top_productos WHERE ranking <= 5 ORDER BY ranking;")
    print("Top 5 Productos:")
    for r, cp, p, u, ing in e.cr.fetchall():
        print("  #{}: [{}] {} - {} unid., Q {:,.2f}".format(r, cp, p, u, ing))

    e.cr.execute("SELECT codigo_producto, producto, existencias, stock_minimo, estado_stock FROM v_bi_inventario WHERE estado_stock = 'Bajo';")
    print("Productos en Stock Bajo (Alertas de BI):")
    for cp, p, ex, sm, es in e.cr.fetchall():
        print("  * [{}] {} (Existencias: {}, Min: {}, Estado: {})".format(cp, p, ex, sm, es))

    e.cr.execute("SELECT count(*), round(sum(subtotal), 2) FROM v_bi_compras;")
    c_po, subt_po = e.cr.fetchone()
    print("v_bi_compras: {} registros, Total Compras: Q {:,.2f}".format(c_po, subt_po or 0))


ejecutar()
