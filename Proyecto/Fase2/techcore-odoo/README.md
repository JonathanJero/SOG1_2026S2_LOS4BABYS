# TechCore Solutions Guatemala - Entorno Odoo 17 ERP/CRM (Fase 2)

Este directorio contiene todo el entorno de trabajo de **Odoo 17.0** y **PostgreSQL 15** empaquetado y listo para levantarse con un solo comando. Incluye la base de datos `TechCore_DB` precargada con todas las configuraciones realizadas hasta el momento (Pipeline Kanban de CRM con sus etapas, clientes/leads, campañas de email marketing, portada institucional del sitio web y filestore de adjuntos e imágenes).

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
