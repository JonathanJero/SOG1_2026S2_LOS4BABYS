# -*- coding: utf-8 -*-
"""Genera 5_Precios_Proveedores_Odoo.xlsx para la carga masiva de precios de
proveedor (modelo product.supplierinfo).

Por que este archivo es necesario
---------------------------------
Los cuatro archivos de datos maestros (productos, clientes, proveedores e
inventario) crean los registros, pero NINGUNO crea las lineas de precio de
proveedor sobre cada producto. Sin esas lineas (product.supplierinfo):

  * el motor de aprovisionamiento no puede generar ordenes de compra y
    falla con "There is no matching vendor price to generate the purchase
    order for product [...]";
  * las RFQ alternativas muestran el mismo precio (caen al Standard Cost),
    por lo que la comparacion de proveedores no aporta evidencia.

Cada proveedor aplica un recargo distinto segun su especialidad, de modo que
la tabla "Compare Product Lines" muestre una combinacion de precios real y no
valores identicos.

Uso:
  python3 scripts/utilidad/generar_excel_precios_proveedor.py
"""
import os

from openpyxl import Workbook

# default_code, nombre, categoria, precio_venta, costo, stock
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

# Proveedor, recargo por unidad, dias de entrega, cantidad minima
PROVEEDORES = [
    ("Ingram Micro Guatemala", 1.03, 3, 1.0),
    ("Intcomex", 1.02, 2, 1.0),
    ("PC Mayorista", 1.01, 1, 1.0),
]

# El proveedor mas barato varia por familia, para que la comparacion sea real
MEJOR_POR_FAMILIA = {
    "Procesador": "Ingram Micro Guatemala",
    "Memoria RAM": "Ingram Micro Guatemala",
    "SSD": "Ingram Micro Guatemala",
    "Tarjeta Madre": "Ingram Micro Guatemala",
    "Switch": "Intcomex",
    "Servidor": "Intcomex",
    "Disco Duro": "PC Mayorista",
}


def precio(proveedor, recargo, costo, familia):
    """Precio del proveedor, con un 4% de descuento al mejor de su familia."""
    base = costo * recargo
    if MEJOR_POR_FAMILIA[familia] == proveedor:
        base *= 0.96
    return round(base, 2)


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Precios Proveedores"

    ws.append([
        "partner_id",
        "product_id/default_code",
        "min_qty",
        "price",
        "delay",
    ])

    filas = 0
    for code, _nombre, familia, _venta, costo, _stock in PRODUCTOS:
        for proveedor, recargo, delay, min_qty in PROVEEDORES:
            ws.append([
                proveedor,
                code,
                min_qty,
                precio(proveedor, recargo, costo, familia),
                delay,
            ])
            filas += 1

    # El script vive en scripts/utilidad/, el Excel va en la raiz de techcore-odoo
    directorio = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    salida = os.path.join(directorio, "5_Precios_Proveedores_Odoo.xlsx")
    wb.save(salida)

    print("Archivo generado: %s" % salida)
    print("Filas: %d (%d productos x %d proveedores)" % (
        filas, len(PRODUCTOS), len(PROVEEDORES)))
    print("\nMuestra de la comparacion para PROD-009 (Dell PowerEdge R750):")
    for proveedor, recargo, delay, min_qty in PROVEEDORES:
        print("  %-26s Q %10.2f  (%d dias)" % (
            proveedor, precio(proveedor, recargo, 3500.0, "Servidor"), delay))


if __name__ == "__main__":
    main()