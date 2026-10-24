# TechCore Solutions Guatemala - Sistema ERP/CRM y Fases del Proyecto

Este directorio contiene tanto el entorno de despliegue del sistema ERP/CRM como las carpetas de trabajo y documentación de cada fase académica.

## Estructura General

```text
Proyecto/
├── techcore-odoo/      # Motor y servidor del ERP/CRM compartido por todo el proyecto
│   ├── docker-compose.yml   # Definicion de contenedores (Odoo 17 y PostgreSQL 15)
│   ├── start.sh             # Script de arranque para Linux y macOS
│   ├── start.ps1            # Script de arranque para Windows PowerShell
│   ├── db-init/             # Dump SQL (dump.sql.gz) y scripts de inicializacion
│   ├── backup/              # Respaldo nativo de Odoo (TechCore_DB_backup.zip)
│   ├── filestore/           # Almacen de archivos e imagenes de productos
│   └── scripts/             # Scripts de carga, siembra y pruebas
│
├── Fase2/              # Entregables y documentacion historica de la Fase 2
│   ├── docu/                # Manuales tecnicos consolidados e individuales
│   ├── plantillas-correo/   # Plantillas HTML de email marketing
│   └── enunciado.md         # Enunciado y requerimientos
│
└── Fase3/              # Entregables, planeacion y reportes de la Fase 3
    ├── PLAN_FASE3_COMPLETO.md  # Plan maestro consolidado de la fase final
    ├── TAREAS_JULIO.md         # Guia de ejecucion para Julio (MRP y pruebas)
    ├── TAREAS_FRANCISCO.md     # Guia de ejecucion para Francisco (Power BI)
    ├── bi/                     # Vistas analiticas SQL y archivo Reportes_TechCore.pbix
    └── docu/                   # Manual tecnico consolidado, manuales individuales y capturas
```

## Guia Rapida de Despliegue

Para levantar el sistema Odoo y la base de datos analitica:

1. Entrar al directorio del servidor:
   ```bash
   cd Proyecto/techcore-odoo
   ```

2. Ejecutar el script de arranque segun tu sistema operativo:
   - **En Linux / macOS:**
     ```bash
     ./start.sh
     ```
   - **En Windows (PowerShell como Administrador):**
     ```powershell
     .\start.ps1
     ```

3. Acceder al sistema:
   - **Odoo Web:** `http://localhost:8069` (Usuario: `admin@techcore.gt`, Contrasena: `1234`)
   - **Tienda E-Commerce:** `http://localhost:8069/shop`
   - **PostgreSQL / Power BI:** Host `localhost:5432`, Base `TechCore_DB`, Usuario `bi_reader`, Contrasena `bi_reader_techcore`

---

## Videos Demostrativos de Fase 3

| Video | Titulo y Alcance Tecnico | Integrante | Carnet | Enlace de Google Drive |
|---|---|---|---|---|
| **VIDEO 1** | **E-Commerce, Portal Web y Trazabilidad CRM/ERP** | Jonathan Jeronimo | 202300353 | [Ver Video 1 en Google Drive](https://drive.google.com/file/d/1Aic7k_oGkkwmFqVYoWFF8siOEHab441A/view?usp=sharing) |
| **VIDEO 2** | **Reportes de Inventario y Ventas en Power BI** | Francisco Castillo | 202300653 | [Ver Video 2 en Google Drive](https://drive.google.com/file/d/1drsu8TdcWIfKtujYJ5SY-BxojB4REDNY/view?usp=sharing) |
| **VIDEO 3** | **Pruebas End-to-End, Trazabilidad y Reposicion** | Julio Herrera | 202300850 | [Ver Video 3 en Google Drive](https://drive.google.com/drive/folders/1KkOk_ql0KaoQXyrvk9ObFsEnRwvmSKz1?usp=sharing) |

---

## Documento Principal de Entrega de Fase 3

El documento maestro integral que unifica todo el trabajo de los tres integrantes se encuentra en:
- **[Manual Tecnico Consolidado de Fase 3](file:///Users/jona/Desktop/USAC/4to_Anio/8vo%20Semestre/GERENCIALES/LAB/Practicas/P1/SOG1_2026S2_LOS4BABYS/Proyecto/Fase3/docu/manual_tecnico_consolidado_fase3.md)** (`Proyecto/Fase3/docu/manual_tecnico_consolidado_fase3.md`)
