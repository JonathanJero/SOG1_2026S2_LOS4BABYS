# Manual Técnico de Configuración y Operación: Módulo CRM, Email Marketing y Portal

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería**  
**Escuela de Ciencias y Sistemas**  
**Sistemas Organizacionales y Gerenciales 1 (SOG1) - Sección A**  
**Segundo Semestre 2026**  

**Empresa:** TechCore Solutions Guatemala  
**Integrante:** Jonathan Eliud Jerónimo Salguero  
**Carnet:** 202300353  
**Rol:** Líder de Infraestructura, CRM y Compilación Final  
**Fase Evaluada:** Fase 2 - Configuración, Desarrollo de Módulos y Operación Base  

---

## 1. Introducción y Alcance Técnico

El presente manual técnico documenta de forma detallada y visual los procedimientos implementados en el ecosistema empresarial **Odoo 17.0 Community Edition** para dar cumplimiento a los requerimientos comerciales, de marketing digital e identidad corporativa de la organización **TechCore Solutions Guatemala**.

Las áreas funcionales cubiertas en este documento corresponden a:
1. **Portal Web Corporativo:** Despliegue de la página de bienvenida y catálogo de soluciones de hardware corporativo en la raíz del ERP.
2. **Punto 15: Tablero de Clientes en CRM (Pipeline de Ventas en Kanban):** Configuración del flujo comercial, creación de las 4 etapas del embudo de ventas, asignación de 5 clientes con etiquetas B2B y demostración de oportunidad ganada.
3. **Punto 13: Plantillas de Correo Electrónico (Email Marketing):** Diseño de plantillas en código HTML responsivo con iconografía vectorial SVG (sin emojis informales) para promociones de hardware y fidelización de clientes preferenciales.
4. **Punto 14: Envío de Correos y Campaña Publicitaria en CRM:** Creación de la campaña corporativa UTM, segmentación de contactos empresariales y auditoría de despacho en el dashboard de marketing.

---

## 2. Portal Institucional y Página de Inicio de TechCore Solutions

### 2.1 Descripción y Propósito
Para proporcionar una presencia corporativa completa tanto a clientes externos como al equipo interno de ventas, se configuró la página de inicio del ERP (`http://192.168.64.11:8069/`). 

Esta vista consolida la identidad corporativa de TechCore Solutions Guatemala, integrando:
* **Banner de Bienvenida (Hero Section):** Resumen de valor sobre infraestructura de centros de datos, servidores rack y componentes de alta gama.
* **Métricas Institucionales:** Catálogo con más de 20 productos, 100% de trazabilidad ERP/CRM, 3 años de garantía directa y cobertura a nivel nacional.
* **Llamados a la Acción (CTA):** Enlaces directos para explorar el catálogo de productos y solicitar cotizaciones B2B.

![Figura 1: Portada Corporativa y Portal Web de TechCore Solutions Guatemala](capturas/captura_1_portada_web.png)

---

## 3. Punto 15: Tablero de Clientes en CRM (Pipeline de Ventas en Kanban)

### 3.1 Flujo Comercial y Etapas del Embudo
El módulo de CRM de TechCore Solutions administra el ciclo de vida de las oportunidades comerciales desde su recepción inicial hasta el cierre definitivo. Se implementó una vista de tipo **Kanban** que proporciona visibilidad en tiempo real del estado de cada cuenta mediante tarjetas dinámicas interactivas.

El embudo de ventas comprende cuatro etapas secuenciales:
1. **Lead:** Registro de prospectos interesados en infraestructura tecnológica.
2. **Contactado:** Comunicación inicial, validación de requerimientos y dimensionamiento técnico.
3. **Negociación:** Presentación formal de la propuesta técnica y cotización económica de servidores y almacenamiento.
4. **Cerrado / Ganado:** Aceptación formal por parte del cliente y confirmación de la venta.

### 3.2 Implementación del Tablero Kanban y Segmentación B2B
En el tablero Kanban se registraron 5 oportunidades representativas, aplicando la etiqueta `B2B` para distinguir cuentas corporativas:
* **Innova Solutions:** Adquisición de unidades de almacenamiento masivo (Etapa: *Lead*, etiqueta *B2B*).
* **Carlos Ruiz:** Cotización de memorias RAM para virtualización (Etapa: *Contactado*, etiqueta *B2B*).
* **TechCorp S.A.:** Suministro e instalación de servidores rack (Etapa: *Contactado*, etiqueta *B2B*).
* **María López:** Renovación de infraestructura de cómputo (Etapa: *Negociación*).
* **Juan Pérez:** Implementación de servidores para centro de datos (Etapa: *Cerrado / Ganado*).

![Figura 2: Tablero Kanban del CRM con las 4 Etapas, Tarjetas de Clientes y Etiquetas B2B](capturas/captura_2_crm_pipeline_kanban.png)

---

### 3.3 Cierre Exitoso de Negociación (Oportunidad Ganada)
Para comprobar el ciclo comercial completo, se procesó la oportunidad de **Juan Pérez** a través de todas las fases del pipeline:
1. Se abrió el formulario detallado de la oportunidad comercial.
2. Se verificó el registro de datos de contacto corporativo (`juan.perez@gmail.com`, teléfono institucional).
3. Se hizo clic en la acción **Ganado**, asignando automáticamente una probabilidad de cierre del **100%**.
4. El sistema actualizó el estado a **Cerrado** e insertó el listón verde distintivo de éxito (*WON*) en la esquina superior del formulario.

![Figura 3: Detalle de la Oportunidad Comercial Cerrada y Marcada Exitosamente como Ganada](capturas/captura_3_crm_oportunidad_ganada.png)

---

## 4. Punto 13 y 14: Email Marketing, Plantillas y Campañas Publicitarias

### 4.1 Arquitectura de Plantillas de Correo (Punto 13)
Para asegurar una comunicación corporativa de primer nivel, no se utilizaron correos de texto plano ni emojis informales. En su lugar, se desarrollaron dos plantillas en código **HTML responsivo con CSS inline e iconografía vectorial SVG**:

1. **Plantilla 1 - Promoción Especial de Hardware B2B:**
   * Archivo en repositorio: `Proyecto/Fase2/plantillas-correo/plantilla_1_promocion_b2b.html`.
   * Incluye banner promocional del **20% de Descuento**, catálogo de memorias DDR5, discos SSD NVMe Enterprise y servidores Rack, concluyendo con un botón de llamada a la acción en azul formal: `COMPRAR AHORA / COTIZAR B2B`.
2. **Plantilla 2 - Programa de Fidelización y Clientes Preferenciales:**
   * Archivo en repositorio: `Proyecto/Fase2/plantillas-correo/plantilla_2_fidelizacion.html`.
   * Diseñada para clientes recurrentes con mensaje de agradecimiento institucional, pilares de soporte 24/7, sustitución inmediata por garantía y un botón de acción en color verde esmeralda: `VER MIS PEDIDOS Y FACTURAS`.

---

### 4.2 Configuración y Despacho de la Campaña Publicitaria (Punto 14)
En el módulo de **Email Marketing**, se creó y gestionó la campaña maestra: **`Campaña Publicitaria B2B TechCore 2026`** vinculada al modelo UTM de Odoo.

1. **Segmentación de Contactos:** Se definió una regla de filtrado sobre el modelo de contactos (`res.partner`) restringida a aquellos con la etiqueta activa `B2B`, asegurando que las promociones alcancen exclusivamente a los clientes empresariales registrados.
2. **Control y Auditoría de Envíos:** En el panel de control de la campaña se vincularon los correos masivos correspondientes, gestionando el paso de estado de *Borrador (Draft)* a *Enviado (Sent)*.
3. **Métricas de Rendimiento:** La cabecera de la campaña provee trazabilidad sobre ingresos proyectados, cotizaciones vinculadas y tasa de entrega efectiva.

![Figura 4: Panel de Control de la Campaña de Email Marketing con Envíos Masivos Vinculados](capturas/captura_4_email_marketing_campanias.png)

---

### 4.3 Verificación de Renderizado de la Plantilla en Odoo
Al acceder a la vista del correo masivo correspondiente a la campaña de fidelización (`Gracias por confiar en TechCore Solutions`), se observa el diseño limpio, la tipografía corporativa y el bloque de agradecimiento renderizado con precisión dentro del editor de Odoo.

![Figura 5: Vista Previa y Estructura de la Plantilla de Correo de Fidelización en Odoo](capturas/captura_5_plantilla_correo_preview.png)

---

## 5. Resumen de Artefactos Técnicos en el Repositorio

Para facilitar la revisión del tribunal evaluador, todos los recursos técnicos se encuentran integrados en la estructura del proyecto:

| Insumo Técnico | Ubicación en el Repositorio | Descripción Funcional |
| --- | --- | --- |
| **Plantilla Promoción B2B** | `Proyecto/Fase2/plantillas-correo/plantilla_1_promocion_b2b.html` | Código fuente HTML responsivo con oferta del 20% e iconos SVG. |
| **Plantilla Fidelización** | `Proyecto/Fase2/plantillas-correo/plantilla_2_fidelizacion.html` | Código fuente HTML con programa VIP y botón de acción verde. |
| **Script de Despliegue Rápido** | `Proyecto/techcore-odoo/start.sh` | Script bash de inicialización automatizada con un solo comando. |
| **Volcado SQL de Base de Datos** | `Proyecto/techcore-odoo/db-init/dump.sql.gz` | Base de datos unificada con CRM, Email Marketing, Portada y Requisición de Compras. |
| **Respaldo Nativo de Odoo** | `Proyecto/techcore-odoo/backup/TechCore_DB_backup.zip` | Archivo zip para restauración mediante el gestor web de base de datos. |
| **Capturas Esenciales** | `Proyecto/Fase2/docu/capturas/` | Directorio con las 5 capturas en alta resolución que ilustran el flujo. |

---

## 6. Conclusiones Técnicas

1. **Trazabilidad y Visibilidad Operativa:** La implementación del pipeline Kanban en Odoo CRM optimiza la supervisión del embudo de ventas de TechCore Solutions, permitiendo identificar de forma inmediata en qué fase se encuentra cada cuenta empresarial y asegurando una transición fluida hacia el cierre de negocios.
2. **Segmentación y Automatización Eficaz:** El uso combinado de campañas UTM y filtros basados en etiquetas B2B garantiza que las iniciativas de mercadeo alcancen a los tomadores de decisiones indicados, maximizando el retorno de inversión en comunicaciones masivas.
3. **Calidad de Presentación y Portabilidad:** Al estandarizar las plantillas de correo en código HTML sin emojis informales e incorporar un portal de bienvenida institucional, se proyecta un nivel de madurez y profesionalismo alineado con los estándares de la industria y la rúbrica de evaluación del curso.

---

**Fin del manual técnico.**

# VIDEO 3 — CRM, Email Marketing y Portal

**Integrante:** Jonathan Eliud Jerónimo Salguero

**Tarea demostrativa:** Pipeline de ventas en CRM (Kanban), plantillas corporativas HTML/SVG y envío de campaña publicitaria B2B

**Puntos del enunciado cubiertos:** 13, 14 y 15

**Enlace de Google Drive:** [https://drive.google.com/file/d/1pgQGruBg9p83gksURiXsvYcohlpZTEd8/view?usp=sharing](https://drive.google.com/file/d/1pgQGruBg9p83gksURiXsvYcohlpZTEd8/view?usp=sharing)

**Descripción del contenido del video:**

El video demuestra la operación completa del área comercial y de mercadeo en **Odoo 17.0 Community Edition**:
1. **Pipeline de Ventas en CRM (Punto 15):** Visualización del tablero Kanban configurado con las 4 etapas comerciales (*Lead*, *Contactado*, *Negociación*, *Cerrado*), la distribución de los 5 prospectos empresariales con la etiqueta `B2B`, el desplazamiento dinámico entre etapas y el cierre exitoso de la oportunidad de *Juan Pérez* marcada con el listón verde de ganada (*Won*, 100% probabilidad).
2. **Plantillas de Correo Electrónico (Punto 13):** Presentación de las dos plantillas corporativas responsivas diseñadas con estándares profesionales (sin emojis e incorporando iconografía SVG): la de *Promoción Especial B2B* (20% de descuento en almacenamiento y memorias) y la de *Fidelización de Clientes Preferenciales* con llamado a la acción destacado en color verde.
3. **Campaña Publicitaria y Envío Segmentado (Punto 14):** Demostración de la vinculación de la *Campaña Publicitaria B2B TechCore 2026* bajo el modelo UTM, la segmentación filtrada de contactos hacia clientes con etiqueta `B2B`, el despacho masivo y la consulta de métricas de entrega en el dashboard de Email Marketing.

