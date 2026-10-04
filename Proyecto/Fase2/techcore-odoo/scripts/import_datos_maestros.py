# -*- coding: utf-8 -*-
"""Carga de datos maestros de Fase 2 (TechCore Solutions).

Replica en codigo la importacion masiva realizada con los archivos Excel del
proyecto:

  * 1_Productos_Odoo.xlsx         -> 20 productos + 7 categorias
  * 3_Proveedores_Odoo.xlsx       -> 3 proveedores
  * 4_Inventario_Fisico_Odoo.xlsx -> inventario fisico en WH/Stock

Uso:
  docker compose run --rm web odoo shell -c <db> \
      < addons/import_datos_maestros.py
"""
import logging

_logger = logging.getLogger(__name__)

# default_code, nombre, categoria, precio_venta, costo, stock_inicial
PRODUCTOS = [
    ("PROD-001", "Intel Core i9-13900K", "Procesador", 650.0, 500.0, 15),
    ("PROD-002", "AMD Ryzen 9 7950X", "Procesador", 600.0, 480.0, 20),
    ("PROD-013", "Intel Core i5-13600K", "Procesador", 320.0, 250.0, 40),
    ("PROD-014", "AMD Ryzen 5 7600X", "Procesador", 280.0, 220.0, 35),
    ("PROD-003", "Corsair Vengeance 32GB DDR5", "Memoria RAM", 150.0, 100.0, 50),
    ("PROD-004", "Kingston Fury Beast 16GB DDR4", "Memoria RAM", 60.0, 40.0, 100),
    ("PROD-015", "G.Skill Trident Z5 RGB 64GB", "Memoria RAM", 280.0, 200.0, 15),
    ("PROD-005", "Samsung 990 PRO 2TB NVMe", "SSD", 200.0, 140.0, 30),
    ("PROD-006", "WD Black SN850X 1TB NVMe", "SSD", 120.0, 80.0, 45),
    ("PROD-016", "Crucial P3 Plus 4TB NVMe", "SSD", 250.0, 190.0, 20),
    ("PROD-020", "Seagate IronWolf Pro 18TB", "Disco Duro", 350.0, 260.0, 25),
    ("PROD-007", "Cisco Catalyst 2960-X 24 Port", "Switch", 800.0, 600.0, 5),
    ("PROD-008", "Ubiquiti UniFi Switch 48 PoE", "Switch", 1100.0, 850.0, 8),
    ("PROD-017", "TP-Link TL-SG108E 8 Port", "Switch", 40.0, 25.0, 80),
    ("PROD-009", "Dell PowerEdge R750", "Servidor", 4500.0, 3500.0, 2),
    ("PROD-010", "HPE ProLiant DL380 Gen10", "Servidor", 4200.0, 3200.0, 3),
    ("PROD-018", "Lenovo ThinkSystem SR650", "Servidor", 3800.0, 2900.0, 4),
    ("PROD-011", "ASUS ROG Maximus Z790 Hero", "Tarjeta Madre", 600.0, 450.0, 10),
    ("PROD-012", "MSI MAG B650 Tomahawk WiFi", "Tarjeta Madre", 250.0, 180.0, 25),
    ("PROD-019", "Gigabyte X670E AORUS Master", "Tarjeta Madre", 500.0, 380.0, 12),
]

PROVEEDORES = [
    (
        "Ingram Micro Guatemala",
        "ventas@ingrammicro.com.gt",
        "Productos: Procesadores, RAM, SSD, Tarjetas Madre. "
        "Condiciones de pago: 30 dias credito",
    ),
    (
        "Intcomex",
        "info@intcomex.com.gt",
        "Productos: Switches, Servidores, Redes. "
        "Condiciones de pago: 15 dias credito",
    ),
    (
        "PC Mayorista",
        "contacto@pcmayorista.gt",
        "Productos: Componentes generales. Condiciones de pago: Contado",
    ),
]

# Proveedor asignado por familia de producto (cotizaciones multi-proveedor)
RUTA_PROVEEDOR = {
    "Procesador": "Ingram Micro Guatemala",
    "Memoria RAM": "Ingram Micro Guatemala",
    "SSD": "Ingram Micro Guatemala",
    "Tarjeta Madre": "Ingram Micro Guatemala",
    "Switch": "Intcomex",
    "Servidor": "Intcomex",
    "Disco Duro": "PC Mayorista",
}

CATEGORIAS = [
    "Procesador",
    "Memoria RAM",
    "SSD",
    "Disco Duro",
    "Switch",
    "Servidor",
    "Tarjeta Madre",
]


def _pais(nombre):
    return env["res.country"].search([("name", "=", nombre)], limit=1)


def _categoria(nombre):
    """Devuelve (o crea) la categoria de producto colgando de 'All'."""
    completa = env["product.category"].search([("name", "=", nombre)], limit=1)
    if completa:
        return completa
    raiz = env["product.category"].search([("name", "=", "All")], limit=1)
    return env["product.category"].create({
        "name": nombre,
        "parent_id": raiz.id,
    })


def cargar_proveedores():
    proveedores = {}
    pais = _pais("Guatemala")
    for nombre, email, comentario in PROVEEDORES:
        partner = env["res.partner"].search([("name", "=", nombre)], limit=1)
        vals = {
            "name": nombre,
            "is_company": True,
            "company_type": "company",
            "supplier_rank": 1,
            "email": email,
            "comment": comentario,
            "street": "Zona 10, Ciudad de Guatemala",
        }
        if pais:
            vals["country_id"] = pais.id
        if partner:
            partner.write(vals)
        else:
            partner = env["res.partner"].create(vals)
        proveedores[nombre] = partner
        _logger.info("Proveedor listo: %s (id=%s)", partner.name, partner.id)
    return proveedores


def cargar_categorias():
    return dict((nombre, _categoria(nombre)) for nombre in CATEGORIAS)


def cargar_productos(categorias, proveedores):
    unidad = env.ref("uom.product_uom_unit")
    productos = {}
    for code, nombre, cat, precio, costo, _stock in PRODUCTOS:
        categoria = categorias.get(cat)
        if categoria is None:
            raise ValueError("Categoria no encontrada: %s" % cat)
        vals = {
            "name": nombre,
            "default_code": code,
            "categ_id": categoria.id,
            "list_price": precio,
            "standard_price": costo,
            # 'product' = almacenable (necesario para Existencias / Recepcion)
            "type": "product",
            "sale_ok": True,
            "purchase_ok": True,
            "uom_id": unidad.id,
            "uom_po_id": unidad.id,
        }
        producto = env["product.template"].search(
            [("default_code", "=", code)], limit=1)
        if producto:
            producto.write(vals)
        else:
            producto = env["product.template"].create(vals)
        productos[code] = producto
        _logger.info("Producto listo: %s - %s", code, producto.name)

    # Lineas de proveedor en el catalogo (precios de compra por proveedor)
    for code, _nombre, cat, _precio, costo, _stock in PRODUCTOS:
        proveedor = proveedores.get(RUTA_PROVEEDOR[cat])
        producto = productos[code]
        if not proveedor:
            continue
        ya_existe = producto.seller_ids.filtered(
            lambda s: s.partner_id.id == proveedor.id)
        if not ya_existe:
            env["product.supplierinfo"].create({
                "product_tmpl_id": producto.id,
                "partner_id": proveedor.id,
                "min_qty": 1.0,
                "price": costo,
                "delay": 3,
            })
    return productos


def cargar_inventario(productos):
    """Inventario fisico en WH/Stock (ajuste de inventario nativo)."""
    ubicacion = env["stock.location"].search(
        [("complete_name", "=", "WH/Stock")], limit=1)
    if not ubicacion:
        raise ValueError("No se encontro la ubicacion WH/Stock")

    motivo = {"inventory_adjustment_name": "Inventario fisico inicial Fase 2"}
    for code, _nombre, _cat, _precio, _costo, stock in PRODUCTOS:
        producto = productos[code]
        env["stock.quant"].with_context(**motivo)._update_available_quantity(
            producto, ubicacion, stock)
    _logger.info("Inventario aplicado sobre %s", ubicacion.complete_name)


def main():
    proveedores = cargar_proveedores()
    categorias = cargar_categorias()
    productos = cargar_productos(categorias, proveedores)
    cargar_inventario(productos)
    env.cr.commit()
    _logger.info(
        "Carga finalizada: %d productos, %d proveedores",
        len(productos), len(proveedores),
    )


main()