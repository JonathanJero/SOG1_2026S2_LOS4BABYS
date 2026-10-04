# -*- coding: utf-8 -*-
"""Asigna los grupos de Ventas al usuario administrador.

En TechCore_DB el usuario admin@techcore.gt se creo antes de que el modulo
'sale' estuviera instalado, por lo que nunca se le asignaron los grupos de
Ventas. Odoo filtra los menus por grupo, asi que la app 'Sales' no aparecia
aunque el menu raiz estuviera activo.

Uso:
  docker compose run --rm web odoo shell -c <db> < scripts/asignar_grupos_ventas.py
"""
import logging

_logger = logging.getLogger(__name__)

GRUPOS = [
    "sales_team.group_sale_manager",      # Sales Manager
    "sales_team.group_sale_salesman",     # Sales / User
    "sales.group_sale_salesman",          # User: Own Documents Only
    "sales.group_sale_salesman_all_leads",  # User: All Documents
]

env = env(user=env.ref("base.user_admin"))


def main():
    usuario = env.ref("base.user_admin")
    agregados = []
    for xmlid in GRUPOS:
        grupo = env.ref(xmlid, raise_if_not_found=False)
        if not grupo:
            _logger.info("Grupo no encontrado: %s", xmlid)
            continue
        if usuario in grupo.users:
            _logger.info("Ya tiene: %s", grupo.name)
            continue
        grupo.sudo().write({"users": [(4, usuario.id)]})
        agregados.append(grupo.name)
    env.cr.commit()
    _logger.info("Grupos agregados a %s: %s",
                 usuario.login, agregados or "ninguno (ya los tenia)")

    # Verificacion: los grupos de ventas ya deben estar asignados
    for xmlid in GRUPOS:
        grupo = env.ref(xmlid, raise_if_not_found=False)
        if grupo:
            _logger.info("  %s -> %s", grupo.name, usuario in grupo.users)


main()