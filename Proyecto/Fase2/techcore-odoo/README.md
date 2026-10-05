# TechCore Solutions Guatemala - Entorno Odoo 17 ERP/CRM (Fase 2)

Este directorio contiene todo el entorno de trabajo de **Odoo 17.0** y **PostgreSQL 15** empaquetado y listo para levantarse con un solo comando.

### Estado de la base de datos `TechCore_DB`

La base se entrega en **estado limpio de datos maestros**, con la configuración completa y lista para la demostración de la Fase 2:

**Configurado (listo para demostrar):**

| Módulo | Detalle |
|---|---|
| Inventario | Almacén `WH/Stock` operativo, con rutas de aprovisionamiento |
| Compras | Ciclo completo RFQ → Alternatives → OC → Recepción |
| Requisiciones | `purchase_requisition_stock` instalado (Blanket Orders) |
| Ventas | Cotizaciones y pedidos con condiciones de crédito |
| CRM | Pipeline Kanban de 4 etapas + 5 oportunidades |
| Email Marketing | 2 plantillas propias + 3 campañas segmentadas |
| Sitio Web | Portal de cliente e integración con el ERP |

**Vacío a propósito (se carga en la demostración):**

| Dato | Estado | Por qué |
|---|---|---|
| Productos | 0 activos | El punto 2.1 de la rúbrica exige demostrar la carga masiva y manual **en vivo**. Con 30 puntos en juego, no puede entregarse precargada. |
| Clientes | 0 | Ídem |
| Proveedores | 0 | Ídem |
| Precios de proveedor | 0 | Se importan después de que existan productos y proveedores |
| Inventario físico | 0 | Se carga después de que existan los productos |
| Órdenes de compra | 0 | Se demuestran en vivo |
| Pedidos de venta | 0 | Se demuestran en vivo |

### Archivos de carga masiva

Los archivos `.xlsx` están en esta carpeta y son los que Julio carga durante la demostración:

| Archivo | Contenido | Registros |
|---|---|---|
| `1_Productos_Odoo.xlsx` | Productos de hardware | 20 |
| `2_Clientes_Odoo.xlsx` | Clientes B2B y B2C | 5 |
| `3_Proveedores_Odoo.xlsx` | Proveedores | 3 |
| `4_Inventario_Fisico_Odoo.xlsx` | Existencias iniciales | 20 |
| `5_Precios_Proveedores_Odoo.xlsx` | Precios de proveedor por producto | 60 |

> **`5_Precios_Proveedores_Odoo.xlsx` es obligatorio.** Los cuatro primeros archivos crean los registros, pero ninguno crea las líneas de precio de proveedor (`product.supplierinfo`). Sin ese quinto archivo, las reglas de reposición fallan con *"There is no matching vendor price to generate the purchase order for product [...]"* y las RFQ alternativas muestran el mismo precio para todos los proveedores.

**Orden de importación:** productos → clientes → proveedores → inventario físico → precios de proveedor. Los precios van al final porque necesitan que ya existan los productos (columna `product_id/default_code`) y los proveedores (columna `partner_id`).

> **Orden de la demostración en la evaluación:**
> 1. Julio importa los cinco archivos y crea un registro manual de producto, cliente y proveedor desde la interfaz.
> 2. Francisco configura puntos de reorden, ejecuta el ciclo de compras con comparación multi-proveedor y genera la cotización B2B.
> 3. Jonathan muestra el pipeline CRM y el envío de la campaña segmentada.

Los datos de esta demostración quedaron documentados con evidencia gráfica en los manuales técnicos de `Proyecto/Fase2/docu/` y en el video demostrativo.

---

## Requisitos Previos

- Tener instalado **Docker** y **Docker Compose** (Docker Desktop en Windows/Mac o docker-ce en Linux).
- Tener libre el puerto `8069`.

---

## Método 1: Despliegue Automático (Recomendado - 1 Solo Comando)

Este método levanta los contenedores, restaura la base de datos `TechCore_DB` y monta el filestore de forma automática.

1. Abre tu terminal en esta carpeta:
   ```bash
   cd Proyecto/Fase2/techcore-odoo
   ```

2. Ejecuta el script de inicio:
   ```bash
   ./start.sh
   ```
   *(O si prefieres usar Docker Compose directamente: `docker compose up -d`)*

3. Espera unos segundos a que la base de datos se inicialice. Cuando termine, abre tu navegador web:
   **URL:** [http://localhost:8069](http://localhost:8069)

---

## Credenciales de Acceso

| Parámetro | Valor |
| --- | --- |
| **URL del Sistema** | `http://localhost:8069` |
| **Base de Datos** | `TechCore_DB` |
| **Usuario Administrador** | `admin@techcore.gt` |
| **Contraseña Administrador** | `1234` |
| **Master Password (Database Manager)** | `techcore_master_pwd` |

---

## Contenido del Entorno

- **`docker-compose.yml`**: Orquestación de servicios `web` (Odoo 17.0) y `db` (Postgres 15) con comprobación de salud (*healthcheck*).
- **`config/odoo.conf`**: Configuración de Odoo preconfigurada para conectar automáticamente a `TechCore_DB`.
- **`db-init/`**:
  - `01-restore-techcore.sh`: Script que crea la base de datos y restaura el dump automáticamente en el primer arranque.
  - `dump.sql.gz`: Volcado binario comprimido de la base de datos `TechCore_DB`.
- **`filestore/TechCore_DB/`**: Almacén de archivos multimedia, logos corporativos, banners de correo y adjuntos.
- **`backup/TechCore_DB_backup.zip`**: Respaldo nativo de Odoo (ZIP) generado desde el administrador de base de datos oficial.
- **`addons/`**: Directorio para módulos adicionales si se requieren en fases posteriores.

---

## Método 2: Restauración Manual por Interfaz Web (Alternativa)

Si por alguna razón deseas restaurar la base de datos de manera manual a través de la interfaz web de Odoo:

1. Levanta los contenedores sin la restauración automática (o déjalos corriendo con `docker compose up -d`).
2. Ingresa en tu navegador a:
   [http://localhost:8069/web/database/manager](http://localhost:8069/web/database/manager)
3. Haz clic en el botón **Restore Database** (Restaurar Base de Datos).
4. Completa los campos:
   - **Master Password:** `techcore_master_pwd`
   - **File (Archivo):** Selecciona el archivo `backup/TechCore_DB_backup.zip`.
   - **Database Name:** `TechCore_DB`
5. Haz clic en **Continue** y espera a que finalice la carga.

---

## Comandos de Mantenimiento

- **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f
  ```
- **Detener el entorno (manteniendo los datos):**
  ```bash
  docker compose down
  ```
- **Reiniciar servicios:**
  ```bash
  docker compose restart
  ```
- **Reiniciar desde cero (borrar datos y volver a auto-restaurar):**
  ```bash
  docker compose down -v
  ./start.sh
  ```
