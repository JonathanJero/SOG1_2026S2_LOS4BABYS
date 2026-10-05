# Scripts de utilidad - NO SON PARTE DEL ENTREGABLE

Esta carpeta contiene scripts de soporte tecnico desarrollados durante la
implementacion del proyecto. **No forman parte de la entrega academica y no
deben ejecutarse durante la evaluacion tecnica.**

## Por que estan en esta carpeta

La rubrica del punto 2.1 (30 puntos) exige demostrar la carga de productos,
clientes y proveedores **en ambas modalidades**: masiva (importador de Excel)
y manual (formulario de la interfaz). El entregable arranca con la base de
datos **sin datos maestros**, precisamente para que esa demostracion pueda
realizarse en vivo.

Estos scripts existen unicamente como red de seguridad: permiten reconstruir
un estado de datos en caso de que la base se dane o se pierda. Si un
integrante los ejecuta antes de la evaluacion, elimina la posibilidad de
demostrar la carga y resta puntos.

## Contenido

| Script | Que hace | Cuando usarlo |
|---|---|---|
| `import_datos_maestros.py` | Crea los 20 productos, 3 proveedores, 7 categorias y el inventario inicial desde los `.xlsx` del proyecto | Solo si se pierde la base y hay que reconstruir los datos |
| `reaplicar_inventario.py` | Reaplica el inventario fisico como ajuste nativo de Odoo (con movimientos y capas de valuacion) | Idem |
| `actualizar_clientes.py` | Actualiza los 5 clientes con sus datos de contacto y los marca como clientes (`customer_rank`) | Idem |
| `asignar_grupos_ventas.py` | Asigna los grupos de Ventas al usuario administrador | Si el menu de Ventas no aparece |
| `generar_base_limpia.py` | **Borra** los datos cargados y deja solo la configuracion, regenerando el estado que se entrega | Para volver al estado de entrega antes de evaluacion |
| `generar_excel_precios_proveedor.py` | Genera el archivo `5_Precios_Proveedores_Odoo.xlsx` con 60 lineas de precio de proveedor (20 productos x 3 proveedores) | Si hay que regenerar ese Excel |

## Nota sobre `generar_excel_precios_proveedor.py`

Este script **si forma parte de la entrega**, a diferencia de los demas. El archivo que produce (`5_Precios_Proveedores_Odoo.xlsx`) es uno de los cinco que se cargan en la demostracion del punto 2.1, y debe estar presente en la carpeta `techcore-odoo/`.

No requiere base de datos: se ejecuta directamente con Python.

```bash
python3 scripts/utilidad/generar_excel_precios_proveedor.py
```

## Uso

Todos se ejecutan con el contenedor de Odoo:

```bash
cd Proyecto/Fase2/techcore-odoo

# Reconstruir datos maestros
docker compose run --rm -T web odoo shell \
  -c /etc/odoo/odoo.conf -d TechCore_DB --db_host=db --stop-after-init \
  --log-level=warn < scripts/utilidad/import_datos_maestros.py

# Volver al estado de entrega (base limpia)
docker compose run --rm -T web odoo shell \
  -c /etc/odoo/odoo.conf -d TechCore_DB --db_host=db --stop-after-init \
  --log-level=warn < scripts/utilidad/generar_base_limpia.py
```

## Lo que NO se toca

`generar_base_limpia.py` conserva deliberadamente la configuracion que si
forma parte de la entrega:

- Menus, grupos y permisos (incluido el menu de Ventas)
- Modulos instalados (`purchase_requisition_stock`, `crm`, `mass_mailing`, ...)
- Etapas del pipeline CRM
- Plantillas de correo y campanas de email marketing
- Sitio web y portal de cliente