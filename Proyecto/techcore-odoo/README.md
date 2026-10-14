# TechCore Solutions Guatemala - Entorno Odoo 17 ERP/CRM/BI (Fase 3)

Este directorio contiene todo el entorno de trabajo integrado de **Odoo 17.0 Community**, **PostgreSQL 15** y **Vistas Analíticas para Power BI**, empaquetado y listo para levantarse con un solo comando tanto en **macOS/Linux** como en **Windows**.

---

## 1. Requisitos Previos

- **Docker** y **Docker Compose** (Docker Desktop en Windows y Mac, o Docker Engine en Linux).
- Mínimo **6 GB de memoria RAM libre** recomendados para Docker.
- Puertos libres en el equipo anfitrión:
  - `8069`: Interfaz web de Odoo 17 y portal de clientes.
  - `5432`: Conexión de base de datos PostgreSQL para Microsoft Power BI Desktop.

---

## 2. Puesta en Marcha (1 Solo Comando)

### En macOS y Linux:
Abre una terminal en esta carpeta y ejecuta:
```bash
./start.sh
```

### En Windows (PowerShell):
Abre PowerShell en esta carpeta y ejecuta:
```powershell
.\start.ps1
```
*(Alternativamente en Windows: ejecutar `./start.sh` desde Git Bash o Ubuntu sobre WSL2).*

Ambos scripts levantan los contenedores, auto-restauran la base `TechCore_DB` si es el primer arranque, aplican las vistas analíticas de Business Intelligence y verifican la disponibilidad de la aplicación de Ventas.

---

## 3. Credenciales y Enlaces de Acceso

| Servicio | Parámetro | Valor |
|---|---|---|
| **Odoo Web / E-Commerce** | URL Principal | [http://localhost:8069](http://localhost:8069) |
| **Tienda en Línea** | Catálogo E-Commerce | [http://localhost:8069/shop](http://localhost:8069/shop) |
| **Portal de Cliente** | Mis Pedidos / Facturas | [http://localhost:8069/my](http://localhost:8069/my) |
| **Base de Datos ERP** | Nombre de Base de Datos | `TechCore_DB` |
| **Usuario Administrador** | Correo / Login | `admin@techcore.gt` |
| **Contraseña Administrador** | Contraseña | `1234` |
| **Database Manager** | Master Password | `techcore_master_pwd` |

---

## 4. Conexión de Microsoft Power BI Desktop (Business Intelligence)

Para conectar Power BI Desktop al entorno analítico local:

1. Abrir **Power BI Desktop**.
2. Seleccionar **Obtener datos (Get Data) → Base de datos PostgreSQL**.
3. Completar los parámetros de conexión:
   - **Servidor:** `localhost:5432`
   - **Base de datos:** `TechCore_DB`
   - **Modo de conectividad:** `Importar` (o `DirectQuery` según necesidad)
4. En la pantalla de autenticación de base de datos:
   - **Tipo de autenticación:** `Base de datos` (Database)
   - **Nombre de usuario:** `bi_reader`
   - **Contraseña:** `bi_reader_techcore`
5. En el navegador de tablas, seleccionar las **4 vistas analíticas**:
   - `v_bi_ventas_detalle`: Detalle de transacciones históricas con segmentación B2B/B2C, temporalidad y canales.
   - `v_bi_inventario`: Existencias en almacén, umbrales de reorden, valoración monetaria y alertas de stock bajo.
   - `v_bi_top_productos`: Ranking de productos más vendidos ordenados por ingresos y unidades.
   - `v_bi_compras`: Registro de compras a proveedores y recepciones de mercancía.

---

## 5. Módulos y Flujos Operativos Implementados (Fase 3)

| Componente | Estado | Detalle |
|---|---|---|
| **E-Commerce Catálogo** | 21 Productos Publicados | Procesadores, RAM, SSD, Discos, Switches, Servidores, Tarjetas Madre y Periféricos con imágenes y fichas técnicas. |
| **Disponibilidad Web** | Control de Stock Activo | `website_sale_stock` configurado para impedir compras sin inventario y alertar umbrales mínimos. |
| **Registro de Clientes** | Libre (/web/signup) | Registro B2C directo con acceso a portal. |
| **Métodos de Pago** | Demo y Transferencia | Proveedor Demo (simulación) y Transferencia Bancaria configurados en GTQ. |
| **Facturación Automática** | GTQ con 12% IVA | Factura generada y emitida automáticamente al confirmar la venta. |
| **Integración CRM** | Automatizada | Al crearse un pedido web, se genera automáticamente una oportunidad en CRM con etiqueta `Web B2C` en etapa `Lead`. |
| **Ventas Históricas** | 75 Órdenes Sembradas | Distribuidas en 13 semanas para permitir análisis temporal en Power BI. |
| **Compras Históricas** | 16 Órdenes Recibidas | Proveedores Ingram Micro, Intcomex, PC Mayorista y Distribuidora Tecno. |

---

## 6. Comandos Útiles

- **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f
  ```
- **Detener el entorno:**
  ```bash
  docker compose down
  ```
- **Reiniciar servicios:**
  ```bash
  docker compose restart
  ```
- **Reinicio limpio (borra volúmenes y re-restaura desde cero):**
  ```bash
  docker compose down -v
  ./start.sh
  ```
  *(En Windows: `docker compose down -v` y luego `.\start.ps1`)*
