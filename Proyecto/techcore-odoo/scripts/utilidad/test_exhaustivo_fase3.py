# -*- coding: utf-8 -*-
"""Suite de Pruebas Exhaustivas de la Fase 3 - TechCore Solutions Guatemala.

Ejecuta una auditoria completa y rigurosa en 6 dimensiones criticas:
1. Capa de Base de Datos y Vistas de Business Intelligence (PostgreSQL).
2. Datos Maestros y Modelos en Odoo (ORM).
3. E-Commerce, Pasarelas de Pago y Automatizacion de CRM.
4. Trazabilidad Contable y de Inventario.
5. Prueba de Arranque Limpio y Restauracion desde dump.sql.gz.
6. Integridad de Documentacion, Enlaces y Reglas de Calidad (cero emojis).

Uso:
  python3 Proyecto/techcore-odoo/scripts/utilidad/test_exhaustivo_fase3.py
"""
import os
import re
import subprocess
import sys
import urllib.request

VM_IP = os.environ.get("TECHCORE_HOST", "192.168.64.11")
ODOO_URL = os.environ.get("TECHCORE_URL", f"http://{VM_IP}:8069")
USE_SSH = os.environ.get("TECHCORE_USE_SSH", "1" if VM_IP not in ("localhost", "127.0.0.1") else "0") == "1"
SSH_USER = os.environ.get("TECHCORE_SSH_USER", "jona")
SSH_CMD = ["ssh", "-o", "StrictHostKeyChecking=no", f"{SSH_USER}@{VM_IP}"] if USE_SSH else []

TOTAL_PRUEBAS = 0
PRUEBAS_PASADAS = 0
PRUEBAS_FALLADAS = 0
REPORTES = []


def registrar_resultado(categoria, nombre, exito, detalle=""):
    global TOTAL_PRUEBAS, PRUEBAS_PASADAS, PRUEBAS_FALLADAS
    TOTAL_PRUEBAS += 1
    if exito:
        PRUEBAS_PASADAS += 1
        estado = "[PASS]"
    else:
        PRUEBAS_FALLADAS += 1
        estado = "[FAIL]"
    msg = f"{estado} {categoria} :: {nombre}"
    if detalle:
        msg += f" -> {detalle}"
    print(msg)
    REPORTES.append((estado, categoria, nombre, detalle))


def run_ssh(cmd, wait_timeout=30):
    if SSH_CMD:
        full_cmd = SSH_CMD + [cmd]
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=wait_timeout)
    else:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=wait_timeout)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


def run_psql(query, db="TechCore_DB", user="odoo", env_vars=""):
    docker_cmd = f"{env_vars} docker exec techcore_postgres_db psql -U {user} -d {db} -t -A -c \"{query}\""
    if env_vars:
        docker_cmd = f"{env_vars} {docker_cmd}"
    return run_ssh(docker_cmd)


def run_odoo_shell(script_code):
    cmd = (
        f"docker exec -i techcore_odoo_web odoo shell -d TechCore_DB "
        f"--db_host techcore_postgres_db -r odoo -w techcore_secure_pwd "
        f"--no-http --log-level=warn"
    )
    if SSH_CMD:
        full_cmd = SSH_CMD + [cmd]
        proc = subprocess.run(
            full_cmd, input=script_code, capture_output=True, text=True, timeout=60
        )
    else:
        proc = subprocess.run(
            cmd, shell=True, input=script_code, capture_output=True, text=True, timeout=60
        )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


print("================================================================================")
print(" SUITE DE PRUEBAS EXHAUSTIVAS - TECHCORE SOLUTIONS GUATEMALA (FASE 3)")
print("================================================================================")

# ==============================================================================
# DIMENSION 1: CAPA DE BASE DE DATOS Y BUSINESS INTELLIGENCE
# ==============================================================================
print("\n--- 1. AUDITORIA DE BASE DE DATOS Y VISTAS DE BI (POSTGRESQL) ---")

# 1.1 Conectividad bi_reader
code, out, _ = run_psql("SELECT current_user;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
registrar_resultado("BI - Seguridad", "Autenticacion de bi_reader", code == 0 and out == "bi_reader", f"Usuario activo: {out}")

# 1.2 Existencia y permisos sobre las 4 vistas
vistas = ["v_bi_ventas_detalle", "v_bi_inventario", "v_bi_top_productos", "v_bi_compras"]
for v in vistas:
    code, out, _ = run_psql(f"SELECT count(*) FROM {v};", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
    registrar_resultado("BI - Vistas", f"Consulta en vista {v}", code == 0, f"Registros retornados: {out}")

# 1.3 Seguridad: bi_reader es de solo lectura (intento de escritura debe fallar)
code, out, err = run_psql("CREATE TABLE test_insegura(id int);", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
registrar_resultado("BI - Seguridad", "Denegacion de DDL a bi_reader", code != 0, f"Correctamente denegado: {err or 'Sin permisos'}")

# 1.4 Cobertura temporal de v_bi_ventas_detalle (al menos 8 semanas continuas)
code, out, _ = run_psql("SELECT count(DISTINCT semana) FROM v_bi_ventas_detalle;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
semanas = int(out) if code == 0 and out.isdigit() else 0
registrar_resultado("BI - Temporalidad", "Cobertura de semanas en ventas", semanas >= 8, f"{semanas} semanas registradas (Requerido >= 8)")

# 1.5 Canales de venta en v_bi_ventas_detalle (Web y Cotizacion presentes)
code, out, _ = run_psql("SELECT DISTINCT canal FROM v_bi_ventas_detalle ORDER BY canal;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
canales = out.splitlines() if code == 0 else []
registrar_resultado("BI - Canales", "Presencia de canales Web y Cotizacion", "Web" in canales and "Cotización" in canales, f"Canales: {canales}")

# 1.6 Segmentacion en v_bi_ventas_detalle (B2B y B2C presentes)
code, out, _ = run_psql("SELECT DISTINCT segmento FROM v_bi_ventas_detalle ORDER BY segmento;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
segmentos = out.splitlines() if code == 0 else []
registrar_resultado("BI - Segmentos", "Presencia de segmentos B2B y B2C", "B2B" in segmentos and "B2C" in segmentos, f"Segmentos: {segmentos}")

# 1.7 Sin valores NULL en campos criticos de ventas
code, out, _ = run_psql("SELECT count(*) FROM v_bi_ventas_detalle WHERE orden IS NULL OR fecha IS NULL OR producto IS NULL OR cantidad IS NULL OR precio_unitario IS NULL OR subtotal IS NULL;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
nulos_ventas = int(out) if code == 0 and out.isdigit() else -1
registrar_resultado("BI - Calidad Datos", "Cero valores NULL en ventas detalle", nulos_ventas == 0, f"Campos nulos detectados: {nulos_ventas}")

# 1.8 Productos en v_bi_inventario y alertas de stock bajo
code, out_tot, _ = run_psql("SELECT count(*) FROM v_bi_inventario;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
code_bajo, out_bajo, _ = run_psql("SELECT count(*) FROM v_bi_inventario WHERE estado_stock = 'Bajo';", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
tot_inv = int(out_tot) if code == 0 and out_tot.isdigit() else 0
bajo_inv = int(out_bajo) if code_bajo == 0 and out_bajo.isdigit() else 0
registrar_resultado("BI - Inventario", "21 productos en inventario con stock bajo activo", tot_inv == 21 and bajo_inv >= 3, f"Total productos: {tot_inv}, Con stock bajo: {bajo_inv}")

# 1.9 Ranking continuo en v_bi_top_productos
code, out_rank, _ = run_psql("SELECT min(ranking), max(ranking) FROM v_bi_top_productos;", user="bi_reader", env_vars="PGPASSWORD=bi_reader_techcore")
registrar_resultado("BI - Top Productos", "Calculo de ranking denso", code == 0 and "1|" in out_rank, f"Rango de ranking: {out_rank}")


# ==============================================================================
# DIMENSION 2: DATOS MAESTROS Y MODELOS EN ODOO (ORM)
# ==============================================================================
print("\n--- 2. AUDITORIA DE DATOS MAESTROS EN ODOO (ORM) ---")

script_orm = """
e = env(user=env.ref('base.user_admin'))
prods = e['product.template'].search([('default_code', '=like', 'PROD-%')])
custs = e['res.partner'].search([('customer_rank', '>', 0)])
supps = e['res.partner'].search([('supplier_rank', '>', 0)])
supp_lines = e['product.supplierinfo'].search([])
reorder_rules = e['stock.warehouse.orderpoint'].search([])

prods_pub = prods.filtered(lambda p: p.is_published and p.website_published)
prods_img = prods.filtered(lambda p: bool(p.image_1920))
prods_desc = prods.filtered(lambda p: bool(p.description_sale and len(p.description_sale) > 20))
prods_policy = prods.filtered(lambda p: p.invoice_policy == 'order')

print(f"PRODS_TOTAL={len(prods)}")
print(f"PRODS_PUB={len(prods_pub)}")
print(f"PRODS_IMG={len(prods_img)}")
print(f"PRODS_DESC={len(prods_desc)}")
print(f"PRODS_POLICY={len(prods_policy)}")
print(f"CUSTS_TOTAL={len(custs)}")
print(f"SUPPS_TOTAL={len(supps)}")
print(f"SUPP_LINES={len(supp_lines)}")
print(f"REORDER_RULES={len(reorder_rules)}")
"""

code, out, _ = run_odoo_shell(script_orm)
orm_data = dict(re.findall(r"([A-Z_]+)=(\d+)", out))

registrar_resultado("ORM - Productos", "21 productos creados y almacenables", orm_data.get("PRODS_TOTAL") == "21", f"Total: {orm_data.get('PRODS_TOTAL')}")
registrar_resultado("ORM - Publicacion", "21 productos publicados en web", orm_data.get("PRODS_PUB") == "21", f"Publicados: {orm_data.get('PRODS_PUB')}")
registrar_resultado("ORM - Imagenes", "21 productos con imagenes reales cargadas", orm_data.get("PRODS_IMG") == "21", f"Con imagen: {orm_data.get('PRODS_IMG')}")
registrar_resultado("ORM - Fichas", "21 productos con descripciones tecnicas formales", orm_data.get("PRODS_DESC") == "21", f"Con descripcion: {orm_data.get('PRODS_DESC')}")
registrar_resultado("ORM - Facturacion", "21 productos con politica invoice_policy='order'", orm_data.get("PRODS_POLICY") == "21", f"Con politica: {orm_data.get('PRODS_POLICY')}")
registrar_resultado("ORM - Contactos", "Al menos 6 clientes registrados (incluyendo Pedro Gomez)", int(orm_data.get("CUSTS_TOTAL", 0)) >= 6, f"Clientes: {orm_data.get('CUSTS_TOTAL')}")
registrar_resultado("ORM - Proveedores", "4 proveedores registrados (incluyendo Distribuidora Tecno)", orm_data.get("SUPPS_TOTAL") == "4", f"Proveedores: {orm_data.get('SUPPS_TOTAL')}")
registrar_resultado("ORM - Precios", "61 lineas de precio de proveedor (product.supplierinfo)", orm_data.get("SUPP_LINES") == "61", f"Lineas: {orm_data.get('SUPP_LINES')}")
registrar_resultado("ORM - Reposicion", "4 reglas de reposicion configuradas", orm_data.get("REORDER_RULES") == "4", f"Reglas: {orm_data.get('REORDER_RULES')}")


# ==============================================================================
# DIMENSION 3: E-COMMERCE, PORTAL Y PASARELAS DE PAGO
# ==============================================================================
print("\n--- 3. AUDITORIA DE E-COMMERCE Y PORTAL WEB ---")

# 3.1 Pruebas HTTP de rutas publicas
rutas = [
    ("/", "Portada Institucional"),
    ("/shop", "Catalogo de Productos"),
    ("/shop/cart", "Carrito de Compras"),
    ("/web/signup", "Registro Libre de Clientes"),
    ("/web/login", "Acceso al Sistema"),
    ("/my", "Portal del Cliente"),
]

for ruta, desc in rutas:
    try:
        req = urllib.request.Request(f"{ODOO_URL}{ruta}", headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=8)
        status = res.status
    except Exception as e:
        status = str(e)
    registrar_resultado("E-Commerce - HTTP", f"Ruta {ruta} ({desc})", status == 200, f"Status: {status}")

# 3.2 Pasarelas de pago y automatizacion de CRM
script_pago_crm = """
e = env(user=env.ref('base.user_admin'))
demo = e['payment.provider'].search([('code', '=', 'demo')], limit=1)
transf = e['payment.provider'].search([('code', '=', 'custom')], limit=1)
leads_web = e['crm.lead'].search([('tag_ids.name', '=', 'Web B2C')])
rule_crm = e['base.automation'].search([('name', '=', 'Generar Lead CRM desde Pedido Web')], limit=1)

print(f"PAGO_DEMO={demo.state == 'test' and demo.is_published}")
print(f"PAGO_TRANSF={transf.state == 'enabled' and transf.is_published}")
print(f"RULE_CRM_ACTIVE={bool(rule_crm and rule_crm.active)}")
print(f"LEADS_WEB_COUNT={len(leads_web)}")
"""
code, out, _ = run_odoo_shell(script_pago_crm)
crm_data = dict(re.findall(r"([A-Z_]+)=([^\n\r]+)", out))

registrar_resultado("E-Commerce - Pagos", "Proveedor Demo activo (test y publicado)", crm_data.get("PAGO_DEMO") == "True", "Demo verificado")
registrar_resultado("E-Commerce - Pagos", "Transferencia Bancaria activa (enabled y publicada)", crm_data.get("PAGO_TRANSF") == "True", "Transferencia verificada")
registrar_resultado("CRM - Automatizacion", "Regla de automatizacion activa para pedidos web", crm_data.get("RULE_CRM_ACTIVE") == "True", "Regla base.automation activa")
registrar_resultado("CRM - Trazabilidad", "Oportunidades con etiqueta 'Web B2C' generadas", int(crm_data.get("LEADS_WEB_COUNT", 0)) > 0, f"Leads generados: {crm_data.get('LEADS_WEB_COUNT')}")


# ==============================================================================
# DIMENSION 4: TRAZABILIDAD CONTABLE Y DE INVENTARIO
# ==============================================================================
print("\n--- 4. AUDITORIA DE TRAZABILIDAD CONTABLE Y OPERATIVA ---")

# 4.1 Facturas de las ordenes sembradas deben estar en estado 'posted' y 'paid'
code, out, _ = run_psql("""
SELECT count(*), 
       count(*) FILTER (WHERE state = 'posted'), 
       count(*) FILTER (WHERE payment_state = 'paid') 
FROM account_move 
WHERE move_type = 'out_invoice' AND invoice_origin LIKE 'S000%';
""")
tot_inv, posted_inv, paid_inv = (out.split("|") if code == 0 else [0, 0, 0])
registrar_resultado("Contabilidad - Facturas", "Facturas de venta publicadas y pagadas", tot_inv == posted_inv == paid_inv and int(tot_inv) >= 75, f"Total: {tot_inv}, Publicadas: {posted_inv}, Pagadas: {paid_inv}")

# 4.2 Despachos en stock_picking deben estar en estado 'done'
code, out, _ = run_psql("""
SELECT count(*), 
       count(*) FILTER (WHERE state = 'done') 
FROM stock_picking 
WHERE origin LIKE 'S000%';
""")
tot_pick, done_pick = (out.split("|") if code == 0 else [0, 0])
registrar_resultado("Inventario - Albaranes", "Despachos de venta completados (done)", tot_pick == done_pick and int(tot_pick) >= 75, f"Total: {tot_pick}, Completados: {done_pick}")

# 4.3 Capas de valoracion de inventario presentes
code, out, _ = run_psql("SELECT count(*) FROM stock_valuation_layer;")
capas = int(out) if code == 0 and out.isdigit() else 0
registrar_resultado("Inventario - Valoracion", "Capas de valoracion de stock activas", capas >= 100, f"Total capas contables: {capas}")


# ==============================================================================
# DIMENSION 5: PRUEBA DE ARRANQUE LIMPIO Y RESTAURACION DESDE DUMP
# ==============================================================================
print("\n--- 5. PRUEBA DE ARRANQUE LIMPIO Y RESTAURACION DESDE DUMP.SQL.GZ ---")

# Creamos una base de datos temporal 'TechCore_DB_TestClean', restauramos dump.sql.gz y aplicamos vistas_bi.sql
cmd_clean_test = """
docker exec techcore_postgres_db dropdb -U odoo --if-exists TechCore_DB_TestClean && \
docker exec techcore_postgres_db createdb -U odoo -O odoo TechCore_DB_TestClean && \
docker exec techcore_postgres_db bash -c "gunzip -c /docker-entrypoint-initdb.d/dump.sql.gz | psql -U odoo -d TechCore_DB_TestClean --quiet" && \
docker exec techcore_postgres_db psql -U odoo -d TechCore_DB_TestClean -f /docker-entrypoint-initdb.d/vistas_bi.sql && \
docker exec techcore_postgres_db psql -U odoo -d TechCore_DB_TestClean -t -A -c "
SELECT 
  (SELECT count(*) FROM product_template WHERE default_code LIKE 'PROD-%') || '|' ||
  (SELECT count(*) FROM sale_order WHERE client_order_ref = 'DEMO-SEED') || '|' ||
  (SELECT count(*) FROM v_bi_ventas_detalle) || '|' ||
  (SELECT count(*) FROM v_bi_inventario)
"
"""
code, out, err = run_ssh(cmd_clean_test, wait_timeout=90)
pipe_lines = [l.strip() for l in out.splitlines() if "|" in l]
clean_stats = pipe_lines[-1].split("|") if code == 0 and pipe_lines else []

if len(clean_stats) == 4:
    c_prod, c_so, c_bi_so, c_bi_inv = clean_stats
    exito_clean = (c_prod == "21" and int(c_so) >= 75 and int(c_bi_so) >= 100 and c_bi_inv == "21")
    detalle_clean = f"Productos: {c_prod}, Ventas: {c_so}, BI Ventas: {c_bi_so}, BI Inv: {c_bi_inv}"
else:
    exito_clean = False
    detalle_clean = f"Error en restauracion: {err}"

registrar_resultado("Arranque Limpio", "Restauracion integra desde dump.sql.gz en BD nueva", exito_clean, detalle_clean)

# Limpieza de la base de prueba
run_ssh("docker exec techcore_postgres_db dropdb -U odoo --if-exists TechCore_DB_TestClean")


# ==============================================================================
# DIMENSION 6: DOCUMENTACION, ENLACES Y REGLAS DE CALIDAD
# ==============================================================================
print("\n--- 6. AUDITORIA DE DOCUMENTACION Y CALIDAD ---")

# 6.1 Comprobacion de imagenes en manual_ecommerce_jonathan.md
manual_path = "Proyecto/Fase3/docu/manual_ecommerce_jonathan.md"
if os.path.exists(manual_path):
    with open(manual_path, "r", encoding="utf-8") as f:
        doc_content = f.read()
    imagenes = re.findall(r"!\[.*?\]\((.*?)\)", doc_content)
    rotas = []
    for img in imagenes:
        img_full = os.path.normpath(os.path.join(os.path.dirname(manual_path), img))
        if not os.path.isfile(img_full):
            rotas.append(img)
    registrar_resultado("Documentacion", f"Integridad de imagenes en {os.path.basename(manual_path)}", len(rotas) == 0 and len(imagenes) >= 8, f"Total imagenes: {len(imagenes)}, Rotas: {len(rotas)}")
else:
    registrar_resultado("Documentacion", "Existencia de manual_ecommerce_jonathan.md", False, "Archivo no encontrado")

# 6.2 Regla de calidad: Cero emojis en archivos clave de Fase 3
archivos_calidad = [
    "Proyecto/Fase3/docu/manual_ecommerce_jonathan.md",
    "Proyecto/Fase3/bi/vistas_bi.sql",
    "Proyecto/techcore-odoo/start.sh",
    "Proyecto/techcore-odoo/start.ps1",
    "Proyecto/techcore-odoo/README.md",
]
emojis_totales = 0
for fpath in archivos_calidad:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            emojis = [c for c in content if ord(c) > 0x1F600]
            emojis_totales += len(emojis)

registrar_resultado("Reglas de Proyecto", "Cero emojis en codigo, markdown y scripts", emojis_totales == 0, f"Emojis encontrados: {emojis_totales}")

# 6.3 Ejecutabilidad de scripts
scripts_ejecutables = [
    "Proyecto/techcore-odoo/start.sh",
    "Proyecto/techcore-odoo/db-init/01-restore-techcore.sh",
    "Proyecto/techcore-odoo/db-init/02-crear-bi-reader.sh",
]
todos_ejecutables = all(os.access(p, os.X_OK) for p in scripts_ejecutables if os.path.exists(p))
registrar_resultado("Portabilidad", "Permisos de ejecucion en scripts POSIX", todos_ejecutables, "chmod +x verificado")


# ==============================================================================
# BALANCE FINAL
# ==============================================================================
print("\n================================================================================")
print(f" RESUMEN FINAL DE PRUEBAS: {PRUEBAS_PASADAS} / {TOTAL_PRUEBAS} PASADAS ({PRUEBAS_FALLADAS} FALLADAS)")
print("================================================================================")

if PRUEBAS_FALLADAS == 0:
    print(">>> CERTIFICACION DE CALIDAD FASE 3: APROBADA AL 100% <<<")
    sys.exit(0)
else:
    print(">>> ALERTA: EXISTEN PRUEBAS FALLADAS. REVISAR EL DETALLE SUPERIOR <<<")
    sys.exit(1)
