# Tareas de Francisco (Gerardo): Reportes de Business Intelligence en Power BI

**Fase 3, Parte B.** Eres el único del grupo con Windows, por lo que tú desarrollas los reportes de Power BI. La evaluación técnica probablemente se haga en tu máquina, así que además verificas que el proyecto levanta completo.

Contexto general y reglas: [PLAN_FASE3_COMPLETO.md](PLAN_FASE3_COMPLETO.md). Lee las secciones 0, 5 (hitos A3 y A5) y 9.

> Regla del proyecto: sin emojis en ningún documento, y español con tildes y eñes.

---

## 1. Qué debes entregar

| Entregable | Ruta en el repositorio |
|---|---|
| Reporte de Power BI | `Proyecto/Fase3/bi/Reportes_TechCore.pbix` |
| Manual de BI con capturas | `Proyecto/Fase3/docu/manual_bi_francisco.md` |
| Capturas | `Proyecto/Fase3/docu/capturas/francisco_f3_NN_nombre.png` |
| Video corto del tablero (2 a 3 minutos) | Google Drive, enlace público; pegarlo en el manual |

**Qué pide el enunciado:**
- **Reporte de inventario:** existencias y stock bajo.
- **Reporte de ventas:** evolución diaria, semanal y mensual, y top 5 de productos.
- Hecho en Power BI (o Looker Studio; el grupo eligió Power BI).

---

## 2. Qué necesitas de Jonathan antes de empezar

Jonathan prepara los datos y las vistas. Hasta que él avise **"vistas BI listas"**, puedes avanzar con la instalación y con el esqueleto del reporte. Lo que él entrega:

- Un Odoo que levanta con `start.sh` / `start.ps1`, con 21 productos, ventas históricas y clientes.
- PostgreSQL expuesto en `localhost:5432`.
- Un usuario de solo lectura:

| Dato | Valor |
|---|---|
| Servidor | `localhost` |
| Puerto | `5432` |
| Base de datos | `TechCore_DB` |
| Usuario | `bi_reader` |
| Contraseña | `bi_reader_techcore` (Jonathan confirmará si cambia) |

- Cuatro vistas SQL (los nombres y columnas son fijos):

| Vista | Columnas |
|---|---|
| `v_bi_ventas_detalle` | `orden`, `fecha`, `anio`, `mes`, `semana`, `cliente`, `segmento`, `canal`, `codigo_producto`, `producto`, `categoria`, `cantidad`, `precio_unitario`, `subtotal`, `estado` |
| `v_bi_inventario` | `codigo_producto`, `producto`, `categoria`, `existencias`, `stock_minimo`, `stock_maximo`, `estado_stock`, `costo`, `precio_venta`, `valor_inventario`, `cantidad_por_recibir` |
| `v_bi_top_productos` | `codigo_producto`, `producto`, `categoria`, `unidades_vendidas`, `ingresos`, `ranking` |
| `v_bi_compras` | `orden`, `fecha`, `proveedor`, `producto`, `cantidad`, `cantidad_recibida`, `subtotal`, `estado` |

Las ventas sembradas por Jonathan son **datos de demostración** y llevan la referencia `DEMO-SEED`. Menciónalo en tu manual.

---

## 3. Preparación de tu máquina (puedes hacerlo ya)

1. **Docker Desktop para Windows** con WSL2 activado. Reserva al menos 6 GB de RAM para Docker.
2. **Git** y clonar el repositorio:
   ```powershell
   git clone https://github.com/JonathanJero/SOG1_2026S2_LOS4BABYS.git
   cd SOG1_2026S2_LOS4BABYS\Proyecto\techcore-odoo
   ```
3. **Power BI Desktop** (Microsoft Store o descarga oficial).
4. Levantar el proyecto. Usa una de estas dos opciones, la que funcione mejor en tu máquina:
   - **PowerShell:** `./start.ps1` (Jonathan lo creará; si todavía no existe, usa la opción siguiente).
   - **WSL2 (Ubuntu) o Git Bash:** `chmod +x start.sh` y luego `./start.sh`.
5. Comprobar que abre `http://localhost:8069` con `admin@techcore.gt` y la contraseña `1234`, y que `http://localhost:8069/shop` muestra productos.
6. **Si algo falla al levantar, avisa a Jonathan con el mensaje de error completo.** Es parte de lo que se evalúa.

---

## 4. Conexión de Power BI a PostgreSQL

1. En Power BI Desktop: **Obtener datos, Base de datos PostgreSQL**.
2. Servidor `localhost:5432`, base de datos `TechCore_DB`, modo **Importar**.
3. Credenciales de base de datos: usuario `bi_reader` y su contraseña.
4. Seleccionar solo las cuatro vistas `v_bi_*` y **Cargar**.
5. Si el conector pide `Npgsql` (versiones antiguas), instalarlo desde el instalador de Npgsql marcando "Npgsql GAC Installation", y reiniciar Power BI.
6. **Plan B si no conecta:** pedir a Jonathan un CSV por vista (él exporta con `COPY ... TO`) y cargarlos con **Obtener datos, Texto o CSV**. Menciónalo en el manual como método alterno.

---

## 5. Reporte de Inventario (página 1 del `.pbix`)

Nombre de la página: `Inventario`.

| Elemento visual | Configuración |
|---|---|
| Tarjetas (KPI) | Total de existencias, valor total del inventario, cantidad de productos en estado Bajo |
| Gráfico de barras | Existencias por producto (de `v_bi_inventario`), ordenado de menor a mayor |
| Gráfico de columnas | Existencias por categoría |
| Tabla de alertas | Productos con `estado_stock = "Bajo"`: código, producto, existencias, stock mínimo, cantidad por recibir. Formato condicional en rojo |
| Medidor (gauge) | Existencias frente a stock mínimo del producto seleccionado |
| Segmentadores | Categoría y Estado de stock |

**Medidas DAX sugeridas:**
```dax
Total Existencias = SUM ( v_bi_inventario[existencias] )
Valor Inventario = SUM ( v_bi_inventario[valor_inventario] )
Productos en Stock Bajo =
CALCULATE ( DISTINCTCOUNT ( v_bi_inventario[codigo_producto] ), v_bi_inventario[estado_stock] = "Bajo" )
```

---

## 6. Reporte de Ventas (página 2 del `.pbix`)

Nombre de la página: `Ventas`.

| Elemento visual | Configuración |
|---|---|
| Tarjetas (KPI) | Ventas totales (Q), número de órdenes, ticket promedio, unidades vendidas |
| Gráfico de líneas, nivel **día** | `fecha` en el eje, suma de `subtotal` |
| Gráfico de líneas, nivel **semana** | `anio` y `semana` en el eje (jerarquía) |
| Gráfico de columnas, nivel **mes** | `anio` y `mes` en el eje |
| **Top 5 de productos** | Gráfico de barras con `v_bi_top_productos`, filtro de los 5 primeros por `ranking <= 5`, valor `unidades_vendidas` (y una segunda visual por `ingresos`) |
| Gráfico circular o de anillo | Ventas por categoría |
| Gráfico de barras | Ventas por canal (Web frente a Cotización) y por segmento (B2B, B2C) |
| Segmentadores | Rango de fechas, canal, segmento |

Para la evolución diaria, semanal y mensual, usa **tres visuales** o un solo visual con un botón o marcador (bookmark) que cambie entre día, semana y mes. Ambas opciones cumplen; lo importante es que las tres granularidades se vean.

**Medidas DAX sugeridas:**
```dax
Ventas Totales = SUM ( v_bi_ventas_detalle[subtotal] )
Ordenes = DISTINCTCOUNT ( v_bi_ventas_detalle[orden] )
Ticket Promedio = DIVIDE ( [Ventas Totales], [Ordenes] )
Unidades Vendidas = SUM ( v_bi_ventas_detalle[cantidad] )
```

Formato: moneda en quetzales (`Q`), título claro en cada visual, paleta de color de marca TechCore (azul oscuro y verde), sin exceso de elementos.

---

## 7. Página opcional de Compras (si hay tiempo)

Usa `v_bi_compras`: gasto por proveedor, órdenes pendientes de recepción y comparación de costo contra precio de venta. No es obligatoria.

---

## 8. Validación de los números (obligatoria)

Antes de capturar, verifica que Power BI coincide con Odoo:

1. En Odoo, **Ventas, Reportes** (o Facturación) y compara el total de ventas y el número de órdenes con tus tarjetas.
2. En Odoo, **Inventario, Reportes, Stock** y compara las existencias por producto.
3. Documenta las cifras en el manual en una tabla "Power BI frente a Odoo" (coinciden o difieren y por qué).

---

## 9. Manual de BI (`manual_bi_francisco.md`)

Usa la misma estructura de tus manuales anteriores:

1. Portada con tus datos (nombre, carnet 202300653, rol).
2. Introducción y alcance (puntos del enunciado: reportes de inventario y de ventas).
3. Requisitos y preparación (Docker, Power BI, conexión).
4. Conexión paso a paso, con captura de la ventana de conexión (oculta o cubre la contraseña).
5. Modelo de datos: las cuatro vistas y su propósito.
6. Reporte de Inventario: captura de la página completa y una explicación de cada visual.
7. Reporte de Ventas: captura de la página completa, de la evolución diaria, semanal y mensual, y del top 5.
8. Validación de cifras (tabla de la sección 8).
9. Problemas frecuentes y solución (conexión, Npgsql, contraseña, vistas vacías).
10. Conclusiones: qué decisiones permite tomar cada reporte (por ejemplo, reponer productos en Bajo, empujar los productos del top 5, reforzar el canal web).
11. Sección de video con el enlace de Drive (patrón `# VIDEO 2 - ...` usado en la Fase 2).

Cada paso del manual lleva su captura, con prefijo `francisco_f3_`. Marca con recuadro rojo lo que importa.

---

## 10. Video (2 a 3 minutos)

1. Presentación (10 segundos): nombre, carnet y objetivo.
2. Mostrar `start.sh` o `start.ps1` levantando y Odoo abierto (15 segundos).
3. Mostrar la conexión de Power BI y el modelo de datos (20 segundos).
4. Recorrer la página de Inventario: KPIs, existencias, alertas de stock bajo (40 segundos).
5. Recorrer la página de Ventas: evolución diaria, semanal y mensual, top 5 y filtros (60 segundos).
6. Cierre: qué decisiones habilitan los reportes (10 segundos).

Subir a Drive con acceso **"Cualquier persona con el enlace puede ver"** y probar el enlace en una ventana de incógnito.

---

## 11. Reglas de Git para ti

- Sube solo: `Proyecto/Fase3/bi/Reportes_TechCore.pbix`, `Proyecto/Fase3/docu/manual_bi_francisco.md` y `Proyecto/Fase3/docu/capturas/francisco_f3_*`.
- **No subas ni modifiques** `dump.sql.gz`, `TechCore_DB_backup.zip` ni `filestore/`. Si al levantar tu entorno Git los marca como modificados, descártalos antes de subir:
  ```powershell
  git checkout -- Proyecto/techcore-odoo/db-init/dump.sql.gz
  git checkout -- Proyecto/techcore-odoo/backup/TechCore_DB_backup.zip
  ```
- Antes de empezar cada sesión: `git pull origin main`.
- Mensajes de commit descriptivos y sin emojis, por ejemplo: `feat(bi): reportes de inventario y ventas en Power BI`.

---

## 12. Lista de verificación final

- [ ] El proyecto levanta en tu máquina con `start.ps1` o `start.sh` desde cero.
- [ ] Power BI se conecta con `bi_reader` y carga las cuatro vistas.
- [ ] La página `Inventario` muestra existencias y alertas de stock bajo.
- [ ] La página `Ventas` muestra evolución diaria, semanal y mensual y el top 5.
- [ ] Las cifras coinciden con Odoo (tabla de validación).
- [ ] `.pbix` guardado en `Proyecto/Fase3/bi/`.
- [ ] Manual completo con capturas y sin emojis.
- [ ] Video subido a Drive con enlace público y pegado en el manual.
