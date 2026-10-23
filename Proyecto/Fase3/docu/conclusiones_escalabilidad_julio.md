# Conclusiones, Medición de Logros y Escalabilidad

**Universidad de San Carlos de Guatemala**
**Facultad de Ingeniería, Escuela de Ciencias y Sistemas**
**Sistemas Organizacionales y Gerenciales 1, Sección A, Segundo Semestre 2026**
**Grupo No. 7, TechCore Solutions Guatemala**

**Integrante:** Julio Alfredo Herrera Orantes
**Carnet:** 202300850
**Proyecto:** Transformación Digital en E-Commerce con ERP, CRM y BI (QuetzalDev)

---

## 1. Medición de logros frente a los objetivos SMART de la Fase 1

Las pruebas de referencia están en `pruebas_e2e_julio.md` (casos CP-01 a CP-09, ejecutados sobre el Odoo local con la base `TechCore_DB`).

| Objetivo SMART | Resultado alcanzado | Evidencia |
|---|---|---|
| **1. Integración ERP, CRM y Web con trazabilidad del 100%** | Cumplido. Cada venta hecha en la tienda quedó reflejada en el inventario (las existencias bajaron exactamente lo vendido), en la factura (con IVA del 12%), en el portal del cliente (`/my`, con descarga del PDF) y en el CRM (oportunidad `Web B2C` en la etapa Lead). Se probó con dos pedidos web (S00080 por transferencia y S00081 con Demo) y uno B2B (S00082). | CP-01 a CP-06 y matriz de trazabilidad (secciones 3 y 4 del documento de pruebas), figuras 1 a 17 |
| **2. Automatización de la cadena de suministro: carga masiva de 20 o más productos y reglas de stock** | Cumplido. Se cargaron 21 productos en 8 categorías (más 6 clientes sembrados y 4 proveedores, con 60 precios de proveedor) mediante archivos Excel, y se crearon 4 reglas de reposición en modo automático. El planificador generó solo la orden de compra P00017 (78,140.16 Q) y, al recibirla, los cuatro productos subieron a su máximo. | CP-08 (figuras 20 a 24) y manuales técnicos de la Fase 2 |
| **3. Fidelización y marketing: 2 campañas y pipeline Kanban** | Cumplido en lo esencial. El pipeline Kanban tiene 4 etapas (Lead, Contactado, Negociación y Cerrado) y las etiquetas `B2B` y `Web B2C`. Hay una campaña de marketing por correo, «Campaña Publicitaria B2B TechCore 2026», con dos correos ya enviados («Actualiza tu hardware B2B» y «Gracias por confiar en TechCore Solutions») y uno más en borrador. Es decir, se cumplen los dos envíos, pero agrupados en una sola campaña. | CP-06 (figuras 16 y 17) y módulo de Email Marketing de Odoo |

Aporte de Business Intelligence: se definieron las vistas SQL `v_bi_ventas_detalle`, `v_bi_inventario`, `v_bi_top_productos` y `v_bi_compras`, que alimentan los tableros de ventas e inventario en Power BI mediante el usuario de solo lectura `bi_reader`. Los tableros se documentan en la Parte III del manual consolidado.

## 2. Conclusiones técnicas y de negocio

1. **La trazabilidad extremo a extremo es posible con una sola plataforma.** Al usar Odoo para tienda, ventas, inventario, compras, contabilidad y CRM, un pedido web recorre todo el ciclo sin reingresar datos: del carrito a la factura y del pedido a la oportunidad. Esto elimina el trabajo duplicado de integrar sistemas separados.
2. **El pago con Demo se factura de forma automática, pero la transferencia no.** El pedido S00081 salió pagado y facturado al instante, mientras que S00080 quedó como cotización pendiente hasta que se confirmó a mano. Para el negocio esto significa una tarea diaria de conciliación bancaria que conviene automatizar.
3. **El inventario solo baja al validar la entrega.** La venta reserva la mercancía de inmediato (el pronóstico baja), pero las existencias en mano se descuentan al validar la salida. Es el comportamiento correcto para un almacén, y por eso el pronóstico es el dato adecuado para decidir compras.
4. **La reposición automática reduce el riesgo de quiebre de stock.** Con reglas de mínimo y máximo, el sistema detectó cuatro productos bajo el mínimo y generó una sola orden de compra consolidada (P00017, a Intcomex). La recepción dejó los cuatro productos en su máximo sin cálculos manuales.
5. **La automatización del CRM funciona, pero captura poca información.** La oportunidad `Web B2C` se crea sola, aunque con ingreso esperado de 0.00 Q, sin ligar el pedido y asignada a OdooBot. Con esos ajustes, el pipeline serviría para medir conversión y valor, no solo para contar contactos.
6. **La carga masiva requiere disciplina en los datos.** Las plantillas Excel, el orden de importación (categorías, productos, clientes, proveedores, inventario y precios) y el mapeo manual de la columna de producto fueron los puntos donde más errores aparecieron. Documentar el procedimiento redujo esos errores en las siguientes cargas.
7. **La experiencia de compra necesita pulirse.** La tienda muestra precios sin IVA mientras las imágenes de producto muestran precios con IVA, y la interfaz está en inglés. Para el cliente guatemalteco conviene unificar el criterio de precios y traducir la tienda.

## 3. Limitaciones actuales

- **Pago simulado:** el proveedor Demo no cobra dinero real, y la transferencia depende de una confirmación manual.
- **Un solo almacén:** no hay múltiples bodegas, rutas entre sucursales ni punto de venta físico.
- **Datos históricos de demostración:** las 75 ventas sembradas (`DEMO-SEED`) sirven para el análisis de BI, pero no reflejan operación real.
- **Evaluación en una VM local:** el sistema corre en Docker en una computadora, sin pruebas de carga, alta disponibilidad ni dominio público.
- **Facturación:** las facturas de Odoo no son facturas electrónicas FEL de la SAT.
- **Correo y envíos:** no se configuró un servidor de correo saliente ni la integración con transportistas, por lo que no se probó el envío de correos ni guías de despacho.

## 4. Propuesta de escalabilidad

| Área | Propuesta | Beneficio |
|---|---|---|
| Pagos | Pasarela de pago real con tarjeta (un proveedor local o internacional), con conciliación automática de transferencias. | Cobro inmediato y facturación automática en todos los pedidos. |
| Infraestructura | Despliegue en la nube con balanceo de carga, copias de seguridad automáticas, certificado HTTPS y dominio propio. | Disponibilidad, seguridad y recuperación ante fallos. |
| Operación | Múltiples almacenes y puntos de venta, con transferencias internas y reglas de reposición por bodega. | Crecer a varias sucursales sin perder control del stock. |
| Logística y fiscal | Integración con couriers (guías de envío) y facturación electrónica FEL de la SAT. | Cumplimiento legal y seguimiento del despacho para el cliente. |
| Business Intelligence | Actualización programada del conjunto de datos de Power BI y tableros de gerencia (ventas, margen, rotación de inventario). | Decisiones con datos al día, sin refrescar a mano. |
| CRM y marketing | Segmentación avanzada y automatización de marketing (flujos de correo por comportamiento), o evaluación de SuiteCRM o Zoho según el plan flexible del enunciado. | Mayor fidelización y mejor conversión de oportunidades. |
| Canales | Aplicación móvil y analítica de comportamiento del cliente (carritos abandonados, productos vistos). | Nuevos canales de venta y datos para campañas. |

Hoja de ruta sugerida: primero pagos y FEL (cumplimiento y cobro), luego nube y respaldos (estabilidad), después múltiples almacenes y couriers (crecimiento), y al final analítica avanzada y móvil.

## 5. Riesgos y mitigación

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Pérdida de datos por una falla del servidor local | Alto | Respaldos automáticos diarios de la base y del filestore, con prueba periódica de restauración. |
| Errores en la carga masiva de datos | Medio | Plantillas validadas, orden de importación documentado y revisión de resultados tras cada carga. |
| Quiebre de stock en productos de alta rotación | Medio | Reglas de mínimo y máximo en automático y revisión semanal de la reposición. |
| Fraude o errores en pagos reales | Alto | Pasarela certificada (PCI), confirmaciones automáticas y revisión de transacciones pendientes. |
| Incumplimiento fiscal | Alto | Implementar FEL de la SAT antes de operar con clientes reales. |
| Resistencia al cambio del personal | Medio | Capacitación con el manual de usuario y acompañamiento en las primeras semanas. |
| Dependencia de un solo equipo técnico | Medio | Documentación técnica completa y reparto de conocimiento entre integrantes. |

## 6. Conclusión general

El proyecto demostró que TechCore Solutions Guatemala puede vender, cobrar, facturar, controlar su inventario, reponerlo y dar seguimiento comercial desde una sola plataforma, con trazabilidad completa de cada venta. Las pruebas de extremo a extremo no encontraron fallos bloqueantes: lo que quedó son mejoras de proceso (facturación de transferencias, datos de la oportunidad en el CRM, precios con IVA en la tienda) que están identificadas y priorizadas. Con una pasarela de pago real, facturación FEL y un despliegue en la nube, el prototipo puede evolucionar de una demostración académica a una operación comercial.
