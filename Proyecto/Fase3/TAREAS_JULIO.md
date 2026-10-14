# Tareas de Julio: Pruebas End-to-End, Manual de Usuario, Conclusiones y Presentación

**Fase 3, Parte C.** Tú verificas que todo el ecosistema funciona de punta a punta (compra, inventario, factura, portal, CRM y reposición), documentas el uso para el cliente final y cierras el proyecto con las conclusiones, la propuesta de escalabilidad y la presentación final.

Contexto general y reglas: [PLAN_FASE3_COMPLETO.md](PLAN_FASE3_COMPLETO.md). Lee las secciones 0, 5 (hitos A2 y A4) y 9.

> Regla del proyecto: sin emojis en ningún documento, y español con tildes y eñes.

---

## 1. Qué debes entregar

| Entregable | Ruta en el repositorio |
|---|---|
| Documento de pruebas E2E con evidencia | `Proyecto/Fase3/docu/pruebas_e2e_julio.md` |
| Manual de usuario del cliente final | `Proyecto/Fase3/docu/manual_usuario_julio.md` |
| Conclusiones y escalabilidad | `Proyecto/Fase3/docu/conclusiones_escalabilidad_julio.md` |
| Presentación final | `Proyecto/Fase3/docu/presentacion_final_fase3.pptx` (o PDF) |
| Capturas | `Proyecto/Fase3/docu/capturas/julio_f3_NN_nombre.jpg` |
| Video (3 a 4 minutos) | Google Drive, enlace público; pegarlo en el documento de pruebas |

---

## 2. Qué necesitas de Jonathan antes de empezar

Puedes redactar los casos de prueba y el borrador del manual ya. Para **ejecutar** las pruebas necesitas el aviso **"e-commerce listo"** de Jonathan. Entonces tendrás:

- Un Odoo con 21 productos publicados en `/shop`, 6 clientes, 4 proveedores y reglas de reposición.
- Registro de clientes habilitado, pago por transferencia y por Demo, facturación automática y portal en `/my`.
- Una acción automática que crea una oportunidad en el CRM con la etiqueta `Web B2C` cuando entra una compra desde la web.

Levanta tu entorno con `./start.sh` en `Proyecto/Fase2/techcore-odoo/` y entra a `http://localhost:8069` (usuario `admin@techcore.gt`, contraseña `1234`). Cuando Jonathan cambie la base, haz `git pull` y vuelve a levantar.

---

## 3. Parte C1: Pruebas end-to-end

### 3.1 Formato de cada caso

Por cada caso documenta una ficha así:

```text
Caso: CP-01
Objetivo:
Precondiciones:
Pasos:
  1. ...
Resultado esperado:
Resultado real:
Estado: Aprobado o Fallido
Evidencia: capturas julio_f3_01..NN
Observaciones:
```

### 3.2 Casos obligatorios

| Caso | Flujo a probar | Qué verificar |
|---|---|---|
| CP-01 | Registro de un cliente nuevo desde `/web/signup` | La cuenta se crea, se puede iniciar sesión y entra al portal `/my` |
| CP-02 | Compra en la tienda: buscar, agregar 2 productos al carrito y pagar con **transferencia bancaria** | El pedido se crea y queda confirmado, con el total correcto (con IVA 12%) |
| CP-03 | Compra pagando con el proveedor **Demo** | El pago se registra y el pedido queda pagado |
| CP-04 | Revisar inventario después de la venta | Las existencias de los productos comprados bajaron exactamente lo vendido (`Inventory, Products` y `Moves History`) |
| CP-05 | Factura y portal | Existe la factura del pedido, está publicada, aparece en `/my` del cliente y se puede descargar en PDF |
| CP-06 | CRM | Se creó una oportunidad etiquetada `Web B2C` en la etapa Lead, ligada al cliente y al pedido |
| CP-07 | Producto sin existencias | Un producto con stock 0 muestra "agotado" y no se puede comprar |
| CP-08 | Reposición | Bajar un producto bajo su mínimo, ejecutar el aprovisionamiento (`Inventory, Operations, Replenishment, Order Once`), confirmar la orden de compra y recibir la mercancía; verificar que el stock sube |
| CP-09 (extra) | Cotización B2B | Crear una cotización para `TechCorp S.A.`, enviarla, confirmarla y facturarla; revisar que aparece en el portal del cliente B2B |

Sugerencia para CP-02, CP-03, CP-04: anota **antes** las existencias y **después** de comprar, y compáralas en una tabla.

### 3.3 Matriz de trazabilidad

Cierra el documento con una matriz que demuestre la trazabilidad del 100% (objetivo SMART de la Fase 1):

| Pedido | Cliente | Productos | Existencias antes y después | Factura | Visible en portal | Oportunidad CRM |
|---|---|---|---|---|---|---|
| S000xx | ... | ... | ... | INV/2026/xxxx | Sí | Sí, etapa Lead |

Si una prueba falla, **no la ocultes**: documenta el fallo, avisa a Jonathan con la captura y el mensaje de error, y vuelve a probar cuando lo corrija. Es mejor un fallo corregido y documentado que una prueba perfecta falsa.

### 3.4 Estructura del documento `pruebas_e2e_julio.md`

1. Portada (nombre, carnet 202300850, rol).
2. Introducción y alcance.
3. Entorno de pruebas (versiones, URL, usuarios usados).
4. Los casos CP-01 a CP-09 con sus fichas y capturas.
5. Matriz de trazabilidad.
6. Resumen de resultados (cuántos aprobados, cuántos fallidos y su corrección).
7. Sección de video con el enlace de Drive.

---

## 4. Parte C2: Manual de usuario (cliente final)

Escribe `manual_usuario_julio.md` para una persona que **no** es técnica. Lenguaje claro, pasos numerados y una captura por paso. Contenido:

1. **Cómo entrar a la tienda** y recorrer el catálogo por categorías.
2. **Buscar un producto** y ver su ficha (precio, disponibilidad, descripción).
3. **Crear una cuenta** (registro) y recuperar la contraseña.
4. **Agregar al carrito** y modificar cantidades.
5. **Pagar:** transferencia bancaria (con los datos de cuenta de TechCore) y pago simulado (Demo).
6. **Confirmación del pedido** y correo recibido.
7. **Mi cuenta (`/my`):** ver pedidos, descargar facturas, actualizar datos.
8. **Cómo solicitar una cotización** (clientes B2B).
9. **Preguntas frecuentes** (qué pasa si un producto está agotado, cuánto tarda el despacho, cómo se factura).

Las capturas se toman con un cliente de prueba (por ejemplo, el que registraste en CP-01).

---

## 5. Parte C3: Conclusiones, escalabilidad y presentación final

### 5.1 Informe `conclusiones_escalabilidad_julio.md`

1. **Medición de logros frente a los objetivos SMART de la Fase 1.** Toma los tres objetivos (integración ERP/CRM/Web con trazabilidad del 100%; automatización de la cadena de suministro con carga masiva de 20+ productos y reglas de stock; fidelización y marketing con 2 campañas y pipeline Kanban) y para cada uno indica el resultado alcanzado con evidencia (referencia a pruebas, capturas y reportes de BI).
2. **Conclusiones técnicas y de negocio** (al menos cinco), apoyadas en lo que se ve en el sistema.
3. **Limitaciones actuales:** pago simulado, un solo almacén, ventas históricas de demostración para el BI, evaluación sobre una VM local.
4. **Propuesta de escalabilidad:**
   - Pasarela de pago real (por ejemplo, tarjeta con un proveedor local o internacional).
   - Despliegue en la nube con balanceo, copias de seguridad automáticas y dominio propio.
   - Múltiples almacenes y puntos de venta.
   - Integración con couriers (guías de envío) y facturación electrónica FEL de SAT.
   - Refresco automático del BI (programación de actualización) y tableros para gerencia.
   - Segmentación avanzada y automatización de marketing en el CRM (o evaluar SuiteCRM o Zoho, según el plan flexible del enunciado).
   - Aplicación móvil y analítica de comportamiento del cliente.
5. **Riesgos y mitigación** (breve tabla).
6. **Conclusión general** de cierre del proyecto.

### 5.2 Presentación final (obligatoria)

Diapositivas sugeridas (12 a 15), con diseño sobrio y consistente (colores de marca TechCore, sin emojis):

1. Portada (curso, grupo 7, integrantes, empresa).
2. Problema y objetivo del proyecto.
3. Objetivos SMART.
4. Arquitectura (VM, Docker, Odoo, PostgreSQL, Power BI).
5. Fase 1: diagnóstico y diseño (resumen).
6. Fase 2: datos maestros, compras y CRM (resumen con una captura).
7. Fase 3: e-commerce (captura de la tienda y del portal).
8. Flujo end-to-end (compra, inventario, factura, CRM) con un diagrama.
9. Resultados de las pruebas (tabla de casos).
10. Business Intelligence: inventario y ventas (capturas del tablero).
11. Logros frente a los objetivos SMART.
12. Escalabilidad y siguientes pasos.
13. Conclusiones.
14. Demostración o enlace a los videos.
15. Preguntas.

Reparte quién presenta cada parte con Jonathan y Francisco. Ensayen una vez con cronómetro.

---

## 6. Video (3 a 4 minutos)

1. Presentación (10 segundos).
2. Registro de un cliente nuevo y compra en la tienda (60 segundos).
3. Pago, confirmación y factura en el portal (40 segundos).
4. Verificación del descuento de inventario (30 segundos).
5. La oportunidad `Web B2C` en el CRM (20 segundos).
6. Reposición: orden de compra y recepción (40 segundos).
7. Cierre con los resultados de las pruebas (10 segundos).

Sube a Drive con acceso **"Cualquier persona con el enlace puede ver"** y verifícalo en una ventana de incógnito.

---

## 7. Reglas de Git para ti

- Sube solo tus archivos: `pruebas_e2e_julio.md`, `manual_usuario_julio.md`, `conclusiones_escalabilidad_julio.md`, la presentación y `capturas/julio_f3_*`.
- **No subas ni modifiques** `dump.sql.gz`, `TechCore_DB_backup.zip` ni `filestore/`. Si Git los marca como modificados después de probar, descártalos:
  ```bash
  git checkout -- Proyecto/Fase2/techcore-odoo/db-init/dump.sql.gz
  git checkout -- Proyecto/Fase2/techcore-odoo/backup/TechCore_DB_backup.zip
  ```
- `git pull origin main` antes de empezar cada sesión.
- Mensajes de commit descriptivos y sin emojis, por ejemplo: `docs(pruebas): casos E2E y matriz de trazabilidad`.
- Tus pruebas modifican **tu** base local; eso es normal y no se sube. El dump oficial lo regenera Jonathan al final.

---

## 8. Lista de verificación final

- [ ] Los casos CP-01 a CP-09 están ejecutados con capturas y resultado real.
- [ ] La matriz de trazabilidad está completa.
- [ ] Los fallos encontrados están documentados y reportados a Jonathan.
- [ ] El manual de usuario cubre registro, compra, pago, factura y portal.
- [ ] El informe de conclusiones y escalabilidad mide los tres objetivos SMART.
- [ ] La presentación final está terminada y ensayada.
- [ ] Video en Drive con enlace público, verificado en incógnito.
- [ ] Todos los documentos están sin emojis y con tildes y eñes.
