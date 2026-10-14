# -*- coding: utf-8 -*-
"""Carga de datos maestros de la Fase 3 (TechCore Solutions Guatemala).

Este script completa el Hito A1 de la Fase 3 de forma 100% idempotente:
1. Carga los 60 precios de proveedor (3 proveedores por producto para los 20 productos base)
   segun 5_Precios_Proveedores_Odoo.xlsx.
2. Crea los extras de la Fase 2 acordados por el equipo:
   - Categoria: Perifericos
   - Producto PROD-021: Logitech MX Keys (almacenable, venta Q 100.00, costo Q 70.00, 10 unid. iniciales)
   - Cliente: Pedro Gomez (individual, B2C)
   - Proveedor: Distribuidora Tecno S.A.
   - Linea de proveedor para PROD-021 con Distribuidora Tecno S.A. (Q 70.00, delay 1 dia)
   - Inventario inicial de 10 unidades en WH/Stock con ajuste nativo de inventario.
3. Crea las 4 reglas de reposicion (stock.warehouse.orderpoint) de Francisco:
   - PROD-009: min 5, max 10
   - PROD-010: min 5, max 10
   - PROD-018: min 5, max 10
   - PROD-007: min 10, max 25

Uso en Odoo Shell:
  docker exec -i techcore_odoo_web odoo shell -d TechCore_DB \
    --db_host techcore_postgres_db -r odoo -w techcore_secure_pwd --no-http --log-level=warn < cargar_fase3_datos_maestros.py
"""
import logging

_logger = logging.getLogger("cargar_fase3_datos_maestros")

# Matriz completa de 60 precios de proveedor (5_Precios_Proveedores_Odoo.xlsx)
PRECIOS_PROVEEDORES = [
    # (proveedor, codigo_producto, min_qty, precio, delay)
    ("Ingram Micro Guatemala", "PROD-001", 1.0, 494.40, 3),
    ("Intcomex", "PROD-001", 1.0, 510.00, 2),
    ("PC Mayorista", "PROD-001", 1.0, 505.00, 1),

    ("Ingram Micro Guatemala", "PROD-002", 1.0, 474.62, 3),
    ("Intcomex", "PROD-002", 1.0, 489.60, 2),
    ("PC Mayorista", "PROD-002", 1.0, 484.80, 1),

    ("Ingram Micro Guatemala", "PROD-013", 1.0, 247.20, 3),
    ("Intcomex", "PROD-013", 1.0, 255.00, 2),
    ("PC Mayorista", "PROD-013", 1.0, 252.50, 1),

    ("Ingram Micro Guatemala", "PROD-014", 1.0, 217.54, 3),
    ("Intcomex", "PROD-014", 1.0, 224.40, 2),
    ("PC Mayorista", "PROD-014", 1.0, 222.20, 1),

    ("Ingram Micro Guatemala", "PROD-003", 1.0, 98.88, 3),
    ("Intcomex", "PROD-003", 1.0, 102.00, 2),
    ("PC Mayorista", "PROD-003", 1.0, 101.00, 1),

    ("Ingram Micro Guatemala", "PROD-004", 1.0, 39.55, 3),
    ("Intcomex", "PROD-004", 1.0, 40.80, 2),
    ("PC Mayorista", "PROD-004", 1.0, 40.40, 1),

    ("Ingram Micro Guatemala", "PROD-015", 1.0, 197.76, 3),
    ("Intcomex", "PROD-015", 1.0, 204.00, 2),
    ("PC Mayorista", "PROD-015", 1.0, 202.00, 1),

    ("Ingram Micro Guatemala", "PROD-005", 1.0, 138.43, 3),
    ("Intcomex", "PROD-005", 1.0, 142.80, 2),
    ("PC Mayorista", "PROD-005", 1.0, 141.40, 1),

    ("Ingram Micro Guatemala", "PROD-006", 1.0, 79.10, 3),
    ("Intcomex", "PROD-006", 1.0, 81.60, 2),
    ("PC Mayorista", "PROD-006", 1.0, 80.80, 1),

    ("Ingram Micro Guatemala", "PROD-016", 1.0, 187.87, 3),
    ("Intcomex", "PROD-016", 1.0, 193.80, 2),
    ("PC Mayorista", "PROD-016", 1.0, 191.90, 1),

    ("Ingram Micro Guatemala", "PROD-020", 1.0, 267.80, 3),
    ("Intcomex", "PROD-020", 1.0, 265.20, 2),
    ("PC Mayorista", "PROD-020", 1.0, 252.10, 1),

    ("Ingram Micro Guatemala", "PROD-007", 1.0, 618.00, 3),
    ("Intcomex", "PROD-007", 1.0, 587.52, 2),
    ("PC Mayorista", "PROD-007", 1.0, 606.00, 1),

    ("Ingram Micro Guatemala", "PROD-008", 1.0, 875.50, 3),
    ("Intcomex", "PROD-008", 1.0, 832.32, 2),
    ("PC Mayorista", "PROD-008", 1.0, 858.50, 1),

    ("Ingram Micro Guatemala", "PROD-017", 1.0, 25.75, 3),
    ("Intcomex", "PROD-017", 1.0, 24.48, 2),
    ("PC Mayorista", "PROD-017", 1.0, 25.25, 1),

    ("Ingram Micro Guatemala", "PROD-009", 1.0, 3605.00, 3),
    ("Intcomex", "PROD-009", 1.0, 3427.20, 2),
    ("PC Mayorista", "PROD-009", 1.0, 3535.00, 1),

    ("Ingram Micro Guatemala", "PROD-010", 1.0, 3296.00, 3),
    ("Intcomex", "PROD-010", 1.0, 3133.44, 2),
    ("PC Mayorista", "PROD-010", 1.0, 3232.00, 1),

    ("Ingram Micro Guatemala", "PROD-018", 1.0, 2987.00, 3),
    ("Intcomex", "PROD-018", 1.0, 2839.68, 2),
    ("PC Mayorista", "PROD-018", 1.0, 2929.00, 1),

    ("Ingram Micro Guatemala", "PROD-011", 1.0, 444.96, 3),
    ("Intcomex", "PROD-011", 1.0, 459.00, 2),
    ("PC Mayorista", "PROD-011", 1.0, 454.50, 1),

    ("Ingram Micro Guatemala", "PROD-012", 1.0, 177.98, 3),
    ("Intcomex", "PROD-012", 1.0, 183.60, 2),
    ("PC Mayorista", "PROD-012", 1.0, 181.80, 1),

    ("Ingram Micro Guatemala", "PROD-019", 1.0, 375.82, 3),
    ("Intcomex", "PROD-019", 1.0, 387.60, 2),
    ("PC Mayorista", "PROD-019", 1.0, 383.80, 1),
]

REGLAS_REPOSICION = [
    # (codigo_producto, min_qty, max_qty)
    ("PROD-009", 5.0, 10.0),
    ("PROD-010", 5.0, 10.0),
    ("PROD-018", 5.0, 10.0),
    ("PROD-007", 10.0, 25.0),
]


def ejecutar():
    admin = env.ref("base.user_admin")
    e = env(user=admin)
    pais_gt = e["res.country"].search([("name", "=", "Guatemala")], limit=1)
    wh_stock = e["stock.location"].search([("complete_name", "=", "WH/Stock")], limit=1)
    if not wh_stock:
        raise ValueError("No se encontro la ubicacion WH/Stock")

    print("=== PASO 1: Cargar 60 precios de proveedor ===")
    proveedores_cache = {}
    productos_cache = {}

    for prov_nombre, code, min_qty, precio, delay in PRECIOS_PROVEEDORES:
        if prov_nombre not in proveedores_cache:
            prov = e["res.partner"].search([("name", "=", prov_nombre)], limit=1)
            if not prov:
                raise ValueError("Proveedor no encontrado: %s" % prov_nombre)
            proveedores_cache[prov_nombre] = prov
        partner = proveedores_cache[prov_nombre]

        if code not in productos_cache:
            tmpl = e["product.template"].search([("default_code", "=", code)], limit=1)
            if not tmpl:
                raise ValueError("Producto no encontrado: %s" % code)
            productos_cache[code] = tmpl
        prod_tmpl = productos_cache[code]

        # Buscar o crear product.supplierinfo
        si = e["product.supplierinfo"].search([
            ("product_tmpl_id", "=", prod_tmpl.id),
            ("partner_id", "=", partner.id),
        ], limit=1)
        vals = {
            "product_tmpl_id": prod_tmpl.id,
            "partner_id": partner.id,
            "min_qty": min_qty,
            "price": precio,
            "delay": delay,
        }
        if si:
            si.write(vals)
        else:
            e["product.supplierinfo"].create(vals)

    print("Precios de proveedor cargados / actualizados.")

    print("\n=== PASO 2: Cargar extras de Fase 2 ===")
    # 2.1 Categoria Perifericos
    cat_raiz = e["product.category"].search([("name", "=", "All")], limit=1)
    cat_perifericos = e["product.category"].search([("name", "=", "Periféricos")], limit=1)
    if not cat_perifericos:
        cat_perifericos = e["product.category"].create({
            "name": "Periféricos",
            "parent_id": cat_raiz.id if cat_raiz else False,
        })
        print("Categoria 'Perifericos' creada.")
    else:
        print("Categoria 'Perifericos' ya existe.")

    # 2.2 Proveedor Distribuidora Tecno S.A.
    prov_tecno = e["res.partner"].search([("name", "=", "Distribuidora Tecno S.A.")], limit=1)
    vals_tecno = {
        "name": "Distribuidora Tecno S.A.",
        "is_company": True,
        "company_type": "company",
        "supplier_rank": 1,
        "email": "ventas@distribuidoratecno.gt",
        "phone": "+502 2444-5555",
        "street": "Zona 9, Ciudad de Guatemala",
        "comment": "Proveedor de perifericos y accesorios de computo.",
    }
    if pais_gt:
        vals_tecno["country_id"] = pais_gt.id
    if prov_tecno:
        prov_tecno.write(vals_tecno)
        print("Proveedor Distribuidora Tecno S.A. actualizado.")
    else:
        prov_tecno = e["res.partner"].create(vals_tecno)
        print("Proveedor Distribuidora Tecno S.A. creado.")

    # 2.3 Cliente Pedro Gomez
    b2c_tag = e["res.partner.category"].search([("name", "=", "B2C")], limit=1)
    if not b2c_tag:
        b2c_tag = e["res.partner.category"].create({"name": "B2C"})

    pedro = e["res.partner"].search([("name", "=", "Pedro Gómez")], limit=1)
    vals_pedro = {
        "name": "Pedro Gómez",
        "is_company": False,
        "company_type": "person",
        "customer_rank": 1,
        "email": "pedro.gomez@gmail.com",
        "phone": "+502 5555-8888",
        "street": "Zona 11, Ciudad de Guatemala",
        "category_id": [(4, b2c_tag.id)],
    }
    if pais_gt:
        vals_pedro["country_id"] = pais_gt.id
    if pedro:
        pedro.write(vals_pedro)
        print("Cliente Pedro Gomez actualizado.")
    else:
        pedro = e["res.partner"].create(vals_pedro)
        print("Cliente Pedro Gomez creado.")

    # 2.4 Producto PROD-021 Logitech MX Keys
    unidad = e.ref("uom.product_uom_unit")
    prod_021 = e["product.template"].search([("default_code", "=", "PROD-021")], limit=1)
    vals_021 = {
        "name": "Logitech MX Keys",
        "default_code": "PROD-021",
        "categ_id": cat_perifericos.id,
        "list_price": 100.0,
        "standard_price": 70.0,
        "type": "product",
        "sale_ok": True,
        "purchase_ok": True,
        "uom_id": unidad.id,
        "uom_po_id": unidad.id,
    }
    if prod_021:
        prod_021.write(vals_021)
        print("Producto PROD-021 actualizado.")
    else:
        prod_021 = e["product.template"].create(vals_021)
        print("Producto PROD-021 creado.")

    # 2.5 Linea de proveedor para PROD-021
    si_021 = e["product.supplierinfo"].search([
        ("product_tmpl_id", "=", prod_021.id),
        ("partner_id", "=", prov_tecno.id),
    ], limit=1)
    vals_si_021 = {
        "product_tmpl_id": prod_021.id,
        "partner_id": prov_tecno.id,
        "min_qty": 1.0,
        "price": 70.0,
        "delay": 1,
    }
    if si_021:
        si_021.write(vals_si_021)
    else:
        e["product.supplierinfo"].create(vals_si_021)
        print("Linea de proveedor para PROD-021 creada.")

    # 2.6 Inventario inicial para PROD-021 (10 unidades)
    prod_product_021 = prod_021.product_variant_id
    quant_021 = e["stock.quant"].search([
        ("location_id", "=", wh_stock.id),
        ("product_id", "=", prod_product_021.id),
    ], limit=1)
    if not quant_021 or quant_021.quantity == 0:
        if quant_021 and quant_021.quantity != 0:
            e["stock.quant"]._update_available_quantity(prod_product_021, wh_stock, -quant_021.quantity)
        quant_021 = e["stock.quant"].search([
            ("location_id", "=", wh_stock.id),
            ("product_id", "=", prod_product_021.id),
        ], limit=1)
        if not quant_021:
            quant_021 = e["stock.quant"].create({
                "location_id": wh_stock.id,
                "product_id": prod_product_021.id,
            })
        quant_021.with_context(inventory_mode=True).write({
            "inventory_quantity": 10.0,
            "inventory_quantity_set": True,
        })
        wizard = e["stock.inventory.adjustment.name"].create({
            "inventory_adjustment_name": "Inventario inicial PROD-021",
            "quant_ids": [(6, 0, quant_021.ids)],
        })
        wizard.action_apply()
        print("Ajuste de inventario de 10 unidades aplicado a PROD-021.")
    else:
        print("PROD-021 ya cuenta con existencias: %s unidades." % quant_021.quantity)

    print("\n=== PASO 3: Recrear reglas de reposicion de Francisco ===")
    for code, min_qty, max_qty in REGLAS_REPOSICION:
        tmpl = e["product.template"].search([("default_code", "=", code)], limit=1)
        if not tmpl:
            print("AVISO: No se encontro producto para regla:", code)
            continue
        p = tmpl.product_variant_id
        op = e["stock.warehouse.orderpoint"].search([
            ("product_id", "=", p.id),
            ("location_id", "=", wh_stock.id),
        ], limit=1)
        vals_op = {
            "product_id": p.id,
            "location_id": wh_stock.id,
            "product_min_qty": min_qty,
            "product_max_qty": max_qty,
            "qty_multiple": 1.0,
            "trigger": "auto",
        }
        if op:
            op.write(vals_op)
            print("Regla de reposicion actualizada para %s (min: %s, max: %s)" % (code, min_qty, max_qty))
        else:
            e["stock.warehouse.orderpoint"].create(vals_op)
            print("Regla de reposicion creada para %s (min: %s, max: %s)" % (code, min_qty, max_qty))

    e.cr.commit()
    print("\n=== VERIFICACION FINAL ===")
    total_prods = e["product.template"].search_count([("default_code", "=like", "PROD-%")])
    total_cust = e["res.partner"].search_count([("customer_rank", ">", 0)])
    total_supp = e["res.partner"].search_count([("supplier_rank", ">", 0)])
    total_si = e["product.supplierinfo"].search_count([])
    total_op = e["stock.warehouse.orderpoint"].search_count([])
    print("Total productos PROD-%: {} (esperado 21)".format(total_prods))
    print("Total clientes: {} (esperado 6)".format(total_cust))
    print("Total proveedores: {} (esperado 4)".format(total_supp))
    print("Total lineas de proveedor: {} (esperado 61: 60 base + 1 tecno)".format(total_si))
    print("Total reglas de reposicion: {} (esperado 4)".format(total_op))


ejecutar()
