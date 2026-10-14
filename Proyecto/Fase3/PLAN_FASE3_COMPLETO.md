# Plan Completo de la Fase 3: TechCore Solutions Guatemala

**Documento maestro de planeación y de ejecución técnica.**
Está escrito para que una persona o una IA lo ejecute de principio a fin sin contexto previo. Toda la parte técnica de Jonathan (Parte A) y la integración final se desarrollan desde este archivo. Las partes de Julio y Francisco tienen sus propios archivos:

- [TAREAS_JULIO.md](TAREAS_JULIO.md): pruebas end-to-end, manual de usuario, conclusiones, escalabilidad y presentación.
- [TAREAS_FRANCISCO.md](TAREAS_FRANCISCO.md): reportes de Business Intelligence en Power BI.

---

## 0. Reglas obligatorias del proyecto

1. **Cero emojis** en código, Markdown, plantillas, scripts, mensajes de commit y documentos. Si hace falta un ícono, usar SVG o texto.
2. **Español formal con tildes y eñes** en todo texto visible o documentado.
3. **Sin placeholders:** si hace falta una imagen (productos, banners), generarla de verdad.
4. **Un solo dueño del dump:** solo Jonathan modifica `dump.sql.gz`, `TechCore_DB_backup.zip` y `filestore/`. Los demás suben solo documentos, capturas y su `.pbix`, con nombres de archivo propios (ver sección 9).
5. **Nada se da por hecho sin verificar:** cada hito termina con una verificación explícita (comando o prueba) y su resultado.
6. La evaluación técnica de la Fase 3 se hará, probablemente, **en la máquina Windows de Francisco** (por Power BI). Por lo tanto, todo debe **levantar desde cero con `start.sh`** (y con una alternativa para Windows, ver el hito A5).

---

## 1. Contexto del proyecto

- **Curso:** Sistemas Organizacionales y Gerenciales 1 (SOG1), USAC, segundo semestre 2026, Grupo 7, sección A.
- **Empresa ficticia:** TechCore Solutions Guatemala (comercio de hardware: procesadores, RAM, SSD, discos, switches, servidores, tarjetas madre).
- **Pila tecnológica:** Odoo 17.0 Community Edition + PostgreSQL 15 en Docker, sobre Ubuntu Server 22.04 (VM en UTM, Mac M2). Meta de integración: ERP + CRM + E-commerce + BI con trazabilidad del 100%.
- **Integrantes:**

| Integrante | Carnet | Rol en la Fase 3 |
|---|---|---|
| Jonathan Eliud Jerónimo Salguero | 202300353 | Parte A: datos, e-commerce, infraestructura para BI, consolidación final |
| Francisco Gerardo Castillo Sagastume (usuario Git: Gerardin0, a quien el grupo llama "Gerardo") | 202300653 | Parte B: Power BI (tiene Windows) |
| Julio Alfredo Herrera Orantes | 202300850 | Parte C: pruebas E2E, manual de usuario, conclusiones, presentación |

- **Enunciado de la Fase 3 (resumen):** sitio e-commerce con catálogo de al menos 20 productos, carrito de compras, registro de clientes, facturación y portal de cliente; pruebas de flujo completo (compra, inventario, CRM, portal); reportes de BI de inventario (existencias, stock bajo) y de ventas (evolución diaria, semanal y mensual, top 5 de productos) en Power BI; conclusiones y escalabilidad; presentación final; video demostrativo en Google Drive.
- **Rúbrica:** Fase 3 vale 100 puntos (40 de habilidades y 60 de conocimiento). El desglose fino todavía no se conoce; Jonathan lo entregará cuando lo tenga y este plan se ajusta. Mientras tanto se asume el mismo estilo de la Fase 2 (carga y flujo de datos, módulo avanzado, CRM, cumplimiento de entregables).

---

## 2. Acceso y entorno

| Elemento | Valor |
|---|---|
| Repositorio | `https://github.com/JonathanJero/SOG1_2026S2_LOS4BABYS` (rama `main`) |
| Ruta local de trabajo | `.../SOG1_2026S2_LOS4BABYS/Proyecto/techcore-odoo/` (infraestructura central del ERP) |
| VM | `ssh jona@192.168.64.11` (el acceso por llave o contraseña lo tiene Jonathan) |
| Carpeta en la VM | `/home/jona/techcore-odoo` (contiene `config/`, `addons/`, `filestore/`, `db-init/`, `docker-compose.yml`) |
| Contenedores | `techcore_odoo_web` (Odoo 17) y `techcore_postgres_db` (PostgreSQL 15) |
| URL de Odoo | `http://192.168.64.11:8069` (en máquinas locales: `http://localhost:8069`) |
| Base de datos | `TechCore_DB` |
| Usuario Odoo | `admin@techcore.gt`, contraseña `1234` |
| Master password (gestor de BD) | `techcore_master_pwd` |
| Usuario PostgreSQL | `odoo`, contraseña `techcore_secure_pwd` |

**Comando base para ejecutar scripts de Odoo en la VM** (probado):

```bash
ssh jona@192.168.64.11 "docker exec -i techcore_odoo_web odoo shell -d TechCore_DB \
  --db_host techcore_postgres_db -r odoo -w techcore_secure_pwd --no-http --log-level=warn" < script.py
```

**Consulta SQL rápida en la VM:**

```bash
ssh jona@192.168.64.11 "docker exec techcore_postgres_db psql -U odoo -d TechCore_DB -c 'SELECT 1;'"
```

---

## 3. Estructura del repositorio relevante

```text
Proyecto/
├── techcore-odoo/                        (servidor ERP central unificado)
│   ├── docker-compose.yml, start.sh, start.ps1, README.md
│   ├── config/odoo.conf, db-init/ (dump.sql.gz, vistas_bi.sql y scripts)
│   ├── backup/TechCore_DB_backup.zip, filestore/TechCore_DB/
│   ├── 0_Categorias_Odoo.xlsx ... 5_Precios_Proveedores_Odoo.xlsx
│   ├── Datos_Maestros_TechCore_Fase2.xlsx
│   └── scripts/ y scripts/utilidad/   (scripts de carga y auditoría)
├── Fase2/                                (entregables históricos Fase 2)
│   ├── enunciado.md                      (enunciado general)
│   ├── contexto.md                       (bitácora técnica)
│   ├── instrucciones_fase_2_quetzaldev.md
│   ├── docu/                             (manuales de la Fase 2 y capturas)
│   └── plantillas-correo/                (2 plantillas HTML con SVG)
└── Fase3/                                (entregables y planeación Fase 3)
    ├── PLAN_FASE3_COMPLETO.md
    ├── TAREAS_JULIO.md
    ├── TAREAS_FRANCISCO.md
    ├── docu/                             (manual técnico eCommerce y 9 capturas)
    └── bi/                               (vistas analíticas y .pbix)
```

---

## 4. Estado actual verificado (12 de octubre de 2026)

| Elemento | Estado |
|---|---|
| Módulos instalados | `website_sale`, `website_sale_stock`, `account`, `portal`, `crm`, `sale_crm`, `website_crm`, `stock`, `purchase`, `mass_mailing`, `purchase_requisition_stock` y dependencias |
| Módulos **no** instalados | `sale_management` (cotizaciones), `payment_demo` (pago simulado) |
| CRM (Fase 2) | 4 etapas (Lead, Contactado, Negociación, Cerrado), 5 oportunidades, etiquetas B2B, Juan Pérez ganado |
| Portada web | Página de inicio corporativa con SVG (vistas `website.page` 1244/1252 modificadas en la Fase 2) |
| Menús | El menú raíz de Ventas se reactiva con un arreglo dentro de `start.sh` |

**Datos maestros cargados hoy en la VM (en vivo, sin exportar al repositorio todavía):** el 12 de octubre se ejecutaron en la VM los scripts `import_datos_maestros.py`, `actualizar_clientes.py` y `reaplicar_inventario.py`. Resultado esperado (verificar con el hito A1): 20 productos, 7 categorías, 3 proveedores, 5 clientes e inventario inicial en `WH/Stock`. **No se ha regenerado `dump.sql.gz`**, por lo que el repositorio todavía refleja la base limpia de la Fase 2.

**Pendiente de datos:**
- Los **60 precios de proveedor** (`5_Precios_Proveedores_Odoo.xlsx`): el script solo creó una línea de proveedor por producto; hay que cargar el Excel completo para tener tres proveedores por producto.
- Los **extras de la Fase 2** que el grupo decidió conservar: producto `PROD-021` Logitech MX Keys (categoría `Periféricos`, precio de venta Q 100.00, costo Q 70.00, almacenable, 10 unidades iniciales), cliente `Pedro Gómez` (individual, con teléfono y correo) y proveedor `Distribuidora Tecno S.A.` (con su precio de Q 70.00 para `PROD-021`). Revisar `Proyecto/Fase2/docu/manual_tecnico_datos_inventario_julio.md`, sección 4, para los datos exactos.
- Las **reglas de reposición** de Francisco para `PROD-009`, `PROD-010`, `PROD-018` y `PROD-007` (mínimos y máximos en `docu/manual_tecnico_compras_cotizaciones_francisco.md`, sección 3.2). Se necesitan para las pruebas de reposición y para la alerta de stock bajo del BI.

---

## 5. Parte A: Datos maestros, e-commerce, infraestructura para BI (Jonathan)

### Hito A1: Repoblar y verificar la base (desbloquea a todos)

1. Verificar el estado:

```sql
SELECT count(*) FROM product_template WHERE default_code LIKE 'PROD-%';           -- esperado 20 (21 con el extra)
SELECT count(*) FROM res_partner WHERE customer_rank > 0;                         -- esperado 5 (6 con Pedro Gómez)
SELECT count(*) FROM res_partner WHERE supplier_rank > 0;                         -- esperado 3 (4 con Distribuidora Tecno)
SELECT count(*) FROM stock_quant sq JOIN stock_location sl ON sl.id = sq.location_id WHERE sl.usage = 'internal';
```

2. Cargar los **60 precios de proveedor** desde `5_Precios_Proveedores_Odoo.xlsx` (columnas `partner_id`, `product_id/default_code`, `min_qty`, `price`, `delay`). Hacerlo con un script Python que lea el Excel (`openpyxl`, disponible en la imagen de Odoo) y cree o actualice `product.supplierinfo`. Debe ser idempotente.
3. Crear los **extras** (`PROD-021`, `Pedro Gómez`, `Distribuidora Tecno S.A.`, categoría `Periféricos`) con un script idempotente que se guarde en `scripts/` del repositorio.
4. Recrear las **reglas de reposición** (`stock.warehouse.orderpoint`) de Francisco en un script idempotente.
5. Verificar: cada producto del catálogo original tiene 3 líneas de proveedor; el catálogo suma 21 productos.
6. **No** regenerar el dump todavía (se hace en el hito A6, con todo lo demás ya configurado). Pero sí avisar al grupo: **"datos listos en la VM"**, porque Julio y Francisco necesitan trabajar.

> Importante para la evaluación: recordar que en la Fase 2 la rúbrica pedía demostrar la carga masiva y manual en vivo. En la Fase 3 el foco es el e-commerce y el BI, por lo que la base **sí** debe entregarse con datos. Los Excel de carga se conservan en el repositorio por trazabilidad.

### Hito A2: Módulos y configuración del e-commerce

1. Instalar `sale_management` y `payment_demo` (en la VM, con `-i` y reinicio de `techcore_odoo_web`).
2. **Publicar los 21 productos** en el sitio web:
   - Campo `website_published = True` y `is_published = True` en cada `product.template`.
   - Categorías de eCommerce (`product.public.category`) alineadas con las categorías internas (Procesador, Memoria RAM, SSD, Disco Duro, Switch, Servidor, Tarjeta Madre, Periféricos).
   - Descripción de venta (`description_sale`) en español con tildes, un párrafo técnico por producto.
   - **Imagen real** por producto (`image_1920`): generarla con la herramienta de generación de imágenes (render de producto sobre fondo neutro) o con una tarjeta tipográfica de marca generada con Python (Pillow). **Prohibido** dejar el ícono gris por defecto.
3. Mostrar disponibilidad (`website_sale_stock`): campos `is_storable`/`allow_out_of_stock_order = False`, `show_availability = True`, `available_threshold = 5`. Un producto sin existencias no debe poder comprarse.
4. Registro de clientes: en Ajustes de sitio web, activar **"Customer Account: On invitation" o "Free sign up"** según corresponda (para la demostración usar **Free sign up**). Verificar que `/web/signup` funciona sin pedir invitación.
5. Pagos simulados:
   - Activar el proveedor **Demo** (`payment.payment_provider_demo`, estado `test`).
   - Activar **Transferencia bancaria** (proveedor `transfer`, con mensaje y datos de cuenta ficticios de TechCore).
   - Ambos visibles en el checkout.
6. Facturación y portal:
   - Activar **facturación automática al confirmar el pago** (Ajustes de Ventas, `Automatic Invoice`) y la **política de facturación** sobre cantidades pedidas, de modo que cada venta web genere factura sin intervención.
   - Confirmar que el cliente ve sus pedidos y facturas en `/my` y puede descargar el PDF.
   - Verificar que la moneda es **GTQ**, el impuesto IVA 12% está aplicado y el diario de ventas está configurado (el diario de ventas aparece como "Customer Invoices").
7. CRM integrado con la tienda (cumple el objetivo "de la compra web al lead"):
   - Activar la generación de oportunidades desde el formulario de contacto web (`website_crm`).
   - Crear una **acción automatizada** (`base.automation`) sobre `sale.order` con `website_id` definido, al crearse, que cree un `crm.lead` etiquetado `Web B2C` en la etapa **Lead** vinculado al cliente y al pedido. Documentar el modelo y el disparador.
8. Mantener el diseño de la portada de la Fase 2 y verificar el menú: Inicio, Tienda, Contáctenos, Iniciar sesión.
9. Prueba de humo manual por HTTP (script `curl` o `requests`): `/`, `/shop`, `/shop/<producto>`, `/web/signup`, `/shop/cart`, `/my`. Todas deben devolver 200 sin errores 500.

### Hito A3: Infraestructura y vistas para BI

1. **Rol de solo lectura** `bi_reader` con contraseña (por ejemplo `bi_reader_techcore`), con `CONNECT` sobre `TechCore_DB`, `USAGE` sobre el esquema `public` y `SELECT` **solo sobre las vistas `v_bi_*`**. Un rol de PostgreSQL es un objeto del clúster, no de la base: el `pg_dump` de una sola base **no lo incluye**. Por eso hay que crearlo de forma idempotente desde un script de arranque (ver hito A5), no solo en la base actual.
2. Crear las **vistas SQL** con estos nombres y columnas exactos (Francisco desarrolla Power BI sobre ellas; no cambiar los nombres sin avisar). Los nombres de producto en Odoo 17 son `jsonb`: usar `COALESCE(pt.name->>'es_GT', pt.name->>'en_US')`.

| Vista | Columnas |
|---|---|
| `v_bi_ventas_detalle` | `orden`, `fecha` (date), `anio`, `mes`, `semana`, `cliente`, `segmento` (B2B o B2C o Sin segmento), `canal` (Web o Cotización), `codigo_producto`, `producto`, `categoria`, `cantidad`, `precio_unitario`, `subtotal`, `estado` |
| `v_bi_inventario` | `codigo_producto`, `producto`, `categoria`, `existencias`, `stock_minimo`, `stock_maximo`, `estado_stock` (Bajo o Normal o Sin regla), `costo`, `precio_venta`, `valor_inventario`, `cantidad_por_recibir` |
| `v_bi_top_productos` | `codigo_producto`, `producto`, `categoria`, `unidades_vendidas`, `ingresos`, `ranking` |
| `v_bi_compras` | `orden`, `fecha`, `proveedor`, `producto`, `cantidad`, `cantidad_recibida`, `subtotal`, `estado` |

   Reglas: solo órdenes de venta en estado `sale` o `done`; `fecha` sale de `sale_order.date_order`; `canal = 'Web'` cuando `sale_order.website_id IS NOT NULL`; `estado_stock = 'Bajo'` cuando `existencias <= stock_minimo`.

3. Guardar el SQL en `Proyecto/Fase3/bi/vistas_bi.sql` (idempotente con `CREATE OR REPLACE VIEW`) y aplicarlo en la VM.
4. **Ventas históricas de demostración** (`scripts/sembrar_ventas_demo.py`):
   - Crear unas 60 a 90 órdenes de venta repartidas entre semanas y meses (por ejemplo, de hace 90 días a hoy), con clientes B2B y B2C, productos variados y cantidades realistas, mezcla de canal web y cotización.
   - Confirmar la orden, validar la entrega (descuenta inventario), crear y publicar la factura y registrarla como pagada, para que **toda la cadena quede consistente**.
   - Retrasar las fechas con SQL (`UPDATE sale_order SET date_order`, `account_move.invoice_date`, `stock_move.date`) o con contexto de ORM, respetando el orden lógico.
   - Marcar las órdenes con una etiqueta o con `client_order_ref = 'DEMO-SEED'`, para poder distinguirlas, y **documentar que son datos de demostración**.
   - Mantener el inventario final positivo y realista: usar reposición automática vía compras sembradas para productos que bajen del mínimo, dejando 3 o 4 productos en estado **Bajo** a propósito (para el reporte de stock bajo).
   - Debe ser **idempotente**: si ya hay órdenes `DEMO-SEED`, no duplicar.
   - Dejar que el orden sembrado produzca al menos 8 semanas con ventas y un top 5 claramente diferenciado.

### Hito A4: Pruebas internas rápidas de Parte A

Antes de dar luz verde a Julio y Francisco, ejecutar el flujo completo una vez a mano o con script:
registro de cliente nuevo, compra de 2 productos, pago por transferencia, ver orden, factura en el portal, descuento de inventario, lead `Web B2C` en el CRM. Capturar el resultado.

### Hito A5: Que todo levante con `start.sh` en cualquier máquina (incluida Windows)

1. **Exponer PostgreSQL** en el `docker-compose.yml` solo a localhost: `"127.0.0.1:5432:5432"` en el servicio `db`. Para la VM, una variante con puerto accesible por LAN debe documentarse aparte (y no entra en el repositorio por seguridad).
2. **Crear `bi_reader` al arrancar:** añadir un script `db-init/02-crear-bi-reader.sh` que corra después de la restauración (o reutilizar `01-restore-techcore.sh`) y que cree el rol y las vistas (`vistas_bi.sql`) de forma idempotente. Verificar que funciona en un arranque limpio (`docker compose down -v` y luego `./start.sh`).
3. **Windows:** `start.sh` es Bash. Documentar y probar una de estas rutas en `README.md`:
   - Docker Desktop con **WSL2** (Ubuntu) y ejecutar `./start.sh` desde WSL; o
   - Git Bash con Docker Desktop.
   Además, crear `start.ps1` equivalente (PowerShell): `docker compose up -d`, esperar a que `pg_isready` responda, reparar el menú de Ventas y mostrar las URL. Debe producir el mismo resultado que `start.sh`.
4. Verificar la **prueba de arranque limpio** (obligatoria): contenedores de prueba en otro puerto y volúmenes nuevos, como se hizo en la Fase 2 (`test_techcore` en 8079). Criterios: HTTP 200 en `/web/login`, `/shop` con 21 productos, ventas sembradas presentes, vistas BI consultables con `bi_reader`.
5. Actualizar `README.md` con: requisitos (Docker, 6 GB de RAM libres, puertos 8069 y 5432), arranque, credenciales, cómo conectar Power BI, cómo restaurar y cómo detener.

### Hito A6: Congelar el estado final

Ejecutar **al final**, cuando Julio y Francisco hayan terminado sus pruebas en vivo (o inmediatamente antes de la entrega):

1. Regenerar `dump.sql.gz` desde la VM (`pg_dump | gzip`) y el backup `.zip` nativo (`/web/database/backup` con la master password).
2. Sincronizar `filestore/` de la VM al repositorio y viceversa (`rsync`), y ajustar permisos (`chmod -R a+rwX`).
3. Recordar las **lecciones aprendidas** (sección 10) y repetir la prueba de arranque limpio con el dump final.
4. Commit y push a `main`, avisando al grupo para que hagan `pull` (ver el procedimiento de sincronización en el README: respaldar su avance, descartar su copia local del dump y traer el oficial).

### Hito A7: Documentación y video de la Parte A

- Manual del e-commerce en `Proyecto/Fase3/docu/manual_ecommerce_jonathan.md`: catálogo, ficha de producto, registro de cliente, carrito, checkout, métodos de pago, factura y portal, y el lead automático en CRM. Cada paso con captura.
- Capturas tomadas con automatización de navegador (sección 11) o a mano, guardadas en `Proyecto/Fase3/docu/capturas/` con el prefijo `jonathan_`.
- Video 1 de la Fase 3 (3 a 4 minutos): recorrido de tienda, registro, compra, factura en el portal y lead en CRM.

---

## 6. Parte B: Business Intelligence (Francisco)

Ver [TAREAS_FRANCISCO.md](TAREAS_FRANCISCO.md). Resumen para quien integre:

- Francisco usa **Power BI Desktop en Windows** y se conecta al PostgreSQL local (puerto 5432) levantado con `start.sh`, con el usuario `bi_reader` y las vistas `v_bi_*`.
- Entrega `Proyecto/Fase3/bi/Reportes_TechCore.pbix`, manual con capturas y un video corto del tablero.
- **Depende** de los hitos A1, A3 y A5 de Jonathan.

## 7. Parte C: Pruebas, manuales y cierre (Julio)

Ver [TAREAS_JULIO.md](TAREAS_JULIO.md). Resumen para quien integre:

- Casos de prueba CP-01 a CP-08 con evidencia, matriz de trazabilidad, manual de usuario del cliente final, informe de conclusiones y escalabilidad, y presentación final.
- **Depende** de los hitos A1, A2 y A4 de Jonathan.

---

## 8. Integración final y entregable (Jonathan)

El enunciado exige para la Fase 3: informe técnico, manuales con capturas, video demostrativo en Google Drive, prototipo funcional, reportes analíticos y presentación final. Como no se conocen indicaciones adicionales del auxiliar, se arma el paquete de la misma forma que en la Fase 2 y se ajusta cuando lleguen las instrucciones.

1. **PDF consolidado** `[SOG1]ProyectoF3_G7.pdf`, generado a partir de un `Proyecto/Fase3/docu/manual_tecnico_consolidado_fase3.md` con esta estructura:
   - Portada institucional (igual a las fases anteriores) y tabla de integrantes.
   - Índice general y tabla de videos con enlaces de Google Drive (acceso público, verificado en incógnito).
   - Parte I: E-commerce (Jonathan).
   - Parte II: Pruebas end-to-end (Julio).
   - Parte III: Business Intelligence (Francisco).
   - Conclusiones y escalabilidad (Julio) y medición de logros frente a los objetivos SMART de la Fase 1.
   - Una sección de video por integrante (patrón `# VIDEO N` ya usado en la Fase 2).
2. **Prototipo funcional:** la carpeta `techcore-odoo/` lista con `start.sh` y `start.ps1`.
3. **Reportes analíticos:** el `.pbix` y capturas de los tableros (y, si se puede, PDF exportado del reporte).
4. **Presentación final:** archivo de diapositivas de Julio (PowerPoint o PDF), obligatoria en todas las fases.
5. **ZIP final** `[SOG1]ProyectoF3_G7.zip` con: el PDF, el `.pbix`, la presentación y (si el auxiliar lo pide) el prototipo o el enlace a su descarga. Confirmar el contenido exacto cuando el auxiliar dé las indicaciones.
6. Convertir Markdown a PDF con una herramienta sin dependencias exóticas (por ejemplo, `pandoc` con `wkhtmltopdf`, o el navegador en modo de impresión), verificando que las imágenes se vean con buena resolución y que los saltos de página no corten tablas.
7. Verificación de integridad: ningún enlace de imagen roto (script que recorra `![...](...)` y compruebe que el archivo existe), ningún enlace de video privado y sin emojis (búsqueda por rango Unicode).

---

## 9. Reglas de Git y estructura de archivos por persona

| Persona | Puede subir | No debe tocar |
|---|---|---|
| Jonathan | Todo lo de `techcore-odoo/`, `Proyecto/Fase3/bi/vistas_bi.sql`, `docu/manual_ecommerce_jonathan.md`, consolidado | n.a. |
| Francisco | `Proyecto/Fase3/bi/*.pbix`, `docu/manual_bi_francisco.md`, `docu/capturas/francisco_f3_*` | `dump.sql.gz`, `TechCore_DB_backup.zip`, `filestore/` |
| Julio | `docu/pruebas_e2e_julio.md`, `docu/manual_usuario_julio.md`, `docu/conclusiones_escalabilidad_julio.md`, `docu/capturas/julio_f3_*`, presentación | `dump.sql.gz`, `TechCore_DB_backup.zip`, `filestore/` |

Prefijos de capturas: `jonathan_f3_NN_...`, `julio_f3_NN_...`, `francisco_f3_NN_...` para no pisar los archivos de la Fase 2.

Flujo de sincronización para cada integrante: hacer `git pull` antes de empezar; trabajar sobre una instancia local levantada con `start.sh`; **no** subir el dump ni el filestore; subir solo sus propios archivos.

---

## 10. Lecciones aprendidas y trampas conocidas (leer antes de tocar la base)

1. **Filestore desincronizado** produce `Error 500` en `web.assets_web.min.css` (`FileNotFoundError` en `/var/lib/odoo/filestore/TechCore_DB/..`). Solución: `rsync` del `filestore/` del repositorio a `/home/jona/techcore-odoo/filestore/`, `chmod -R a+rwX`, borrar las líneas de assets (`DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';`) y reiniciar `techcore_odoo_web`.
2. **Vistas QWeb en memoria:** tras modificar `ir.ui.view` (por ORM o SQL) hay que reiniciar `techcore_odoo_web`.
3. **Entidades HTML en QWeb:** usar entidades numéricas (`&#8594;`) o SVG; las entidades con nombre (`&rarr;`) rompen el parser.
4. **Menú de Ventas archivado:** el dump original se creó sin `sale`; `start.sh` desarchiva el menú raíz en cada arranque. Mantener ese arreglo.
5. **Contraseñas distintas:** la contraseña real del usuario `admin@techcore.gt` es `1234`; la master password del gestor es `techcore_master_pwd`; PostgreSQL usa `techcore_secure_pwd`. El archivo `contexto.md` menciona otra master password, que está desactualizada.
6. **Conflictos de Git con binarios:** `dump.sql.gz` y `.zip` no se fusionan. Para integrar remoto y local, `git merge -X ours origin/main` favoreciendo la versión del dueño del dump y luego regenerar el dump a partir de la VM.
7. **Reloj de la VM:** las fechas de los logs de la VM aparecen distintas a la fecha real del equipo; al sembrar datos históricos, calcular las fechas con `CURRENT_DATE` de PostgreSQL, no con la fecha del Mac.
8. **Idempotencia:** todos los scripts nuevos deben poder ejecutarse varias veces sin duplicar datos.
9. **Capturas con navegador automatizado:** funcionan con `puppeteer-core` y Chrome en `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (instalar en una carpeta temporal fuera del repositorio). Para Odoo 17, esperar 3 a 4 segundos tras cada navegación; las acciones se identifican por `action=<id>` o por `menu_id`. Algunas URL con `model=` y `view_type=` directas fallan y muestran "Odoo Client Error"; preferir `#action=<id>&menu_id=<id>`.

---

## 11. Plan de ejecución por olas (sin fechas)

| Ola | Qué ocurre | Responsable | Desbloquea |
|---|---|---|---|
| 1 | Hito A1: verificar datos, cargar 60 precios y extras, recrear reglas de reposición | Jonathan | Todos |
| 2 | Hito A2 (e-commerce) en paralelo con la preparación de Francisco (Docker Desktop, Power BI, esqueleto) y Julio (casos de prueba, borrador del manual) | Todos | |
| 3 | Hito A3 (rol `bi_reader`, vistas y ventas sembradas) y A5 (arranque limpio y Windows) | Jonathan | Parte B completa |
| 4 | Hito A4 y luego pruebas E2E (Julio) y tableros (Francisco) | Julio y Francisco | |
| 5 | Redacción de documentos, conclusiones y videos | Todos | |
| 6 | Hito A6 (congelar dump) y consolidación final (PDF, ZIP) con revisión cruzada | Jonathan | Entrega |

---

## 12. Criterios de aceptación globales

- [ ] `./start.sh` (y `start.ps1` en Windows) levanta Odoo con 21 productos publicados, 6 clientes, 4 proveedores, ventas sembradas y vistas BI, partiendo de volúmenes vacíos.
- [ ] Un cliente nuevo se registra, compra, paga por transferencia o con Demo, y ve su factura en `/my`.
- [ ] La venta descuenta inventario y crea la oportunidad `Web B2C` en el CRM.
- [ ] `bi_reader` consulta las cuatro vistas desde Power BI en Windows.
- [ ] El reporte de inventario muestra existencias y stock bajo; el de ventas muestra evolución diaria, semanal y mensual y el top 5.
- [ ] Los ocho casos de prueba están documentados con capturas y resultado real.
- [ ] El PDF consolidado no tiene imágenes rotas, emojis ni enlaces privados.
- [ ] El ZIP contiene lo que el auxiliar pida (a confirmar).

---

## 13. Pendientes que dependen de Jonathan

1. Entregar el **desglose de la rúbrica** de la Fase 3 y las **indicaciones del auxiliar** cuando existan (formato de entrega, plataforma, contenido del ZIP).
2. Confirmar que la evaluación técnica se hará en la **máquina Windows de Francisco** y, si no, en cuál.
3. Autorizar la regeneración final del dump (hito A6) cuando el grupo termine.
