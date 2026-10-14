# -*- coding: utf-8 -*-
"""Genera el estado 'base limpia' de TechCore_DB.

Deja el ERP unicamente con la CONFIGURACION necesaria para la demostracion
de la Fase 2, eliminando los datos cargados en las fases previas:

  * 20 productos de hardware  (product.template / product.product)
  * inventario fisico        (stock.quant / stock.move)
  * 3 proveedores            (res.partner con supplier_rank)
  * 5 clientes               (res.partner con customer_rank)
  * reglas de reposicion     (stock.warehouse.orderpoint)
  * ordenes de compra        (purchase.order y sus lineas)
  * requisiciones / acuerdos (purchase.requisition)
  * pedidos de venta         (sale.order y sus lineas)

CONSERVADO INTENCIONALMENTE (es la configuracion que hay que demostrar):

  * menus, grupos y permisos de acceso (incluido el fix de Ventas)
  * modulos instalados (purchase_requisition_stock, crm, mass_mailing, etc.)
  * etapas del pipeline CRM  (Lead, Contactado, Negociacion, Cerrado)
  * plantillas de correo     (Plantilla 1 Promocion / Plantilla 2 Fidelizacion)
  * sitio web y portal de cliente

Motivo pedagogico
-----------------
La rubrica del punto 2.1 (30 puntos) exige demostrar la carga de productos,
clientes y proveedores "en ambas modalidades": masiva (importador de Excel) y
manual (formulario). Si la base se entrega con los datos ya cargados, esa
demostracion no puede realizarse en la evaluacion tecnica.

Uso (deja el repo con el dump limpio):
  docker compose run --rm web odoo shell -c <db> < scripts/utilidad/generar_base_limpia.py
"""
import logging

_logger = logging.getLogger(__name__)

env = env(user=env.ref("base.user_admin"))

# Productos del servicio interno de Odoo que NO deben eliminarse
CODIGOS_A_ELIMINAR = None  # None = eliminar todos los que tengan default_code propio


def eliminar_transacciones():
    """Borra documentos transaccionales (ventas, compras, inventario)."""
    # --- Pedidos de venta y cotizaciones
    ventas = env["sale.order"].search([])
    if ventas:
        _logger.info("Eliminando %d pedido(s) de venta: %s",
                     len(ventas), ", ".join(ventas.mapped("name")))
        ventas.with_context(active_test=False).unlink()



    # --- Ordenes de compra
    compras = env["purchase.order"].search([])
    if compras:
        _logger.info("Eliminando %d orden(es) de compra: %s",
                     len(compras), ", ".join(compras.mapped("name")))
        compras.with_context(active_test=False).unlink()

    # --- Acuerdos marco (blanket orders)
    requisiciones = env["purchase.requisition"].search([])
    if requisiciones:
        _logger.info("Eliminando %d acuerdo(s) marco: %s",
                     len(requisiciones), ", ".join(requisiciones.mapped("name")))
        requisiciones.unlink()

    # --- Reglas de reposicion
    reglas = env["stock.warehouse.orderpoint"].search([])
    if reglas:
        _logger.info("Eliminando %d regla(s) de reposicion", len(reglas))
        reglas.unlink()

    # --- Movimientos de inventario
    # Odoo bloquea el borrado por ORM de movimientos cuyo picking ya esta
    # validado ("You can not delete product moves if the picking is done").
    # Como aqui se busca resetear la base completa, se eliminan por SQL.
    env.cr.execute("SELECT COUNT(*) FROM stock_move")
    n_mov = env.cr.fetchone()[0]
    if n_mov:
        _logger.info("Eliminando %d movimiento(s) de stock (via SQL)", n_mov)
        env.cr.execute("DELETE FROM stock_move")

    env.cr.execute("SELECT COUNT(*) FROM stock_valuation_layer")
    n_capas = env.cr.fetchone()[0]
    if n_capas:
        _logger.info("Eliminando %d capa(s) de valoracion (via SQL)", n_capas)
        env.cr.execute("DELETE FROM stock_valuation_layer")

    env.cr.execute("SELECT COUNT(*) FROM stock_quant")
    n_quants = env.cr.fetchone()[0]
    if n_quants:
        _logger.info("Eliminando %d quant(s) (via SQL)", n_quants)
        env.cr.execute("DELETE FROM stock_quant")


def eliminar_datos_maestros():
    """Borra productos, clientes y proveedores cargados."""
    # --- Productos de hardware
    # Se ARCHIVAN (active = False) en lugar de eliminarse: el producto de
    # servicio "Standard delivery" esta referenciado por el transportista
    # (delivery_carrier) y otros internos, y el borrado falla por restriccion
    # de llave foranea. Al archivar, el catalogo queda vacio para la
    # demostracion y una reimportacion posterior los reactiva.
    #
    # Se hace por SQL porque el campo 'active' vive en product_template y el
    # filtrado por 'type' a traves de product.product no es confiable.
    env.cr.execute(
        "SELECT COUNT(*) FROM product_template "
        "WHERE default_code IS NOT NULL AND active = true")
    n_prod = env.cr.fetchone()[0]
    if n_prod:
        _logger.info("Archivando %d producto(s) de hardware", n_prod)
        env.cr.execute(
            "UPDATE product_template SET active = false "
            "WHERE default_code IS NOT NULL")

    # --- Proveedores y clientes (conservando los usuarios internos)
    partners = env["res.partner"].search([
        "|", ("supplier_rank", ">", 0), ("customer_rank", ">", 0)
    ])
    if partners:
        _logger.info("Eliminando %d cliente(s)/proveedor(es): %s", len(partners),
                     ", ".join(partners.mapped("name")))
        partners.with_context(active_test=False).unlink()

    # --- Categorias de producto creadas para el catalogo de hardware
    # Los productos archivados siguen apuntando a ellas, por lo que primero
    # se desvincula cualquier referencia y luego se eliminan.
    cats = env["product.category"].search([
        ("name", "in", [
            "Procesador", "Memoria RAM", "SSD", "Disco Duro",
            "Switch", "Servidor", "Tarjeta Madre",
        ])
    ])
    if cats:
        _logger.info("Eliminando %d categoria(s) de producto", len(cats))
        env["product.template"].search([("categ_id", "in", cats.ids)]).write(
            {"categ_id": env.ref("product.product_category_all").id})
        cats.unlink()


def verificar():
    _logger.info("")
    _logger.info("=== VERIFICACION BASE LIMPIA ===")
    _logger.info("Productos con codigo      : %d",
                 env["product.product"].search_count([("default_code", "!=", False)]))
    _logger.info("Proveedores (supplier_rank): %d",
                 env["res.partner"].search_count([("supplier_rank", ">", 0)]))
    _logger.info("Clientes (customer_rank)  : %d",
                 env["res.partner"].search_count([("customer_rank", ">", 0)]))
    _logger.info("Ordenes de compra         : %d", env["purchase.order"].search_count([]))
    _logger.info("Pedidos de venta          : %d", env["sale.order"].search_count([]))
    _logger.info("Reglas de reposicion     : %d",
                 env["stock.warehouse.orderpoint"].search_count([]))
    _logger.info("Quants con cantidad       : %d",
                 env["stock.quant"].search_count([("quantity", "!=", 0)]))
    _logger.info("")
    _logger.info("-- CONFIGURACION CONSERVADA --")
    _logger.info("Etapas del pipeline CRM   : %d", env["crm.stage"].search_count([]))
    _logger.info("Oportunidades CRM         : %d", env["crm.lead"].search_count([]))
    _logger.info("Plantillas de correo      : %d", env["mail.template"].search_count([]))
    _logger.info("Campanas de email         : %d", env["mailing.mailing"].search_count([]))
    menu_ventas = env.ref("sale.sale_menu_root", raise_if_not_found=False)
    _logger.info("Menu Ventas activo        : %s", menu_ventas.active if menu_ventas else "n/a")


def main():
    eliminar_transacciones()
    eliminar_datos_maestros()
    env.cr.commit()
    verificar()
    env.cr.commit()
    _logger.info("")
    _logger.info("Base limpia lista. Para persistir en el repo, ejecutar pg_dump.")


main()