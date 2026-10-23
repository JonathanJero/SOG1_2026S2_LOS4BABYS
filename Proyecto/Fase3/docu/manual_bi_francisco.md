# Manual Técnico y Funcional: Reportes de Inventario y Ventas en Power BI

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería – Escuela de Ciencias y Sistemas**  
**Sistemas Organizacionales y Gerenciales 1 – Sección A**  
**Segundo Semestre 2026**  
**Grupo No. 7 – TechCore Solutions Guatemala**

**Responsable:** Francisco Gerardo Castillo Sagastume  
**Carnet:** 202300653  
**Rol:** Business Intelligence y Reportes en Power BI (Parte B, Fase 3)  
**Fecha:** 22 de octubre de 2026

---

## Contenido

- Resumen ejecutivo
- 1. Introducción y alcance
- 2. Requisitos y preparación del entorno
- 3. Conexión de Power BI a PostgreSQL
- 4. Modelo de datos
- 5. Reporte de Inventario
- 6. Reporte de Ventas
- 7. Validación de cifras
- 8. Problemas frecuentes y solución
- 9. Conclusiones y decisiones de negocio
- 10. Lista de verificación
- VIDEO 2 - Reportes de Inventario y Ventas en Power BI
- Anexos

---

## Resumen ejecutivo

El presente manual documenta la construcción, el funcionamiento y la validación de los tableros de Business Intelligence desarrollados en **Power BI Desktop** para **TechCore Solutions Guatemala**, como Parte B de la Fase 3. El reporte se alimenta de las cuatro vistas analíticas `v_bi_*` publicadas en PostgreSQL y se compone de dos páginas: **Inventario** y **Ventas**.

Las cifras que se presentan corresponden al corte del **22 de octubre de 2026**, con ventas registradas entre el **13 de julio y el 6 de octubre de 2026**. Los datos de ventas fueron sembrados por Jonathan con la referencia `DEMO-SEED` y tienen fines de demostración académica.

| Indicador | Valor |
|---|---|
| Ventas netas (sin IVA) | Q 62,946.36 |
| IVA (12 %) | Q 7,553.64 |
| Total facturado con IVA | Q 70,500.00 |
| Órdenes de venta | 77 |
| Unidades vendidas | 221 |
| Ticket promedio | Q 817.49 |
| Productos en catálogo | 21 |
| Existencias totales | 1,219 unidades |
| Valor del inventario | Q 242,960.00 |
| Productos en stock bajo | 4 |
| Productos sin regla de reposición | 17 |
| Periodo de ventas | 13/07/2026 al 06/10/2026 |

Los hallazgos principales son los siguientes:

- El canal **Web** concentra el **67.79 %** de las ventas netas (Q 42,669.58), mientras que **Cotización** representa el **32.21 %** (Q 20,276.78).
- El segmento **B2C** aporta el **49.22 %** de las ventas (Q 30,982.11) y el **B2B** el **50.78 %** (Q 31,964.25).
- El producto con más ingresos es el **Intel Core i9-13900K** (Q 9,285.72), aunque el de más unidades vendidas es el **Samsung 990 PRO 2TB NVMe** (36 unidades).
- Existen **4 productos en stock bajo** (tres servidores y un switch), con **14 unidades** y un valor de **Q 31,200.00**. Ninguno tiene mercancía en tránsito (`cantidad_por_recibir = 0`).
- **17 productos no tienen regla de reposición** (`estado_stock = "Sin regla"`), por lo que la alerta de stock bajo todavía no los cubre.
- La tarjeta **Ventas Totales** muestra el subtotal sin IVA (Q 62,946.36); el total con IVA es Q 70,500.00. Esta diferencia se explica en la sección de validación.

---

## 1. Introducción y alcance

### 1.1 Objetivo general

Transformar las vistas analíticas preparadas en PostgreSQL en dos tableros interactivos de Power BI que permitan responder, con evidencia numérica, las siguientes preguntas de negocio:

- ¿Cuántas existencias hay, cuánto vale el inventario y qué productos están por debajo de su mínimo?
- ¿Cómo evolucionan las ventas por día, por semana y por mes?
- ¿Cuáles son los productos más vendidos por unidades y por ingresos?
- ¿Qué canal, segmento y categoría explican mejor las ventas?
- ¿Las cifras del tablero coinciden con Odoo y con las vistas SQL?

### 1.2 Alcance

El alcance de la Parte B comprende:

1. La conexión de Power BI Desktop a la base `TechCore_DB` con el usuario de solo lectura `bi_reader`.
2. La carga de las cuatro vistas `v_bi_ventas_detalle`, `v_bi_inventario`, `v_bi_top_productos` y `v_bi_compras`.
3. La construcción del modelo en estrella con dimensiones de producto, cliente, canal, proveedor y fecha.
4. La página **Inventario**, con tarjetas, existencias por producto y categoría, tabla de alertas y segmentadores.
5. La página **Ventas**, con tarjetas, evolución diaria, semanal y mensual, top de productos por unidades, ventas por categoría y segmentadores.
6. La validación de las cifras contra Odoo y contra consultas SQL de control.
7. Este manual y el video demostrativo de 2 a 3 minutos.

No forman parte del alcance la publicación en Power BI Service, la actualización programada, la seguridad a nivel de fila ni una página específica de compras. La vista `v_bi_compras` se cargó en el modelo y queda disponible para una ampliación futura.

### 1.3 Entregables

| Entregable | Ruta |
|---|---|
| Reporte de Power BI | `Proyecto/Fase3/bi/Reportes_TechCore.pbix` |
| Manual de BI | `Proyecto/Fase3/docu/manual_bi_francisco.md` |
| Capturas | `Proyecto/Fase3/docu/capturas/francisco_f3_*.png` |
| Video | Google Drive, enlace público (apartado VIDEO 2) |

### 1.4 Contexto de los datos

Las ventas fueron sembradas por Jonathan para que las series de tiempo tuvieran suficiente volumen y dispersión. Cada orden de venta de demostración lleva la referencia `DEMO-SEED`. Por lo tanto, las tendencias y los montos deben interpretarse como un ejercicio académico y no como ventas reales de la empresa.

La vista de ventas incluye únicamente líneas de órdenes en estado `sale` o `done`; excluye cotizaciones, borradores y cancelaciones. El campo `subtotal` proviene de `price_subtotal`, es decir, **no incluye impuestos**. Esta decisión es importante para interpretar la tarjeta de ventas y se explica con detalle en la sección 7.3.

---

## 2. Requisitos y preparación del entorno

### 2.1 Requisitos de hardware y software

| Componente | Requisito |
|---|---|
| Sistema operativo | Windows 10 u 11 de 64 bits |
| Docker Desktop | Con WSL2 activado y al menos 6 GB de RAM asignados |
| Power BI Desktop | Última versión disponible (Microsoft Store o instalador oficial) |
| Odoo | 17.0 Community Edition, en contenedor |
| PostgreSQL | 15, en contenedor, expuesto en `127.0.0.1:5432` |
| Navegador | Edge o Chrome para abrir Odoo |
| Conector PostgreSQL | Npgsql 4.1.x si la versión de Power BI lo solicita |
| Espacio libre en disco | Al menos 2 GB |
| Puertos libres | `5432` (PostgreSQL) y `8069` (Odoo) |

### 2.2 Arranque del entorno

El entorno se levanta desde la carpeta `Proyecto/techcore-odoo`:

```powershell
git clone https://github.com/JonathanJero/SOG1_2026S2_LOS4BABYS.git
cd SOG1_2026S2_LOS4BABYS\Proyecto\techcore-odoo
.\start.ps1
```

Si PowerShell bloquea la ejecución del script por la política de ejecución:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

El script construye las imágenes, levanta los servicios, espera a que PostgreSQL esté saludable y aplica la inicialización de la base. En el primer arranque, la restauración del dump puede tardar varios minutos.

Para verificar el estado de los contenedores:

```powershell
docker compose ps
```

El resultado esperado es:

| Contenedor | Servicio | Estado esperado | Puerto |
|---|---|---|---|
| `techcore_postgres_db` | `db` | `Up (healthy)` | `127.0.0.1:5432->5432/tcp` |
| `techcore_odoo_web` | `web` | `Up` | `0.0.0.0:8069->8069/tcp` |

### 2.3 Verificación de Odoo

1. Abrir `http://localhost:8069/web/login`.
2. Iniciar sesión con `admin@techcore.gt` y la contraseña `1234`.
3. Abrir `http://localhost:8069/shop` y confirmar que el catálogo muestra los 21 productos.
4. Abrir **Ventas > Órdenes** y confirmar que existen órdenes en estado confirmado.
5. Abrir **Inventario > Productos** y confirmar las existencias de los productos de prueba.

Si Odoo muestra un error 500 o la tienda no carga los estilos, revisar la sección 8.14.

### 2.4 Credenciales de solo lectura

| Parámetro | Valor |
|---|---|
| Servidor | `localhost` |
| Puerto | `5432` |
| Base de datos | `TechCore_DB` |
| Usuario | `bi_reader` |
| Contraseña | `bi_reader_techcore` |
| Modo de conexión | Importar |
| Esquema | `public` |

El usuario `bi_reader` fue creado por Jonathan con permisos de conexión a `TechCore_DB` y `SELECT` únicamente sobre las cuatro vistas `v_bi_*`. No tiene acceso a las tablas operativas de Odoo. La contraseña es una credencial de laboratorio; en un entorno productivo debería rotarse y almacenarse en un gestor de secretos.

### 2.5 Verificación de la capa analítica

Antes de abrir Power BI, se puede comprobar que las vistas responden con `psql`:

```powershell
docker compose exec -T -e PGPASSWORD=bi_reader_techcore db psql -U bi_reader -d TechCore_DB -c "SELECT COUNT(*) FROM v_bi_ventas_detalle;"
```

Si la consulta devuelve un número mayor que cero, la capa analítica está lista. Si devuelve un error de permisos o de relación inexistente, revisar la sección 8.5.

---

## 3. Conexión de Power BI a PostgreSQL

### 3.1 Procedimiento paso a paso

1. Abrir **Power BI Desktop**.
2. Ir a **Inicio > Obtener datos > Más > Base de datos > PostgreSQL**.
3. En la ventana de conexión, ingresar:
   - **Servidor:** `localhost:5432`
   - **Base de datos:** `TechCore_DB`
   - **Modo de conectividad de datos:** `Importar`
4. Si Power BI solicita credenciales, seleccionar el tipo **Base de datos** e ingresar:
   - **Nombre de usuario:** `bi_reader`
   - **Contraseña:** `bi_reader_techcore`
5. Dejar desmarcada la opción **Usar SSL** para la conexión local. El contenedor de PostgreSQL del proyecto no exige SSL.
6. En el **Navegador**, expandir el esquema `public` y seleccionar únicamente las cuatro vistas:
   - `public.v_bi_compras`
   - `public.v_bi_inventario`
   - `public.v_bi_top_productos`
   - `public.v_bi_ventas_detalle`
7. Verificar la vista previa de `v_bi_ventas_detalle` y hacer clic en **Cargar**.
8. Confirmar que las cuatro tablas aparecen en el panel **Datos** y renombrarlas como se indica en la sección 4.2.

![Figura 1: Conexión a PostgreSQL y selección de las cuatro vistas analíticas](capturas/francisco_f3_01_seleccion_vistas.png)

*Figura 1. Navegador de Power BI Desktop conectado a `localhost:5432`, base `TechCore_DB`, con las cuatro vistas `v_bi_*` seleccionadas. La vista previa corresponde a `v_bi_ventas_detalle` y muestra las órdenes, fechas, clientes y semanas del periodo de demostración.*

La captura confirma que la conexión llega a la base correcta y que la vista de ventas contiene datos. La contraseña no se reproduce en el texto del manual.

### 3.2 Carga en modo Importar

Se eligió el modo **Importar** porque:

- El volumen es pequeño (120 líneas de venta, 21 productos y 17 órdenes de compra).
- Las vistas son de solo lectura y cambian con poca frecuencia.
- El rendimiento de los visuales es mejor con los datos en memoria.
- La evaluación se realizará en la máquina local, sin dependencia de la red.

La desventaja es que los datos no se actualizan en tiempo real. Después de una nueva venta o de un cambio de inventario, hay que pulsar **Inicio > Actualizar** en Power BI Desktop.

### 3.3 Verificación de la carga

Después de cargar, comprobar en el panel **Datos** que existen las cuatro tablas y que sus columnas tienen el tipo correcto:

| Tabla | Filas esperadas | Columnas clave |
|---|---|---|
| `v_bi_ventas_detalle` | 120 | `orden`, `fecha`, `cliente`, `canal`, `codigo_producto`, `cantidad`, `subtotal` |
| `v_bi_inventario` | 21 | `codigo_producto`, `producto`, `categoria`, `existencias`, `stock_minimo`, `estado_stock` |
| `v_bi_top_productos` | 17 | `codigo_producto`, `producto`, `unidades_vendidas`, `ingresos`, `ranking` |
| `v_bi_compras` | 36 | `orden`, `fecha`, `proveedor`, `producto`, `cantidad`, `subtotal`, `estado` |

Las fechas deben estar en tipo **Fecha** y los montos en tipo **Número decimal**. Si alguna columna aparece como texto, corregir el tipo en **Transformar datos**.

### 3.4 Si Power BI solicita Npgsql

Algunas versiones de Power BI Desktop no incluyen el proveedor Npgsql. El síntoma es un mensaje como:

```text
The provider 'Npgsql' is not registered.
```

La solución es instalar **Npgsql 4.1.x** desde el instalador oficial, marcar la opción **Npgsql GAC Installation** y reiniciar Power BI Desktop. En versiones recientes el conector ya viene incluido y este paso no es necesario.

### 3.5 Plan alterno con CSV

Si la conexión directa no es posible en la máquina de evaluación, se puede usar un plan alterno:

1. Pedir a Jonathan la exportación de cada vista a CSV con `COPY ... TO`.
2. En Power BI: **Obtener datos > Texto o CSV**.
3. Cargar los cuatro archivos y renombrar las tablas igual que las vistas.
4. Mantener las mismas medidas y relaciones.

Este plan no reemplaza la conexión directa, pero permite demostrar el tablero si el conector de PostgreSQL falla durante la evaluación.

---

## 4. Modelo de datos

### 4.1 Las cuatro vistas y su propósito

| Vista | Columnas principales | Propósito en el reporte |
|---|---|---|
| `v_bi_ventas_detalle` | `orden`, `fecha`, `anio`, `mes`, `semana`, `cliente`, `segmento`, `canal`, `codigo_producto`, `producto`, `categoria`, `cantidad`, `precio_unitario`, `subtotal`, `estado` | Alimenta las tarjetas de ventas, la evolución diaria, semanal y mensual, y los análisis por canal, segmento y categoría. |
| `v_bi_inventario` | `codigo_producto`, `producto`, `categoria`, `existencias`, `stock_minimo`, `stock_maximo`, `estado_stock`, `costo`, `precio_venta`, `valor_inventario`, `cantidad_por_recibir` | Alimenta las tarjetas de inventario, el gráfico por producto, el gráfico por categoría y la tabla de alertas. |
| `v_bi_top_productos` | `codigo_producto`, `producto`, `categoria`, `unidades_vendidas`, `ingresos`, `ranking` | Aporta el ranking precalculado por ingresos y sirve de apoyo para el top de productos. |
| `v_bi_compras` | `orden`, `fecha`, `proveedor`, `producto`, `cantidad`, `cantidad_recibida`, `subtotal`, `estado` | Se cargó para una futura página de compras; no se usa en las dos páginas obligatorias. |

La vista de ventas usa `price_subtotal`, que es el subtotal de la línea **sin impuestos**. La vista de inventario es una fotografía del stock en la ubicación `WH/Stock`; no es un histórico. La vista de top productos calcula el ranking con `DENSE_RANK()` ordenado por ingresos descendentes. La vista de compras incluye órdenes confirmadas y borradores; el borrador no representa una compra comprometida.

### 4.2 Renombrado de tablas

Para que el modelo sea legible, las vistas se renombraron de la siguiente manera:

| Vista original | Nombre en el modelo | Tipo |
|---|---|---|
| `v_bi_ventas_detalle` | `FactVentas` | Tabla de hechos |
| `v_bi_inventario` | `FactInventario` | Tabla de hechos / fotografía |
| `v_bi_top_productos` | `TopProductos` | Tabla agregada de apoyo |
| `v_bi_compras` | `FactCompras` | Tabla de hechos |

### 4.3 Esquema en estrella

El modelo sigue un esquema en estrella con una tabla de hechos principal (`FactVentas`), una tabla de inventario (`FactInventario`), una tabla agregada (`TopProductos`) y dimensiones compartidas. La estructura simplificada es la siguiente:

```text
DimFecha ─────1:*────┐
DimCliente ───1:*────┼──> FactVentas <──1:*── DimCanal
DimProducto ──1:*────┘         │
    │                          │ 1:*
    ├──1:*──> FactInventario   └──> TopProductos (agregado)

DimFecha ─────1:*────> FactCompras <──1:*── DimProveedor
```

Las relaciones son de uno a varios, con filtro en una sola dirección, desde la dimensión hacia el hecho. La tabla `DimFecha` se marcó como tabla de fechas del modelo.

### 4.4 Tablas y relaciones

| Desde | Hacia | Cardinalidad | Filtro | Propósito |
|---|---|---|---|---|
| `DimProducto[codigo_producto]` | `FactVentas[codigo_producto]` | 1:* | Único | Filtrar ventas por producto y categoría. |
| `DimProducto[codigo_producto]` | `FactInventario[codigo_producto]` | 1:* | Único | Filtrar inventario por producto y categoría. |
| `DimProducto[codigo_producto]` | `TopProductos[codigo_producto]` | 1:* | Único | Relacionar el ranking con el catálogo. |
| `DimCliente[cliente]` | `FactVentas[cliente]` | 1:* | Único | Segmentar por cliente y segmento. |
| `DimCanal[canal]` | `FactVentas[canal]` | 1:* | Único | Segmentar por canal Web o Cotización. |
| `DimFecha[fecha]` | `FactVentas[fecha]` | 1:* | Único | Evolución diaria, semanal y mensual. |
| `DimFecha[fecha]` | `FactCompras[fecha]` | 1:* | Único | Compras por fecha (uso futuro). |
| `DimProveedor[proveedor]` | `FactCompras[proveedor]` | 1:* | Único | Compras por proveedor (uso futuro). |

La tabla `FactCompras` no tiene `codigo_producto`; si en el futuro se quiere relacionar con `DimProducto`, conviene agregar esa columna a la vista o usar el nombre del producto como clave.

### 4.5 Dimensiones

| Dimensión | Columnas | Origen sugerido |
|---|---|---|
| `DimProducto` | `codigo_producto`, `producto`, `categoria` | `SUMMARIZE` de `FactInventario` (incluye los 21 productos) o una unión con `FactVentas` si hay productos vendidos sin registro de inventario. |
| `DimCliente` | `cliente`, `segmento` | `SUMMARIZE(FactVentas, FactVentas[cliente], FactVentas[segmento])`. |
| `DimCanal` | `canal` | `SUMMARIZE(FactVentas, FactVentas[canal])`. |
| `DimProveedor` | `proveedor` | `SUMMARIZE(FactCompras, FactCompras[proveedor])`. |
| `DimFecha` | `fecha`, `Año`, `Mes`, `NombreMes`, `AñoMes`, `AñoMesOrden`, `SemanaISO`, `AñoSemana`, `AñoSemanaOrden`, `Día`, `DíaSemana` | Tabla calculada con `CALENDAR` y `ADDCOLUMNS` (sección 4.6). |

Ejemplo de creación de `DimProducto` con DAX:

```dax
DimProducto =
SUMMARIZE (
    FactInventario,
    FactInventario[codigo_producto],
    FactInventario[producto],
    FactInventario[categoria]
)
```

Si se construye solo desde `FactVentas`, los productos sin ventas (Dell, HPE, Lenovo y Cisco) quedarían fuera del gráfico de inventario. Por eso se recomienda partir de `FactInventario`, que contiene los 21 productos. Si se necesita el costo y el precio de venta, ya están en `FactInventario`; se pueden incorporar a la dimensión con `LOOKUPVALUE` o en Power Query.

### 4.6 Tabla de fechas

La tabla `DimFecha` cubre del 1 de enero al 31 de diciembre de 2026. Las columnas de orden (`AñoMesOrden` y `AñoSemanaOrden`) garantizan que los ejes se ordenen cronológicamente y no alfabéticamente.

```dax
DimFecha =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2026, 1, 1 ), DATE ( 2026, 12, 31 ) ),
    "Año", YEAR ( [Date] ),
    "Mes", MONTH ( [Date] ),
    "NombreMes", FORMAT ( [Date], "MMMM" ),
    "AñoMes", FORMAT ( [Date], "YYYY-MM" ),
    "AñoMesOrden", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
    "SemanaISO", WEEKNUM ( [Date], 21 ),
    "AñoSemana", YEAR ( [Date] ) & "-S" & FORMAT ( WEEKNUM ( [Date], 21 ), "00" ),
    "AñoSemanaOrden", YEAR ( [Date] ) * 100 + WEEKNUM ( [Date], 21 ),
    "Día", DAY ( [Date] ),
    "DíaSemana", FORMAT ( [Date], "dddd" )
)
```

En el rango actual de ventas (julio a octubre de 2026) no hay semanas de borde de año, por lo que `AñoSemana` coincide con el año calendario. Si se amplía el periodo a diciembre o enero, conviene usar el año ISO para evitar ambigüedad.

### 4.7 Medidas DAX

| Medida | Fórmula | Uso |
|---|---|---|
| `Ventas Totales` | `SUM ( FactVentas[subtotal] )` | Tarjeta de ventas, series de tiempo, top de productos y pastel. |
| `Órdenes` | `DISTINCTCOUNT ( FactVentas[orden] )` | Tarjeta de órdenes. |
| `Ticket Promedio` | `DIVIDE ( [Ventas Totales], [Órdenes] )` | Tarjeta de ticket promedio. |
| `Unidades Vendidas` | `SUM ( FactVentas[cantidad] )` | Tarjeta de unidades y top por unidades. |
| `Total Existencias` | `SUM ( FactInventario[existencias] )` | Tarjeta de existencias y gráficos de inventario. |
| `Valor Inventario` | `SUM ( FactInventario[valor_inventario] )` | Tarjeta de valor del inventario. |
| `Productos en Stock Bajo` | `CALCULATE ( DISTINCTCOUNT ( FactInventario[codigo_producto] ), FactInventario[estado_stock] = "Bajo" )` | Tarjeta de alertas. |
| `Productos Sin Regla` | `CALCULATE ( DISTINCTCOUNT ( FactInventario[codigo_producto] ), FactInventario[estado_stock] = "Sin regla" )` | Tarjeta de productos sin punto de reorden. |
| `Cantidad por Recibir` | `SUM ( FactInventario[cantidad_por_recibir] )` | Columna de la tabla de alertas (opcional como tarjeta). |
| `Ventas con IVA` | `SUMX ( FactVentas, ROUND ( FactVentas[subtotal] * 1.12, 2 ) )` | Medida opcional para conciliar con el total de Odoo. |

La medida `Ventas con IVA` puede diferir por centavos del total de Odoo debido al redondeo por línea. Para una conciliación exacta conviene agregar `amount_total` y `amount_tax` de la orden a la vista.

### 4.8 Formato del reporte

- Tema oscuro de Power BI (`ReportThemeDark`) con acentos azules y verdes.
- Páginas de 1920 x 1080 px (16:9).
- Tarjetas con formato de moneda `Q #,##0.00` y separador de miles.
- Gráficos con títulos claros, etiquetas de datos y orden descendente cuando el objetivo es comparar magnitudes.
- Tabla de alertas filtrada a `estado_stock = "Bajo"`.
- Segmentadores con selección simple o múltiple y opción de borrar filtro.

---

## 5. Reporte de Inventario

### 5.1 Objetivo

La página **Inventario** responde cuatro preguntas:

1. ¿Cuántas unidades hay en existencia?
2. ¿Cuánto vale el inventario al costo estándar?
3. ¿Qué productos están por debajo de su stock mínimo?
4. ¿Qué productos no tienen una regla de reposición?

### 5.2 Captura de la página

![Figura 2: Página de Inventario con tarjetas, existencias por producto y categoría, tabla de alertas y segmentadores](capturas/francisco_f3_02_dashboard_inventario.png)

*Figura 2. Página `Inventario` del reporte. En la fila superior se muestran las cuatro tarjetas; en el centro, el gráfico de existencias por producto y el de existencias por categoría; en la parte inferior, la tabla de alertas y los segmentadores de categoría, estado y producto.*

### 5.3 Visuales de la página

| Visual | Tipo | Campos | Qué muestra |
|---|---|---|---|
| Total Existencias | Tarjeta | `FactInventario[Total Existencias]` | 1,219 unidades (la tarjeta las abrevia como 1.22 mil). |
| Valor Inventario | Tarjeta | `FactInventario[Valor Inventario]` | Q 242,960.00 (la tarjeta lo abrevia como Q 242.96 mil). |
| Productos en Stock Bajo | Tarjeta | `FactInventario[Productos en Stock Bajo]` | 4 productos. |
| Productos Sin Regla | Tarjeta | `FactInventario[Productos Sin Regla]` | 17 productos. |
| Total Existencias por producto | Gráfico de barras | Eje: `DimProducto[producto]`; valor: `[Total Existencias]` | Existencias de los 21 productos, ordenadas de mayor a menor. |
| Total Existencias por categoría | Gráfico de columnas | Eje: `DimProducto[categoria]`; valor: `[Total Existencias]` | Existencias agrupadas en las 8 categorías. |
| Alertas de stock bajo | Tabla | `codigo_producto`, `producto`, `categoria`, `existencias`, `stock_minimo`, `cantidad_por_recibir`, `estado_stock` | Los 4 productos con `estado_stock = "Bajo"`. |
| Segmentador de categoría | Segmentador | `FactInventario[categoria]` | Filtra la página por categoría. |
| Segmentador de estado | Segmentador | `FactInventario[estado_stock]` | Filtra por los estados disponibles (Bajo y Sin regla al corte). |
| Segmentador de producto | Segmentador | `FactInventario[producto]` | Permite aislar un producto específico. |

La tabla de alertas tiene un filtro de nivel de visual en `estado_stock = "Bajo"`. Por eso muestra los cuatro productos críticos cuando el segmentador de estado está en Bajo o sin selección. Si se elige otro estado, la intersección de filtros puede dejar la tabla vacía; para explorar otros estados conviene quitar el filtro del visual o usar los gráficos. Los segmentadores afectan a las tarjetas y a los gráficos, y también se cruzan con el filtro de la tabla.

### 5.4 Lectura de las tarjetas

| Tarjeta | Valor exacto | Interpretación |
|---|---|---|
| Total Existencias | 1,219 unidades | Inventario total en `WH/Stock` al corte del 22/10/2026. |
| Valor Inventario | Q 242,960.00 | Valor al costo estándar. Los servidores concentran valor aunque tengan pocas unidades. |
| Productos en Stock Bajo | 4 | Productos con existencia menor al mínimo definido en su regla de reposición. |
| Productos Sin Regla | 17 | Productos sin `stock.warehouse.orderpoint`; no se evalúan contra un mínimo. |

### 5.5 Existencias por categoría

| Categoría | Productos | Unidades | Valor | Productos en Bajo |
|---|---:|---:|---:|---:|
| Memoria RAM | 3 | 372 | Q 28,320.00 | 0 |
| Procesador | 4 | 249 | Q 90,440.00 | 0 |
| SSD | 3 | 217 | Q 26,280.00 | 0 |
| Switch | 3 | 171 | Q 22,000.00 | 1 |
| Tarjeta Madre | 3 | 85 | Q 27,060.00 | 0 |
| Disco Duro | 1 | 66 | Q 17,160.00 | 0 |
| Periféricos | 1 | 50 | Q 3,500.00 | 0 |
| Servidor | 3 | 9 | Q 28,200.00 | 3 |
| **Total** | **21** | **1,219** | **Q 242,960.00** | **4** |

La categoría **Servidor** tiene solo 9 unidades, pero un valor de Q 28,200.00, equivalente al 11.61 % del valor del inventario. Esto explica por qué los tres servidores en stock bajo son críticos: aunque son pocas unidades, su costo unitario es alto.

### 5.6 Tabla de alertas de stock bajo

| Código | Producto | Categoría | Existencias | Mínimo | Por recibir | Estado |
|---|---|---|---:|---:|---:|---|
| PROD-009 | Dell PowerEdge R750 | Servidor | 2 | 5 | 0 | Bajo |
| PROD-010 | HPE ProLiant DL380 Gen10 | Servidor | 3 | 5 | 0 | Bajo |
| PROD-018 | Lenovo ThinkSystem SR650 | Servidor | 4 | 5 | 0 | Bajo |
| PROD-007 | Cisco Catalyst 2960-X 24 Port | Switch | 5 | 10 | 0 | Bajo |

Los cuatro productos suman **14 unidades** y **Q 31,200.00** de valor, es decir, el **12.84 %** del valor total del inventario. Ninguno tiene mercancía en tránsito: `cantidad_por_recibir = 0` en todos los casos.

Para llevar los cuatro productos al mínimo se necesitan:

| Producto | Faltante para el mínimo | Costo de reposición |
|---|---:|---:|
| Dell PowerEdge R750 | 3 | Q 10,500.00 |
| HPE ProLiant DL380 Gen10 | 2 | Q 6,400.00 |
| Lenovo ThinkSystem SR650 | 1 | Q 2,900.00 |
| Cisco Catalyst 2960-X 24 Port | 5 | Q 3,000.00 |
| **Total** | **11** | **Q 22,800.00** |

Se recomienda añadir una cantidad de seguridad adicional, especialmente en los servidores, porque el tiempo de reposición de hardware empresarial suele ser mayor que el de los componentes de consumo.

### 5.7 Productos sin regla de reposición

Los 17 productos restantes tienen `stock_minimo = 0` y `estado_stock = "Sin regla"`. No están en la tabla de alertas porque no existe un mínimo contra el cual compararlos. Entre ellos hay productos con ventas altas, como el Samsung 990 PRO 2TB NVMe (36 unidades vendidas) y el Corsair Vengeance 32GB DDR5 (18), y otros con inventario alto pero baja salida, como el TP-Link TL-SG108E 8 Port (148 unidades en stock).

La tarjeta **Productos Sin Regla** es una invitación a completar la configuración: mientras no se definan puntos de reorden, el reporte no puede advertir sobre su agotamiento.

### 5.8 Interpretación y mejoras

- El inventario está concentrado en componentes de alta rotación (memoria RAM, procesadores y SSD), que suman 838 unidades.
- El riesgo financiero está en los servidores: 9 unidades, Q 28,200.00 y tres de ellos por debajo del mínimo.
- El switch Cisco también está en alerta: 5 unidades frente a un mínimo de 10.
- No hay órdenes de compra en tránsito; la reposición debe iniciarse.
- La tabla de alertas no tiene formato condicional en rojo en la versión actual. Se recomienda aplicarlo a la columna `estado_stock` para reforzar la lectura visual.
- El gráfico de barras está ordenado de mayor a menor. Para priorizar la reposición, conviene invertirlo y mostrar los productos con menos existencias primero.
- Se recomienda agregar un medidor (gauge) que compare las existencias del producto seleccionado contra su stock mínimo. La tabla de alertas ya cumple esa función, pero el medidor facilita la lectura ejecutiva.

---

## 6. Reporte de Ventas

### 6.1 Objetivo

La página **Ventas** responde cinco preguntas:

1. ¿Cuánto se vendió en el periodo y cuántas órdenes se emitieron?
2. ¿Cómo evolucionan las ventas por día, por semana y por mes?
3. ¿Qué productos lideran las ventas por unidades?
4. ¿Qué categorías, canales y segmentos explican los ingresos?
5. ¿Cómo se comporta el ticket promedio?

### 6.2 Captura de la página

![Figura 3: Página de Ventas con tarjetas, evolución diaria, semanal y mensual, top de unidades, ventas por categoría y segmentadores](capturas/francisco_f3_03_dashboard_ventas.png)

*Figura 3. Página `Ventas` del reporte. En la fila superior se muestran las cuatro tarjetas; en el centro, la evolución semanal, diaria y mensual; en la parte inferior, el top de unidades por producto, el pastel de ventas por categoría y los segmentadores de fecha, canal, segmento y categoría.*

### 6.3 Visuales de la página

| Visual | Tipo | Campos | Qué muestra |
|---|---|---|---|
| Ventas Totales | Tarjeta | `FactVentas[Ventas Totales]` | Q 62,946.36 (la tarjeta lo abrevia como 62.95 mil). |
| Órdenes | Tarjeta | `FactVentas[Órdenes]` | 77 órdenes. |
| Ticket Promedio | Tarjeta | `FactVentas[Ticket Promedio]` | Q 817.49. |
| Unidades Vendidas | Tarjeta | `FactVentas[Unidades Vendidas]` | 221 unidades. |
| Ventas Totales por Año y Semana | Gráfico de columnas | Eje: `DimFecha[AñoSemana]`; valor: `[Ventas Totales]` | Evolución semanal (13 semanas ISO). |
| Ventas Totales por fecha | Gráfico de líneas | Eje: `DimFecha[fecha]`; valor: `[Ventas Totales]` | Evolución diaria del 13/07/2026 al 06/10/2026. |
| Ventas Totales por Año y Mes | Gráfico de columnas | Eje: `DimFecha[AñoMes]`; valor: `[Ventas Totales]` | Evolución mensual (julio a octubre). |
| Top Unidades por producto | Gráfico de barras | Eje: `DimProducto[producto]`; valor: `[Unidades Vendidas]`; filtro Top N | Top de productos por unidades. |
| Ventas Totales por categoría | Gráfico circular | Leyenda: `TopProductos[categoria]`; valor: `[Ventas Totales]` | Participación de cada categoría en los ingresos. |
| Segmentador de fecha | Segmentador | `DimFecha[fecha]` | Rango de fechas. |
| Segmentador de canal | Segmentador | `DimCanal[canal]` | Web o Cotización. |
| Segmentador de segmento | Segmentador | `DimCliente[segmento]` | B2B o B2C. |
| Segmentador de categoría | Segmentador | `DimProducto[categoria]` | Filtra por categoría de producto. |

### 6.4 Tarjetas de ventas

| Tarjeta | Valor exacto | Cálculo |
|---|---|---|
| Ventas Totales | Q 62,946.36 | Suma de `FactVentas[subtotal]` (sin IVA). |
| Órdenes | 77 | `DISTINCTCOUNT` de `FactVentas[orden]`. |
| Ticket Promedio | Q 817.49 | Ventas netas / órdenes. |
| Unidades Vendidas | 221 | Suma de `FactVentas[cantidad]`. |

El ticket promedio se calcula sobre las ventas netas. Si se usara el total con IVA, el ticket sería Q 915.58 (70,500.00 / 77). La diferencia es el IVA.

### 6.5 Evolución diaria, semanal y mensual

#### 6.5.1 Nivel diario

El gráfico de líneas **Ventas Totales por fecha** muestra la serie diaria entre el 13 de julio y el 6 de octubre de 2026. La serie permite identificar picos de venta y días sin movimiento. Como los datos son de demostración, la volatilidad diaria es alta y no debe interpretarse como una estacionalidad real.

#### 6.5.2 Nivel mensual

| Mes | Órdenes | Ventas netas | Participación |
|---|---:|---:|---:|
| Julio 2026 | 17 | Q 14,526.77 | 23.08 % |
| Agosto 2026 | 27 | Q 21,553.53 | 34.24 % |
| Septiembre 2026 | 26 | Q 21,392.85 | 33.99 % |
| Octubre 2026 (1 al 6) | 7 | Q 5,473.21 | 8.69 % |
| **Total** | **77** | **Q 62,946.36** | **100.00 %** |

Agosto y septiembre son los meses más fuertes, con ventas similares (Q 21,553.53 y Q 21,392.85). Octubre es un mes parcial de solo seis días; no debe compararse directamente con los meses completos.

#### 6.5.3 Nivel semanal

| Semana ISO | Órdenes | Ventas netas |
|---|---:|---:|
| 2026-S29 | 6 | Q 4,464.28 |
| 2026-S30 | 6 | Q 6,258.92 |
| 2026-S31 | 6 | Q 4,125.00 |
| 2026-S32 | 7 | Q 7,571.41 |
| 2026-S33 | 6 | Q 4,491.06 |
| 2026-S34 | 6 | Q 3,250.00 |
| 2026-S35 | 6 | Q 5,517.84 |
| 2026-S36 | 6 | Q 4,687.50 |
| 2026-S37 | 6 | Q 4,749.99 |
| 2026-S38 | 6 | Q 5,026.78 |
| 2026-S39 | 6 | Q 4,687.51 |
| 2026-S40 | 6 | Q 5,258.93 |
| 2026-S41 | 4 | Q 2,857.14 |
| **Total** | **77** | **Q 62,946.36** |

La semana 32 (Q 7,571.41) es la de mayor venta; la semana 34 (Q 3,250.00) es la de menor venta entre las semanas completas. La semana 41 es parcial (solo hasta el 6 de octubre). El promedio semanal es de Q 4,842.03.

### 6.6 Top de productos por unidades

| Puesto | Código | Producto | Unidades | Ingresos |
|---:|---|---|---:|---:|
| 1 | PROD-005 | Samsung 990 PRO 2TB NVMe | 36 | Q 6,428.55 |
| 2 | PROD-003 | Corsair Vengeance 32GB DDR5 | 18 | Q 2,410.73 |
| 3 | PROD-011 | ASUS ROG Maximus Z790 Hero | 17 | Q 9,107.13 |
| 3 | PROD-002 | AMD Ryzen 9 7950X | 17 | Q 9,107.13 |
| 3 | PROD-004 | Kingston Fury Beast 16GB DDR4 | 17 | Q 910.70 |

Hay un empate en 17 unidades entre el ASUS ROG Maximus, el AMD Ryzen 9 y el Kingston Fury Beast. Por eso los puestos 3, 4 y 5 se comparten. Los cinco productos suman **105 unidades** (47.51 % del total) y **Q 27,964.24** (44.43 % de los ingresos).

El gráfico **Top Unidades por producto** debe mostrar estos cinco productos. Si muestra otros, revisar la sección 8.7: el filtro Top N está configurado sobre `TopProductos[producto]` por conteo y no por la medida `Unidades Vendidas`.

### 6.7 Top de productos por ingresos

El ranking por ingresos se calcula con `DENSE_RANK()` en `v_bi_top_productos`. Como hay un empate en el segundo puesto, el filtro `ranking <= 5` devuelve **seis filas**, no cinco:

| Ranking | Código | Producto | Unidades | Ingresos |
|---:|---|---|---:|---:|
| 1 | PROD-001 | Intel Core i9-13900K | 16 | Q 9,285.72 |
| 2 | PROD-002 | AMD Ryzen 9 7950X | 17 | Q 9,107.13 |
| 2 | PROD-011 | ASUS ROG Maximus Z790 Hero | 17 | Q 9,107.13 |
| 3 | PROD-005 | Samsung 990 PRO 2TB NVMe | 36 | Q 6,428.55 |
| 4 | PROD-008 | Ubiquiti UniFi Switch 48 PoE | 6 | Q 5,892.84 |
| 5 | PROD-014 | AMD Ryzen 5 7600X | 15 | Q 3,750.00 |

Los seis productos suman **Q 43,571.37**, equivalentes al **69.22 %** de las ventas netas. El Intel Core i9-13900K es el producto con más ingresos (Q 9,285.72), aunque solo vendió 16 unidades: su precio unitario es alto. El Samsung 990 PRO, en cambio, lidera por unidades (36) pero genera Q 6,428.55.

Si se necesita una tabla de exactamente cinco filas, se debe romper el empate con un criterio adicional, por ejemplo, unidades vendidas o código de producto. Con `DENSE_RANK()` se respeta el empate y se muestran seis filas; con `ROW_NUMBER()` se fuerza un orden arbitrario. La decisión debe documentarse en el reporte.

### 6.8 Ventas por categoría

| Categoría | Órdenes | Unidades | Ventas netas | Participación |
|---|---:|---:|---:|---:|
| Procesador | 27 | 51 | Q 22,999.99 | 36.54 % |
| Tarjeta Madre | 20 | 37 | Q 14,910.70 | 23.69 % |
| SSD | 29 | 58 | Q 9,598.17 | 15.25 % |
| Switch | 7 | 8 | Q 5,964.27 | 9.48 % |
| Memoria RAM | 19 | 43 | Q 5,321.43 | 8.45 % |
| Disco Duro | 6 | 9 | Q 2,812.50 | 4.47 % |
| Periféricos | 7 | 15 | Q 1,339.30 | 2.13 % |
| **Total** | **77** | **221** | **Q 62,946.36** | **100.00 %** |

Las órdenes por categoría no son sumables: una misma orden puede incluir productos de varias categorías. El total de 77 corresponde a las órdenes distintas del periodo.

Procesador, Tarjeta Madre y SSD concentran el **75.48 %** de los ingresos. El pastel de la página muestra esa distribución. La categoría con más unidades es SSD (58), seguida de Procesador (51) y Memoria RAM (43).

### 6.9 Ventas por canal y segmento

| Canal | Segmento | Órdenes | Ventas netas | Participación |
|---|---|---:|---:|---:|
| Web | B2C | 34 | Q 26,330.33 | 41.83 % |
| Web | B2B | 16 | Q 16,339.25 | 25.96 % |
| Cotización | B2B | 23 | Q 15,625.00 | 24.82 % |
| Cotización | B2C | 4 | Q 4,651.78 | 7.39 % |
| **Total** |  | **77** | **Q 62,946.36** | **100.00 %** |

Subtotales:

| Dimensión | Órdenes | Ventas netas | Participación |
|---|---:|---:|---:|
| Web | 50 | Q 42,669.58 | 67.79 % |
| Cotización | 27 | Q 20,276.78 | 32.21 % |
| B2B | 39 | Q 31,964.25 | 50.78 % |
| B2C | 38 | Q 30,982.11 | 49.22 % |

El canal Web es el principal motor de ventas, con el 67.79 % de los ingresos. Dentro del canal Web, el segmento B2C aporta el 41.83 % del total. La cotización B2B, aunque tiene 23 órdenes, aporta el 24.82 % y registra el ticket promedio más bajo de los cuatro flujos (Q 679.35); el ticket más alto está en Cotización B2C (Q 1,162.95) y Web B2B (Q 1,021.20).

La página no incluye un gráfico de barras específico por canal y segmento; los segmentadores permiten filtrar las tarjetas y los gráficos, y las tablas de esta sección documentan la comparación. Se recomienda agregar ese gráfico en una versión futura.

### 6.10 Segmentadores e interactividad

| Segmentador | Campo | Uso |
|---|---|---|
| Fecha | `DimFecha[fecha]` | Seleccionar un rango de fechas; recalcula tarjetas y gráficos. |
| Canal | `DimCanal[canal]` | Comparar Web contra Cotización. |
| Segmento | `DimCliente[segmento]` | Comparar B2B contra B2C. |
| Categoría | `DimProducto[categoria]` | Aislar una categoría de producto. |

Los segmentadores son independientes entre sí y se combinan con lógica AND. Para limpiar todos los filtros, usar el icono de borrador del panel de filtros o **Restablecer filtros** en la cinta.

### 6.11 Interpretación

- Las ventas netas del periodo son **Q 62,946.36**; con IVA, **Q 70,500.00**.
- El ticket promedio es **Q 817.49** y se vendieron **221 unidades** en **77 órdenes**.
- El canal Web concentra el **67.79 %** de los ingresos; el B2C es el segmento más fuerte dentro de Web.
- Procesador, Tarjeta Madre y SSD explican el **75.48 %** de los ingresos.
- El Intel Core i9-13900K lidera por ingresos; el Samsung 990 PRO lidera por unidades.
- El top 5 por ingresos (seis filas por empate) representa el **69.22 %** de las ventas.
- Agosto y septiembre son los meses más fuertes; octubre es parcial.
- La semana 32 es la de mayor venta; la 34, la de menor venta entre las semanas completas.

### 6.12 Mejoras recomendadas

- Corregir el filtro Top N del gráfico de unidades para que clasifique por `[Unidades Vendidas]` y no por conteo de `TopProductos[producto]` (sección 8.7).
- Agregar un segundo gráfico de top 5 por ingresos, con un criterio de desempate documentado.
- Agregar un gráfico de barras de ventas por canal y por segmento.
- Cambiar la leyenda del pastel a `DimProducto[categoria]` para que dependa de la dimensión de producto y no de la tabla agregada.
- Asignar títulos personalizados y etiquetas de datos a todos los visuales.
- Renombrar la tarjeta **Ventas Totales** como **Ventas netas (sin IVA)** para evitar confusiones con el total de Odoo.
- Agregar una tarjeta de **Ventas con IVA** si la evaluación exige el total facturado.

---

## 7. Validación de cifras

### 7.1 Metodología

La validación se hizo en tres niveles:

1. **Contra las vistas SQL:** se ejecutaron consultas de control con `bi_reader` (Anexo B).
2. **Contra Odoo:** se compararon las tarjetas con los reportes de **Ventas > Informes** y **Inventario > Informes > Stock**.
3. **Contra el propio reporte:** se revisó que las tarjetas, los gráficos y las tablas mostraran los mismos totales al aplicar y limpiar filtros.

Las cifras de Odoo pueden variar según la fecha de corte y según se consulte el subtotal o el total con impuestos. Por eso la tabla distingue explícitamente ambos conceptos.

### 7.2 Tabla "Power BI frente a Odoo"

| Indicador | Power BI | Odoo / SQL | Diferencia | Estado |
|---|---:|---:|---:|---|
| Órdenes de venta | 77 | 77 | 0 | Coincide |
| Líneas de venta | No se muestra en una tarjeta | 120 | No aplica | Dato de control |
| Unidades vendidas | 221 | 221 | 0 | Coincide |
| Ventas netas (sin IVA) | Q 62,946.36 | Q 62,946.36 | Q 0.00 | Coincide |
| IVA (12 %) | No se muestra en una tarjeta | Q 7,553.64 | No aplica | Se concilia |
| Total con IVA | La tarjeta muestra el neto | Q 70,500.00 | Q 7,553.64 | Diferencia por IVA |
| Ticket promedio | Q 817.49 | Q 817.49 | Q 0.00 | Coincide |
| Existencias totales | 1,219 | 1,219 | 0 | Coincide |
| Valor del inventario | Q 242,960.00 | Q 242,960.00 | Q 0.00 | Coincide |
| Productos en stock bajo | 4 | 4 | 0 | Coincide |
| Productos sin regla | 17 | 17 | 0 | Coincide |
| Top 5 por ingresos | 6 filas por empate | 6 filas | 0 | Coincide con la vista |
| Top 5 por unidades | 5 productos | 5 productos | 0 | Coincide con el ranking calculado; el filtro del visual debe corregirse (8.7) |

### 7.3 Conciliación del IVA

La vista `v_bi_ventas_detalle` usa `price_subtotal`, que es el subtotal de la línea sin impuestos. La suma de esas líneas es **Q 62,946.36**. Odoo calcula el IVA del 12 % por línea, redondea y obtiene un total de **Q 70,500.00**; el impuesto es **Q 7,553.64**.

La diferencia de **Q 7,553.64** no es un error del tablero: es el IVA que la vista no incluye. Para evitar confusiones:

- La tarjeta **Ventas Totales** debe interpretarse como **ventas netas**.
- La tabla de validación compara el subtotal de Odoo con la tarjeta y el total con IVA por separado.
- Si se necesita una tarjeta con el total facturado, se puede crear la medida `Ventas con IVA` (sección 4.7) o agregar `amount_total` y `amount_tax` a la vista.
- La medida `Ventas con IVA` calculada como `subtotal * 1.12` puede diferir por centavos del total de Odoo debido al redondeo por línea. Para una coincidencia exacta, usar los campos de la orden.

### 7.4 Empate del top 5 por ingresos

La vista `v_bi_top_productos` usa `DENSE_RANK()` sobre los ingresos. El AMD Ryzen 9 7950X y el ASUS ROG Maximus Z790 Hero tienen exactamente **Q 9,107.13** cada uno, por lo que ambos reciben el ranking 2. El filtro `ranking <= 5` devuelve:

- Ranking 1: Intel Core i9-13900K.
- Ranking 2: AMD Ryzen 9 7950X.
- Ranking 2: ASUS ROG Maximus Z790 Hero.
- Ranking 3: Samsung 990 PRO 2TB NVMe.
- Ranking 4: Ubiquiti UniFi Switch 48 PoE.
- Ranking 5: AMD Ryzen 5 7600X.

Son seis filas. Si el enunciado exige exactamente cinco, hay que definir un criterio de desempate. Las opciones son:

1. Ordenar por ingresos y luego por unidades vendidas.
2. Ordenar por ingresos y luego por código de producto.
3. Usar `ROW_NUMBER()` en lugar de `DENSE_RANK()`.

Cada opción produce un quinto producto distinto, por lo que la decisión debe quedar documentada. En este manual se respeta el empate y se muestran las seis filas.

### 7.5 Inventario y reglas de reposición

La vista `v_bi_inventario` clasifica cada producto así:

- **Bajo:** `existencias < stock_minimo` y existe una regla de reposición.
- **Normal:** `existencias >= stock_minimo` y existe una regla de reposición.
- **Sin regla:** no existe una regla de reposición (`stock_minimo = 0`).

Al corte hay **4 productos en Bajo**, **0 en Normal** y **17 Sin regla**. El hecho de que no haya productos en Normal no significa que el inventario esté mal: los 17 productos sin regla no se clasifican como Normal porque no tienen mínimo. Si se definen puntos de reorden para ellos, la distribución cambiará.

La tabla de alertas está filtrada a Bajo. Para ver los productos sin regla, usar el segmentador de estado en las tarjetas y gráficos, o consultar la vista directamente; la tabla de alertas permanece fija en Bajo.

### 7.6 Consultas de control

Las consultas del Anexo B permiten reproducir todos los totales de este manual. Se ejecutan con:

```powershell
docker compose exec -T -e PGPASSWORD=bi_reader_techcore db psql -U bi_reader -d TechCore_DB
```

Si se ejecutan desde un cliente gráfico, usar los mismos parámetros de conexión de la sección 2.4.

---

## 8. Problemas frecuentes y solución

### 8.1 Power BI no conecta a PostgreSQL

**Síntoma:** error de conexión rechazada o tiempo de espera agotado en `localhost:5432`.

**Causa:** el contenedor de PostgreSQL no está levantado, el puerto está ocupado o el servicio no terminó de restaurar.

**Solución:**

1. Ejecutar `docker compose ps` y confirmar que `techcore_postgres_db` está `Up (healthy)`.
2. Si no está levantado, ejecutar `.\start.ps1` de nuevo.
3. Revisar los logs con `docker compose logs -f db`.
4. Comprobar el puerto con `Test-NetConnection localhost -Port 5432`.
5. Si hay un PostgreSQL local ocupando el puerto, detenerlo o cambiar el mapeo de puertos.

### 8.2 Error del proveedor Npgsql

**Síntoma:** `The provider 'Npgsql' is not registered`.

**Causa:** la versión de Power BI Desktop no incluye el proveedor o no lo encuentra en la GAC.

**Solución:** instalar Npgsql 4.1.x con la opción **Npgsql GAC Installation**, reiniciar Power BI y volver a intentar. En versiones recientes el conector ya está incluido.

### 8.3 Error de autenticación con `bi_reader`

**Síntoma:** `password authentication failed for user "bi_reader"` o el usuario no existe.

**Causa:** la contraseña es incorrecta, el rol no se creó o la base fue recreada sin aplicar `vistas_bi.sql`.

**Solución:**

1. Verificar la contraseña `bi_reader_techcore`.
2. Entrar al contenedor y comprobar el rol:
   ```powershell
   docker compose exec -T db psql -U odoo -d TechCore_DB -c "\du bi_reader"
   ```
3. Si el rol no existe, aplicar el script `db-init/sql/vistas_bi.sql`.
4. Si la base fue recreada, esperar a que termine la restauración y volver a aplicar el script.

### 8.4 Error de SSL o cifrado

**Síntoma:** Power BI pide cifrado o muestra un error de SSL al conectar.

**Causa:** la conexión local no tiene SSL configurado y Power BI intenta usarlo.

**Solución:** en la ventana de conexión, desmarcar **Usar SSL** o seleccionar **Sin cifrado**. La conexión es local y el contenedor no exige SSL.

### 8.5 Las vistas no aparecen en el Navegador

**Síntoma:** el esquema `public` no muestra las vistas `v_bi_*`.

**Causa:** el script `vistas_bi.sql` no se aplicó, el usuario no tiene permisos o la restauración aún no terminó.

**Solución:**

1. Verificar que la base esté restaurada.
2. Ejecutar `db-init/sql/vistas_bi.sql` con el usuario administrador.
3. Confirmar los permisos de `bi_reader` con `\dp public.v_bi_*`.
4. Refrescar el Navegador de Power BI.

### 8.6 El reporte se ve vacío o con filtros inesperados

**Síntoma:** las tarjetas muestran cero o los gráficos no tienen datos.

**Causa:** un segmentador con una selección vacía, una relación inactiva, un filtro de página o un rango de fechas fuera del periodo.

**Solución:**

1. Limpiar todos los filtros y segmentadores.
2. Revisar el panel **Filtros** en los niveles de visual, página y reporte.
3. Confirmar que la relación `DimFecha[fecha]` con `FactVentas[fecha]` está activa.
4. Verificar que el rango de fechas incluya julio a octubre de 2026.
5. Actualizar el reporte.

### 8.7 El gráfico de top 5 muestra productos que no son los de mayor volumen

**Síntoma:** el gráfico **Top Unidades por producto** muestra cinco productos, pero no coinciden con el ranking de la tabla 6.6 (Samsung 990 PRO, Corsair Vengeance, ASUS ROG Maximus, AMD Ryzen 9 y Kingston Fury Beast).

**Causa:** el filtro Top N del visual está configurado sobre `TopProductos[producto]` y ordena por **conteo** de producto. Como `TopProductos` tiene una fila por producto, el conteo es 1 para todos y la selección de los cinco es arbitraria.

**Solución:**

1. Seleccionar el visual **Top Unidades por producto**.
2. En el panel **Filtros**, eliminar el filtro Top N sobre `TopProductos[producto]`.
3. Agregar un filtro sobre `DimProducto[producto]`, de tipo **Top N**.
4. Configurar **Mostrar los 5 primeros** y ordenar por la medida `[Unidades Vendidas]`.
5. Confirmar que el eje Y sea `[Unidades Vendidas]` y que el orden sea descendente.
6. Actualizar el reporte y volver a capturar la página de Ventas.

Si se quiere un orden determinista entre los productos empatados en 17 unidades, agregar un criterio secundario (por ejemplo, ingresos o código) o usar una medida de ranking con desempate.

### 8.8 El pastel de categorías no coincide con la tabla

**Síntoma:** las categorías del pastel no suman el total o los porcentajes no coinciden con la tabla 6.8.

**Causa:** la leyenda usa `TopProductos[categoria]` en lugar de `DimProducto[categoria]`. Si la relación entre `TopProductos` y `DimProducto` no está activa o no filtra correctamente, el pastel puede mostrar valores inconsistentes.

**Solución:**

1. Cambiar la leyenda del pastel a `DimProducto[categoria]`.
2. Mantener `[Ventas Totales]` como valor.
3. Confirmar que la relación `DimProducto[codigo_producto]` con `FactVentas[codigo_producto]` esté activa y con filtro único.
4. Actualizar el reporte.

### 8.9 La tarjeta de ventas no coincide con Odoo

**Síntoma:** Power BI muestra Q 62,946.36 y Odoo Q 70,500.00.

**Causa:** la tarjeta usa el subtotal sin IVA; Odoo muestra el total con impuestos.

**Solución:** comparar el subtotal de Odoo con la tarjeta y el total con IVA por separado. Si se necesita el total facturado, agregar la medida `Ventas con IVA` o los campos `amount_total` y `amount_tax` a la vista. No cambiar la tarjeta de ventas netas sin actualizar la validación y las capturas.

### 8.10 La tabla de stock bajo está vacía

**Síntoma:** la tabla no muestra filas.

**Causa:** no hay productos con `estado_stock = "Bajo"` o el filtro del visual no encuentra coincidencias.

**Solución:**

1. Consultar `SELECT * FROM v_bi_inventario WHERE estado_stock = 'Bajo';`.
2. Verificar que las reglas de reposición existan y que las existencias estén por debajo del mínimo.
3. Revisar el filtro de nivel de visual de la tabla.
4. Si se quiere ver todos los estados, quitar el filtro de la tabla o usar una copia sin filtro.

### 8.11 La tarjeta "Productos Sin Regla" muestra 17

**Síntoma:** la tarjeta muestra 17 y parece un error.

**Causa:** solo cuatro productos tienen regla de reposición; los otros 17 no tienen mínimo y se clasifican como `Sin regla`.

**Solución:** no es un error. Es una oportunidad de mejora: definir puntos de reorden para los 17 productos restantes, priorizando los de mayor rotación.

### 8.12 El top 5 por ingresos muestra seis filas

**Síntoma:** el filtro `ranking <= 5` devuelve seis productos.

**Causa:** el ranking usa `DENSE_RANK()` y hay un empate en el segundo puesto.

**Solución:** si se requieren exactamente cinco filas, definir un criterio de desempate o usar `ROW_NUMBER()`. Documentar la decisión en el reporte y en el manual.

### 8.13 Power BI muestra datos antiguos

**Síntoma:** las cifras no cambian después de una venta o de una modificación de inventario.

**Causa:** el reporte está en modo Importar y no se ha actualizado.

**Solución:** pulsar **Inicio > Actualizar**. Si la actualización falla, revisar las credenciales y la conexión. Si la base fue recreada, esperar a que termine la restauración.

### 8.14 Odoo no carga después de actualizar el repositorio

**Síntoma:** error 500, estilos rotos o tienda sin imágenes.

**Causa:** los assets del frontend quedaron modificados o incompletos después de un `git pull` o de una restauración.

**Solución:**

1. Identificar los archivos modificados sin tocar el filestore:
   ```powershell
   git status --short
   ```
2. Restaurar únicamente los assets del frontend que aparezcan modificados, por ejemplo los archivos `.css` y `.js` de la carpeta de estáticos:
   ```powershell
   git checkout -- <ruta-de-los-assets-modificados>
   ```
3. Reiniciar el contenedor web:
   ```powershell
   docker compose restart web
   ```
4. Si persiste, revisar los logs con `docker compose logs -f web`.
5. No modificar ni subir `filestore/`, `dump.sql.gz` ni los archivos de respaldo.

### 8.15 PowerShell bloquea `start.ps1`

**Síntoma:** `No se puede cargar el archivo start.ps1 porque la ejecución de scripts está deshabilitada`.

**Causa:** la política de ejecución de PowerShell.

**Solución:** ejecutar con:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

O cambiar la política solo para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

### 8.16 El puerto 8069 está ocupado

**Síntoma:** el contenedor web no levanta o Docker muestra un error de puerto en uso.

**Causa:** otro servicio está usando el puerto 8069.

**Solución:** detener el servicio conflictivo o cambiar el mapeo de puertos en `docker-compose.yml`. Si se cambia el puerto, actualizar la URL de Odoo en la documentación.

---

## 9. Conclusiones y decisiones de negocio

### 9.1 Conclusiones de inventario

1. **El inventario total es de 1,219 unidades y Q 242,960.00.** La mayor parte del valor está en procesadores (Q 90,440.00), memoria RAM (Q 28,320.00) y servidores (Q 28,200.00).
2. **Hay cuatro productos en stock bajo:** Dell PowerEdge R750 (2/5), HPE ProLiant DL380 Gen10 (3/5), Lenovo ThinkSystem SR650 (4/5) y Cisco Catalyst 2960-X 24 Port (5/10).
3. **Los cuatro productos críticos suman 14 unidades y Q 31,200.00**, el 12.84 % del valor del inventario. Para llevarlos al mínimo se necesitan 11 unidades y Q 22,800.00.
4. **No hay mercancía en tránsito:** `cantidad_por_recibir = 0` en todos los productos. La reposición debe iniciarse.
5. **Diecisiete productos no tienen regla de reposición.** La alerta de stock bajo no los cubre; entre ellos hay productos de alta rotación.

### 9.2 Conclusiones de ventas

1. **Se vendieron 77 órdenes, 221 unidades y Q 62,946.36 netos** entre el 13 de julio y el 6 de octubre de 2026. Con IVA, el total es Q 70,500.00.
2. **El ticket promedio es Q 817.49.** El canal Web concentra el 67.79 % de los ingresos y el segmento B2C el 49.22 %.
3. **Agosto y septiembre son los meses más fuertes**, con Q 21,553.53 y Q 21,392.85. Octubre es parcial y no debe compararse con meses completos.
4. **Procesador, Tarjeta Madre y SSD explican el 75.48 % de los ingresos.** El Intel Core i9-13900K lidera por ingresos (Q 9,285.72) y el Samsung 990 PRO por unidades (36).
5. **El top 5 por ingresos (seis filas por empate) representa el 69.22 % de las ventas.** El top 5 por unidades representa el 47.51 % de las unidades y el 44.43 % de los ingresos.
6. **La semana 32 es la de mayor venta** (Q 7,571.41); la 34, la de menor venta entre las semanas completas (Q 3,250.00).

### 9.3 Decisiones recomendadas

| Decisión | Evidencia | Acción |
|---|---|---|
| Reponer los cuatro productos críticos | 4 productos en Bajo, 0 unidades por recibir | Emitir orden de compra por al menos 11 unidades (Q 22,800.00) y definir stock de seguridad. |
| Completar las reglas de reposición | 17 productos Sin regla | Crear `stock.warehouse.orderpoint` para los 17, priorizando Samsung 990 PRO, Corsair Vengeance y TP-Link. |
| Asegurar stock de los productos líderes | Samsung 990 PRO (36 unidades) y Corsair Vengeance (18) | Revisar existencias y planificar compras antes de campañas. |
| Impulsar los productos de alto ingreso | Intel Core i9, Ryzen 9 y ASUS ROG | Mantener disponibilidad y destacarlos en el canal Web y en cotizaciones B2B. |
| Reforzar el canal Web y el B2C | Web 67.79 %; B2C 49.22 % | Invertir en la tienda, campañas digitales y conversión del checkout. |
| Analizar la brecha B2B Web vs. Cotización | Web B2B 25.96 %; Cotización B2B 24.82 % | Revisar precios, condiciones, tamaño de cotización y seguimiento; Cotización B2B tiene el ticket promedio más bajo (Q 679.35). |
| Planificar con el calendario semanal | 13 semanas, pico en S32 | Usar la serie semanal para programar inventario y promociones. |

---

# [VIDEO 2 - Reportes de Inventario y Ventas en Power BI](https://drive.google.com/file/d/1drsu8TdcWIfKtujYJ5SY-BxojB4REDNY/view?usp=sharing)


---

## Anexos

### Anexo A. Estructura de archivos

```text
Proyecto/Fase3/
├── bi/
│   └── Reportes_TechCore.pbix
├── docu/
│   ├── manual_bi_francisco.md
│   └── capturas/
│       ├── francisco_f3_01_seleccion_vistas.png
│       ├── francisco_f3_02_dashboard_inventario.png
│       └── francisco_f3_03_dashboard_ventas.png
├── TAREAS_FRANCISCO.md
└── PLAN_FASE3_COMPLETO.md

Proyecto/techcore-odoo/
└── db-init/sql/vistas_bi.sql
```

### Anexo B. Consultas SQL de validación

```sql
-- 1. Totales de ventas
SELECT
    COUNT(DISTINCT orden) AS ordenes,
    COUNT(*) AS lineas,
    SUM(cantidad) AS unidades,
    ROUND(SUM(subtotal)::numeric, 2) AS ventas_netas,
    MIN(fecha) AS desde,
    MAX(fecha) AS hasta
FROM v_bi_ventas_detalle
WHERE estado IN ('sale', 'done');

-- 2. Ventas por canal y segmento
SELECT
    canal,
    segmento,
    COUNT(DISTINCT orden) AS ordenes,
    ROUND(SUM(subtotal)::numeric, 2) AS ventas
FROM v_bi_ventas_detalle
WHERE estado IN ('sale', 'done')
GROUP BY canal, segmento
ORDER BY ventas DESC;

-- 3. Ventas por mes
SELECT
    anio,
    mes,
    COUNT(DISTINCT orden) AS ordenes,
    ROUND(SUM(subtotal)::numeric, 2) AS ventas
FROM v_bi_ventas_detalle
WHERE estado IN ('sale', 'done')
GROUP BY anio, mes
ORDER BY anio, mes;

-- 4. Ventas por semana ISO
SELECT
    anio,
    semana,
    COUNT(DISTINCT orden) AS ordenes,
    ROUND(SUM(subtotal)::numeric, 2) AS ventas
FROM v_bi_ventas_detalle
WHERE estado IN ('sale', 'done')
GROUP BY anio, semana
ORDER BY anio, semana;

-- 5. Resumen de inventario
SELECT
    COUNT(*) AS productos,
    SUM(existencias) AS unidades,
    ROUND(SUM(valor_inventario)::numeric, 2) AS valor,
    COUNT(*) FILTER (WHERE estado_stock = 'Bajo') AS bajo,
    COUNT(*) FILTER (WHERE estado_stock = 'Normal') AS normal,
    COUNT(*) FILTER (WHERE estado_stock = 'Sin regla') AS sin_regla
FROM v_bi_inventario;

-- 6. Productos en stock bajo
SELECT
    codigo_producto,
    producto,
    categoria,
    existencias,
    stock_minimo,
    cantidad_por_recibir,
    costo,
    ROUND((existencias * costo)::numeric, 2) AS valor
FROM v_bi_inventario
WHERE estado_stock = 'Bajo'
ORDER BY existencias;

-- 7. Ranking de productos
SELECT
    codigo_producto,
    producto,
    unidades_vendidas,
    ROUND(ingresos::numeric, 2) AS ingresos,
    ranking
FROM v_bi_top_productos
ORDER BY ranking, unidades_vendidas DESC;

-- 8. Resumen de compras
SELECT
    COUNT(DISTINCT orden) AS ordenes,
    COUNT(*) AS lineas,
    ROUND(SUM(subtotal)::numeric, 2) AS total
FROM v_bi_compras;

-- 9. Compras por estado
SELECT
    estado,
    COUNT(DISTINCT orden) AS ordenes,
    COUNT(*) AS lineas,
    ROUND(SUM(subtotal)::numeric, 2) AS total
FROM v_bi_compras
GROUP BY estado
ORDER BY estado;
```

### Anexo C. Credenciales y parámetros del reporte

| Parámetro | Valor |
|---|---|
| Archivo del reporte | `Proyecto/Fase3/bi/Reportes_TechCore.pbix` |
| Servidor PostgreSQL | `localhost:5432` |
| Base de datos | `TechCore_DB` |
| Usuario | `bi_reader` |
| Contraseña | `bi_reader_techcore` |
| Modo | Importar |
| Páginas | `Inventario`, `Ventas` |
| Tamaño de página | 1920 x 1080 |
| Tema | `ReportThemeDark` |
| Vistas | `v_bi_ventas_detalle`, `v_bi_inventario`, `v_bi_top_productos`, `v_bi_compras` |

### Anexo D. Inventario completo al 22/10/2026

| Código | Producto | Categoría | Existencias | Mínimo | Estado |
|---|---|---|---:|---:|---|
| PROD-001 | Intel Core i9-13900K | Procesador | 74 | 0 | Sin regla |
| PROD-002 | AMD Ryzen 9 7950X | Procesador | 48 | 0 | Sin regla |
| PROD-003 | Corsair Vengeance 32GB DDR5 | Memoria RAM | 152 | 0 | Sin regla |
| PROD-004 | Kingston Fury Beast 16GB DDR4 | Memoria RAM | 193 | 0 | Sin regla |
| PROD-005 | Samsung 990 PRO 2TB NVMe | SSD | 79 | 0 | Sin regla |
| PROD-006 | WD Black SN850X 1TB NVMe | SSD | 100 | 0 | Sin regla |
| PROD-007 | Cisco Catalyst 2960-X 24 Port | Switch | 5 | 10 | Bajo |
| PROD-008 | Ubiquiti UniFi Switch 48 PoE | Switch | 18 | 0 | Sin regla |
| PROD-009 | Dell PowerEdge R750 | Servidor | 2 | 5 | Bajo |
| PROD-010 | HPE ProLiant DL380 Gen10 | Servidor | 3 | 5 | Bajo |
| PROD-011 | ASUS ROG Maximus Z790 Hero | Tarjeta Madre | 28 | 0 | Sin regla |
| PROD-012 | MSI MAG B650 Tomahawk WiFi | Tarjeta Madre | 36 | 0 | Sin regla |
| PROD-013 | Intel Core i5-13600K | Procesador | 82 | 0 | Sin regla |
| PROD-014 | AMD Ryzen 5 7600X | Procesador | 45 | 0 | Sin regla |
| PROD-015 | G.Skill Trident Z5 RGB 64GB | Memoria RAM | 27 | 0 | Sin regla |
| PROD-016 | Crucial P3 Plus 4TB NVMe | SSD | 38 | 0 | Sin regla |
| PROD-017 | TP-Link TL-SG108E 8 Port | Switch | 148 | 0 | Sin regla |
| PROD-018 | Lenovo ThinkSystem SR650 | Servidor | 4 | 5 | Bajo |
| PROD-019 | Gigabyte X670E AORUS Master | Tarjeta Madre | 21 | 0 | Sin regla |
| PROD-020 | Seagate IronWolf Pro 18TB | Disco Duro | 66 | 0 | Sin regla |
| PROD-021 | Logitech MX Keys | Periféricos | 50 | 0 | Sin regla |
| **Total** |  |  | **1,219** |  | **4 Bajo / 17 Sin regla** |

`cantidad_por_recibir = 0` en los 21 productos al corte del 22/10/2026.

---

**Fin del manual.**
