# -*- coding: utf-8 -*-
"""Repara el menu raiz de Ventas al arrancar el entorno.

Problema que corrige
--------------------
El snapshot original de TechCore_DB se creo sin el modulo 'sale' instalado,
por lo que su menu raiz (xmlid sale.sale_menu_root) quedo archivado
(ir_ui_menu.active = False). Al restaurar ese dump, los submenus (Quotations,
Orders, Customers) existen y estan activos, pero Odoo no muestra la aplicacion
de Ventas porque el padre esta archivado.

Este script es idempotente: si el menu ya esta activo no hace nada y sale con
codigo 0. Lo ejecuta start.sh en cada arranque como red de seguridad, para
que el menu quede disponible sin importar con que dump se restaure.

Uso:
  docker compose run --rm -T web odoo shell -c /etc/odoo/odoo.conf \
      -d TechCore_DB --db_host=db --stop-after-init --log-level=warn \
      < scripts/activar_menu_ventas.py
"""
import logging

_logger = logging.getLogger(__name__)

# Menus raiz que deben quedar visibles para el usuario administrador
MENUS_A_ACTIVAR = [
    ("sale.sale_menu_root", "Ventas"),
]

# Grupos de Ventas que el usuario administrador debe tener
GRUPOS_VENTAS = [
    "sales_team.group_sale_manager",
    "sales_team.group_sale_salesman",
    "sales_team.group_sale_salesman_all_leads",
]

env = env(user=env.ref("base.user_admin"))


def activar_menus():
    """Desarchiva los menus raiz indicados. Devuelve cuantos cambio."""
    cambios = 0
    for xmlid, etiqueta in MENUS_A_ACTIVAR:
        menu = env.ref(xmlid, raise_if_not_found=False)
        if menu is None:
            _logger.warning("[WARN] Menu no encontrado: %s", xmlid)
            continue
        if menu.active:
            _logger.info("[OK] Menu '%s' ya activo (id=%s)", etiqueta, menu.id)
            continue
        menu.active = True
        cambios += 1
        _logger.info("[FIX] Menu '%s' reactivado (id=%s)", etiqueta, menu.id)
    return cambios


def revisar_grupos():
    """Verifica que el administrador tenga los grupos de Ventas."""
    usuario = env.ref("base.user_admin")
    faltantes = []
    for xmlid in GRUPOS_VENTAS:
        grupo = env.ref(xmlid, raise_if_not_found=False)
        if grupo is None:
            _logger.warning("[WARN] Grupo no encontrado: %s", xmlid)
            continue
        if usuario not in grupo.users:
            grupo.sudo().write({"users": [(4, usuario.id)]})
            faltantes.append(grupo.name)
    if faltantes:
        _logger.info("[FIX] Grupos asignados a %s: %s",
                     usuario.login, ", ".join(faltantes))
    return faltantes


def main():
    cambios = activar_menus()
    revisar_grupos()
    env.cr.commit()

    raiz = env.ref("sale.sale_menu_root", raise_if_not_found=False)
    if raiz is None:
        _logger.warning("[WARN] No se pudo verificar el estado de Ventas.")
        return

    usuario = env.ref("base.user_admin")
    visibles = env["ir.ui.menu"]._visible_menu_ids(usuario)
    hijos = env["ir.ui.menu"].search([("parent_id", "=", raiz.id)])
    _logger.info("[OK] Ventas: activo=%s, %d submenus, visible para admin=%s",
                 raiz.active, len(hijos), raiz.id in visibles)
    _logger.info("[OK] Sin cambios adicionales" if not cambios
                 else "[OK] %d menu(s) reactivado(s)" % cambios)


main()