# Manual Técnico de Cadena de Suministro, Compras y Cotizaciones

**Universidad San Carlos de Guatemala**  
**Facultad de Ingeniería**  
**Escuela de Ciencias y Sistemas**  
**Sistemas Organizacionales y Gerenciales 1 (SOG1) - Sección A**  
**Segundo Semestre 2026**

**Empresa:** TechCore Solutions Guatemala  
**Integrante:** Francisco Gerardo Castillo Sagastume  
**Carnet:** 202300653  
**Rol:** Cadena de Suministro y Cotizaciones  
**Fase Evaluada:** Fase 2 - Configuración, Desarrollo de Módulos y Operación Base

---

## 1. Introducción y Alcance Técnico

El presente manual documenta paso a paso, con capturas de pantalla, la configuración de la cadena de suministro y el proceso transaccional de cotizaciones en **Odoo 17.0 Community Edition** para **TechCore Solutions Guatemala**. Las áreas cubiertas corresponden a:

1. **Punto 12.2: Administración de Almacén y Compras a Proveedores.** Reglas de stock mínimo (puntos de reorden) y ejecución del ciclo completo de compras: Solicitud de Cotización, Orden de Compra y Recepción de mercancía.
2. **Punto 12.3: Implementación del Módulo Avanzado de Compras y Cotizaciones a Clientes.** Configuración del acuerdo marco (requisición), comparación multi-proveedor y conversión de cotización en pedido de venta.

Acceso al sistema: `http://localhost:8069`, base de datos `TechCore_DB`, usuario `admin@techcore.gt`. La moneda de la compañía es el quetzal (Q).

### 1.1 Nota sobre el módulo de requisición

El enunciado del proyecto solicita el ciclo **Requisición → Solicitud de Cotización → Orden de Compra → Recepción de Mercancía**. En **Odoo 17 Community Edition** el modelo `purchase.requisition` no incorpora la requisición de libre forma disponible en versiones anteriores: el único tipo de registro que trae el módulo es **Blanket Order**, cuyo campo *Vendor* es obligatorio y por tanto admite un único proveedor. El flujo multi-proveedor se implementa mediante la pestaña **Alternatives** de la Solicitud de Cotización, que genera RFQ alternativas y permite compararlas con **Compare Product Lines**.

Por lo tanto se configuraron **ambos mecanismos**: el acuerdo marco Blanket Order (concepto de requisición) y la comparación de tres proveedores mediante alternativas. La justificación técnica detallado se desarrolla en la sección 7.

---

## 2. Configuración Inicial Requerida

### 2.1 Módulo de Requisiciones de Compra

El flujo de alternativas requiere el módulo `purchase_requisition_stock`, que instala también sus dependencias `purchase_requisition` y `purchase_requisition_sale`.

Para verificar su instalación: **Apps → filtrar por "Purchase Requisition"**. El estado de los tres módulos quedó como `installed`, y por lo tanto existen los modelos `Purchase Requisition` y `Purchase Requisition Line`.

> El menú **Blanket Orders** aparece en `Purchase → Orders` una vez instalado el módulo. No existe un menú titulado "Requisitions".

### 2.2 Menú de Ventas

El menú raíz de la aplicación de Ventas (`ir.ui.menu` identificador XML `sale.sale_menu_root`) debe estar activo. Si está archivado, los submenús **Quotations** y **Orders** existen pero no se muestran porque Odoo no renderiza los hijos de un menú archivado.

Para reactivarlo desde la interfaz: **Settings → Technical → Database Structure → Menu Items**, buscar "Sales" y marcar **Active**.

Además, el usuario debe ser de tipo **Internal User**. Los usuarios de tipo portal (`share = True`) no tienen acceso a menús internos por diseño de Odoo, ya que están destinados a clientes que operan el portal del sitio web, no al back-office de la empresa.

### 2.3 Catálogo de Proveedores por Producto

**Este paso es prerequisite de la comparación de cotizaciones.** Cuando se crea una RFQ alternativa, Odoo toma el precio del producto desde el catálogo de proveedores (`product.supplierinfo`). Si un producto tiene un solo proveedor registrado, las alternativas caen al *Standard Cost* del producto y **todas las RFQ muestran el mismo precio**, con lo cual la tabla comparativa no aporta evidencia de comparación.

Se configuraron tres proveedores en la pestaña **Purchasing** de los productos involved:

| Producto | Ingram Micro Guatemala | Intcomex | PC Mayorista |
|---|---|---|---|
| PROD-009 Dell PowerEdge R750 | Q 3,600.00 | Q 3,500.00 | Q 3,125.00 |
| PROD-010 HPE ProLiant DL380 Gen10 | Q 3,350.00 | Q 3,200.00 | Q 2,857.14 |
| PROD-018 Lenovo ThinkSystem SR650 | — | Q 2,900.00 | Q 2,589.29 |
| PROD-007 Cisco Catalyst 2960-X | Q 520.00 | Q 600.00 | Q 535.71 |

Procedimiento: `Inventory → Products → [producto] → pestaña Purchasing → Vendors → Add`, indicando *Vendor*, *Price* y *Minimum Quantity*.

---

## 3. Punto 12.2: Administración en Almacén

### 3.1 Ruta de acceso

El menú de reglas de reposición se encuentra en:

**Inventory → Configuration → Products → Reordering Rules**

Alternativamente, desde cualquier producto: botón **On Hand** → pestaña *Replenishment* → **New**.

### 3.2 Reglas de stock mínimo configuradas

Se configuraron cuatro reglas sobre los productos con existencias más bajas del catálogo, con el fin de que la reposición se dispare de forma automática.

![Figura 1: Lista de Reordering Rules con las cuatro reglas configuradas](capturas/francisco_01_lista_reordering_rules.png)

| Producto | Stock inicial | Trigger | Min Quantity | Max Quantity | Ubicación |
|---|---|---|---|---|---|
| PROD-009 Dell PowerEdge R750 | 2 | Order Point | 5 | 10 | WH/Stock |
| PROD-010 HPE ProLiant DL380 Gen10 | 3 | Order Point | 5 | 10 | WH/Stock |
| PROD-018 Lenovo ThinkSystem SR650 | 4 | Order Point | 5 | 10 | WH/Stock |
| PROD-007 Cisco Catalyst 2960-X | 5 | Order Point | 10 | 25 | WH/Stock |

Campos del formulario:

| Campo | Valor | Descripción |
|---|---|---|
| Product | Producto a reponer | Se elige del catálogo |
| Location | `WH/Stock` | Almacén físico principal |
| Trigger | `Auto` | Compara contra el umbral mínimo inmediato |
| Min Quantity | 5 / 10 | Umbral que dispara la reposición |
| Max Quantity | 10 / 25 | Cantidad a la que se repone el stock |
| Days To Order | 3 | Días de anticipación de compra |

### 3.3 Generación automática de la orden de compra

Las reglas configuradas disparan la creación automática de solicitudes de compra. Al situarse el stock por debajo del mínimo, el sistema calcula la cantidad a ordenar en la columna **To Order**.

| Producto | On Hand | Min | Max | To Order |
|---|---|---|---|---|
| PROD-009 Dell PowerEdge R750 | 2.00 | 5.00 | 10.00 | 8.00 |
| PROD-010 HPE ProLiant DL380 Gen10 | 3.00 | 5.00 | 10.00 | 7.00 |
| PROD-018 Lenovo ThinkSystem SR650 | 4.00 | 5.00 | 10.00 | 6.00 |
| PROD-007 Cisco Catalyst 2960-X | 5.00 | 10.00 | 25.00 | 20.00 |

Para ejecutar la reposición: botón **Order Once** en la fila correspondiente. Esta acción invoca el motor de aprovisionamiento, que crea la RFQ y la asocia a su regla de origen mediante el campo `orderpoint_id` de la línea de compra.

**Este mecanismo es la evidencia del KPI "Operaciones/Logística 1"** definido en la Fase 1: *tiempo transcurrido desde la creación de la Orden de Compra automatizada hasta la recepción del hardware por parte de los proveedores*. Las órdenes no se crearon manualmente, sino que el sistema las generó al detectar el cruce del umbral.

---

## 4. Punto 12.2: Ciclo de Compras Completo

### 4.1 Solicitud de Cotización generada

Al ejecutar **Order Once**, el sistema generó las solicitudes de compra. El proveedor destino se determina a partir del catálogo: `PROD-009`, `PROD-010`, `PROD-018` y `PROD-007` tienen a **Intcomex** como proveedor registrado, por lo que el motor de aprovisionamiento agrupa las cuatro líneas en una sola RFQ.

![Figura 6: RFQ autogenerada con las cuatro líneas de producto](capturas/francisco_02_rfq_autogenerada.png)

Se accederió a `Purchase → Orders → Requests for Quotation` para localizar los documentos generados.

### 4.2 RFQ alternativas multi-proveedor

Con la RFQ base abierta, en la pestaña **Alternatives** se EJECUTÓ el botón **Create Alternative**, que abre un asistente donde se selecciona el proveedor de la RFQ alternativa y opcionalmente *Copy Products*.

![Figura 3: Asistente Create Alternative con la selección de proveedor](capturas/francisco_03_asistente_alternativa.png)

Se crearon dos alternativas:

| Documento | Proveedor | Estado | Líneas |
|---|---|---|---|
| P00001 | Intcomex | Cancelada | 4 |
| P00002 | Ingram Micro Guatemala | Cancelada | 4 |
| P00003 | PC Mayorista | Purchase Order | 4 con cantidad |

Las tres RFQ quedaron enlazadas en un mismo grupo (`purchase.order.group`), lo que Odoo denomina "call for tender" o licitación.

![Figura 4: Pestaña Alternatives con las RFQ alternativas enlazadas](capturas/francisco_04_pestana_alternatives.png)

### 4.3 Comparación de cotizaciones

Con las alternativas creadas, el botón **Compare Product Lines** genera una vista comparativa agrupada por producto que muestra precio, subtotal y fecha de entrega de cada proveedor.

![Figura 5: Tabla Compare Product Lines con los precios de los tres proveedores](capturas/francisco_05_comparacion_proveedores.png)


### 4.4 Confirmación de la Orden de Compra

La RFQ seleccionada se confirmó con el botón **Confirm Order**, que la convirtió en Orden de Compra en estado `Purchase Order` y creó automáticamente el picking de recepción.

![Figura 6: Orden de Compra P00003 en estado Purchase Order](capturas/francisco_06_oc_confirmada.png)

| Documento | Proveedor | Estado | Líneas | Importe |
|---|---|---|---|---|
| P00003 | PC Mayorista | Purchase Order | 4 | Q 66,428.52 |

| Producto | Cantidad | Precio Unitario | Subtotal |
|---|---|---|---|
| PROD-009 Dell PowerEdge R750 | 8.00 | Q 2,790.18 | Q 19,929.86 |
| PROD-010 HPE ProLiant DL380 Gen10 | 7.00 | Q 2,551.02 | Q 15,943.88 |
| PROD-018 Lenovo ThinkSystem SR650 | 6.00 | Q 2,589.29 | Q 13,871.20 |
| PROD-007 Cisco Catalyst 2960-X | 20.00 | Q 535.71 | Q 9,566.25 |
| **Total** | | | **Q 66,428.52** |

El picking asociado quedó registrado como **WH/IN/00001** (tipo *Receipt*).

### 4.5 Recepción de mercancía

Se Republicó el picking **WH/IN/00001** y se validó con el botón **Validate**.


### 4.6 Validación del aumento de stock

**Este es el punto de verificación exigido por la tarea: "Validar que el stock aumentó".**

`Inventory → Products → [producto]` → botón **On Hand**

![Figura 7: Existencias del Dell PowerEdge R750 antes de la recepción (2 unidades)](capturas/francisco_07_stock_antes.png)

![Figura 8: Existencias del Dell PowerEdge R750 después de la recepción (10 unidades)](capturas/francisco_08_stock_despues.png)

| Producto | Stock antes | Cantidad recibida | Stock después |
|---|---|---|---|
| PROD-009 Dell PowerEdge R750 | 2.00 | 8.00 | **10.00** |
| PROD-010 HPE ProLiant DL380 Gen10 | 3.00 | 7.00 | **10.00** |
| PROD-018 Lenovo ThinkSystem SR650 | 4.00 | 6.00 | **10.00** |
| PROD-007 Cisco Catalyst 2960-X | 5.00 | 20.00 | **25.00** |

El incremento coincide exactamente con la cantidad transferida en el picking, lo que confirma la trazabilidad entre la orden de compra y el inventario.

![Figura 9: Historial de movimientos Updated con el origen P00003](capturas/francisco_09_movimientos_updated.png)

---

## 5. Punto 12.3: Blanket Order (Acuerdo Marco)

### 5.1 Configuración

`Purchase → Orders → Blanket Orders` → **New**

![Figura 10: Formulario de creación de Blanket Order](capturas/francisco_10_blanket_order_formulario.png)

| Campo | Valor |
|---|---|
| Reference | `Acuerdo anual de abastecimiento B2B - Ingram Micro Guatemala` |
| Purchase Representative | Administrator |
| Agreement Type | Blanket Order |
| Vendor | Ingram Micro Guatemala |
| Agreement Deadline | 31/12/2026 |
| Ordering Date | 01/10/2026 |
| Delivery Date | 15/10/2026 |
| Currency | GTQ |


**Advertencia importante:** el campo *Unit Price* de una Blanket Order **no se hereda** del catálogo de proveedores, a diferencia de lo que ocurre en una RFQ. Si se deja en cero, el acuerdo queda con importe total Q0.00 y el documento se muestra como inconsistente. Los precios deben escribirse manualmente.

### 5.2 Flujo de estados

`Draft` → **Confirm** → `Ongoing` → **Validate** → `Closed`

![Figura 11: Blanket Order en estado Ongoing con las cuatro líneas](capturas/francisco_11_blanket_order_detalle.png)

El documento quedó registrado como **BO00001** en estado `Ongoing`. Al alcanzar el estado *Closed*, el botón **New Quotation** permite generar una RFQ asociada al acuerdo marco, estableciendo el vínculo requisición → orden de compra.

---

## 6. Punto 12.3: Cotización a Clientes

### 6.1 Datos del cliente

Se utilizó **TechCorp S.A.**, cliente corporativo con categoría **B2B**, correo `compras@techcorp.com.gt`.

### 6.2 Creación de la cotización

`Sales → Orders → Quotations` → **New**

| Campo | Valor |
|---|---|
| Customer | TechCorp S.A. |
| Payment Terms | 30 Days (crédito) |
| Delivery | Guatemala |

### 6.3 Envío y confirmación de precio

La cotización se envió por correo con el botón **Send by email**, generando el documento PDF con las condiciones comerciales.

![Figura 12: Cotización enviada por correo con el PDF generado](capturas/francisco_12_cotizacion_enviada.png)

En el panel de chatter se utilizó la acción **Solicitar confirmación de precio**, que envía al cliente un enlace seguro para aprobar los precios propuestos. Esta acción distingue una cotización real de un pedido directo.

### 6.4 Conversión a pedido de venta

Una vez validada la confirmación, el sistema creó el **Pedido de venta** en estado `Sale`.

El picking de entrega **WH/OUT/00001** fue generado automáticamente con estado `assigned`.

---

## 7. Nota Técnica: Requisición versus Blanket Order

Esta sección documenta la decisión de diseño frente a la diferencia entre el enunciado y la funcionalidad disponible en la versión del ERP.

### 7.1 Restricción de Odoo 17 Community Edition

Al instalar el módulo `purchase_requisition_stock`, el sistema crea un único registro en el modelo `purchase.requisition.type`:

| Tipo | Exclusive | Quantity Copy | Line Copy |
|---|---|---|---|
| Blanket Order | multiple | none | copy |

El campo *Vendor* de la requisición es obligatorio cuando `quantity_copy = none`, lo que significa que cada requisición pertenece a **un solo proveedor**. El modelo, por tanto, no representa una solicitud abierta a múltiples proveedores sino un **acuerdo marco** con un proveedor determinado, del cual se derivan múltiples órdenes de compra.

### 7.2 Mecanismo de comparación multi-proveedor

La comparación de cotizaciones se implementa mediante el campo `alternative_po_ids` del modelo `purchase.order`, definido en la vista *Alternatives* de la RFQ. Cuando se registran alternativas, Odoo agrupa automáticamente las RFQ en un `purchase.order.group`, que representa la licitación.

### 7.3 Cobertura del ciclo solicitado

| Paso del enunciado | Implementación en Odoo 17 CE | Evidencia |
|---|---|---|
| Requisición de compra | Blanket Order (acuerdo marco) | BO00001 |
| Solicitud de Cotización | RFQ autogenerada + 2 alternativas | P00001, P00002, P00003 |
| Comparación de cotizaciones | Compare Product Lines | Tabla de tres proveedores |
| Orden de Compra | Confirm Order sobre la RFQ ganadora | P00003 (Q 66,428.52) |
| Recepción de mercancía | Receipt + Validate | WH/IN/00001 |

**Conclusión:** los cinco pasos del ciclo solicitado por el enunciado están implementados y demostrados, utilizando el mecanismo multi-proveedor propio de la versión 17 del ERP.

---

## 8. Problemas Frecuentes y Solución

| Problema | Causa | Solución |
|---|---|---|
| El menú **Ventas** no aparece | El menú raíz `sale.sale_menu_root` quedó archivado (`active = False`) en el respaldo original de la base | `Settings → Technical → Database Structure → Menu Items` → buscar "Sales" → **Active** |
| El menú **Ventas** no aparece aunque esté activo | El usuario es de tipo **portal** (`share = True`); los portales no acceden a menús internos | `Settings → Users & Companies → Users` → Edit → *User Type* → **Internal User** |
| Las RFQ alternativas muestran el mismo precio | El producto solo tiene un proveedor en su pestaña *Purchasing*; Odoo cae al *Standard Cost* | Registrar los proveedores alternos con sus precios en `product.supplierinfo` |
| No existe un menú "Requisitions" | Odoo 17 CE nombra el menú `Blanket Orders` dentro de `Purchase → Orders` | Navegar a `Purchase → Orders → Blanket Orders` |
| La Blanket Order muestra importe Q0.00 | El campo *Unit Price* no se hereda del catálogo, a diferencia de la RFQ | Escribir los precios manualmente en cada línea |
| No se generó ninguna orden de compra | Las reglas de reposición no ejecutan solas; el cron diario no está activo en el entorno | Pulsar **Order Once** en la lista de Reordering Rules |
| La aplicación no refleja los cambios de menú | El contenedor web conserva la caché de menús en memoria | `docker compose restart web` |

---

## 9. Medición de Logros y Resultados

Se validan los indicadores definidos en la Fase 1 y los criterios de la rúbrica de Fase 2.

### 9.1 KPI Operaciones/Logística 1

**Indicador:** tiempo transcurrido desde la creación de la Orden de Compra automatizada hasta la recepción del hardware por parte de los proveedores.

| Hito | Registro en el sistema | Fecha y hora |
|---|---|---|
| Creación de la OC automatizada | P00003 | 04/10/2026 12:00:00 |
| Validación de la recepción | WH/IN/00001 | 04/10/2026 21:53:42 |
| **Tiempo de ciclo** | | **9 horas 53 minutos** |

El intervalo es consistente con la condición de pago de PC Mayorista (contado) y con la configuración de anticipación de compra.

### 9.2 KPI Ventas/Clientes 1

**Indicador:** tasa de conversión de solicitudes de cotización corporativa B2B a ventas efectivamente facturadas.

Se generó una cotización B2B (TechCorp S.A.) que se convirtió en pedido de venta confirmado por Q 12,880.00. La tasa de conversión observada en esta fase es de **1 cotización sobre 1 generada = 100%**, correspondiente a una muestra de un solo caso.

### 9.3 Validación del criterio 2.2 de la rúbrica

**Criterio:** *"Se configura y demuestra el flujo completo de compras y cotizaciones."*

| Componente | Estado | Evidencia |
|---|---|---|
| Puntos de reorden configurados | Completo | 4 reglas activas en WH/Stock |
| Generación automática de OC | Completo | RFQ creada por el motor de aprovisionamiento |
| Comparación multi-proveedor | Completo | 3 RFQ en un mismo grupo, tabla comparativa |
| Selección de mejor combinación | Completo | 2 RFQ canceladas, 1 confirmada |
| Recepción validada | Completo | WH/IN/00001, 41 unidades transferidas |
| Stock verificado | Completo | 4 productos con incremento exacto |
| Requisición / acuerdo marco | Completo | BO00001 con 4 líneas |
| Cotización a cliente | Completo | S00001, Q 12,880.00, crédito 30 días |
| Conversión a pedido | Completo | Estado Sale |

---

**Fin del manual técnico.**