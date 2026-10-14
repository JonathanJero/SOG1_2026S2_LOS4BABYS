# -*- coding: utf-8 -*-
"""Configuracion completa del E-Commerce de la Fase 3 (TechCore Solutions Guatemala).

Este script ejecuta el Hito A2 de forma 100% idempotente:
1. Actualiza los datos de la compania (nombre a 'TechCore Solutions Guatemala', moneda GTQ).
2. Configura los ajustes de ventas y facturacion:
   - automatic_invoice = True (factura generada automaticamente al confirmar pago)
   - default_invoice_policy = 'order' (politica sobre cantidades pedidas)
   - Aplica invoice_policy = 'order' y el impuesto IVA 12% a los 21 productos.
3. Habilita y publica los metodos de pago:
   - Demo (test, publicado)
   - Transferencia Bancaria (publicado, habilitado, con cuenta y datos bancarios de TechCore)
4. Crea las categorias publicas de eCommerce (product.public.category) y clasifica los 21 productos.
5. Publica los 21 productos en el eCommerce:
   - website_published = True, is_published = True
   - allow_out_of_stock_order = False (no permite comprar sin inventario)
   - show_availability = True, available_threshold = 5.0
   - description_sale con descripcion tecnica formal en espanol
   - image_1920 generada dinamicamente con Pillow en alta resolucion (800x800 px)
6. Habilita registro libre de clientes (auth_signup_uninvited = 'b2c').
7. Crea la accion automatizada (base.automation) sobre sale.order que genera
   la oportunidad en CRM con etiqueta 'Web B2C' en etapa 'Lead' al crearse un pedido web.

Uso:
  docker exec -i techcore_odoo_web odoo shell -d TechCore_DB \
    --db_host techcore_postgres_db -r odoo -w techcore_secure_pwd --no-http --log-level=warn < configurar_fase3_ecommerce.py
"""
import base64
import io
import logging
from PIL import Image, ImageDraw, ImageFont

_logger = logging.getLogger("configurar_fase3_ecommerce")

# Informacion tecnica detallada de los 21 productos
CATALOGO_DETALLE = [
    {
        "code": "PROD-001",
        "name": "Intel Core i9-13900K",
        "cat": "Procesador",
        "accent": (59, 130, 246),  # Azul
        "specs": "24 Núcleos (8P+16E) / 32 Hilos · 5.8 GHz Turbo · LGA1700",
        "desc": "Procesador de gama alta para entusiastas y estaciones de trabajo. Arquitectura híbrida con 24 núcleos (8 de rendimiento y 16 de eficiencia) y 32 hilos de procesamiento, frecuencia máxima de hasta 5.8 GHz con Intel Thermal Velocity Boost y 36 MB de Intel Smart Cache. Compatible con zócalo LGA1700 y memoria DDR5."
    },
    {
        "code": "PROD-002",
        "name": "AMD Ryzen 9 7950X",
        "cat": "Procesador",
        "accent": (239, 68, 68),  # Rojo/Naranja
        "specs": "16 Núcleos / 32 Hilos · 5.7 GHz Boost · 80MB Caché · AM5",
        "desc": "Procesador insignia para creadores de contenido y renderizado pesado. Cuenta con 16 núcleos físicos y 32 hilos basados en la arquitectura Zen 4 de 5 nanómetros, velocidad boost de hasta 5.7 GHz y 80 MB de caché combinada L2+L3. Requiere plataforma AM5 con soporte nativo para PCIe 5.0 y DDR5."
    },
    {
        "code": "PROD-013",
        "name": "Intel Core i5-13600K",
        "cat": "Procesador",
        "accent": (59, 130, 246),
        "specs": "14 Núcleos (6P+8E) / 20 Hilos · 5.1 GHz · LGA1700",
        "desc": "Procesador de alto rendimiento para gaming competitivo y productividad multitarea. Dispone de 14 núcleos (6 P-Cores y 8 E-Cores) y 20 hilos, frecuencia turbo de 5.1 GHz y 24 MB de caché. Gran equilibrio térmico y eficiencia energética en plataforma Intel LGA1700."
    },
    {
        "code": "PROD-014",
        "name": "AMD Ryzen 5 7600X",
        "cat": "Procesador",
        "accent": (249, 115, 22),
        "specs": "6 Núcleos / 12 Hilos · 5.3 GHz Boost · Zen 4 · AM5",
        "desc": "Procesador ágil para computadoras de alto desempeño y juegos de última generación. Posee 6 núcleos y 12 hilos con arquitectura Zen 4, frecuencia base de 4.7 GHz y aceleración hasta 5.3 GHz, con 38 MB de caché total en zócalo AM5 con soporte DDR5."
    },
    {
        "code": "PROD-003",
        "name": "Corsair Vengeance 32GB DDR5",
        "cat": "Memoria RAM",
        "accent": (168, 85, 247),  # Morado
        "specs": "32GB (2x16GB) · DDR5 5600 MHz · Disipador Aluminio · XMP 3.0",
        "desc": "Kit de memoria RAM de alto rendimiento compuesto por dos módulos de 16 GB DDR5 a 5600 MHz. Integra disipador de calor de aluminio anodizado de bajo perfil y perfiles XMP 3.0 para configuración automática de latencias en plataformas Intel y AMD."
    },
    {
        "code": "PROD-004",
        "name": "Kingston Fury Beast 16GB DDR4",
        "cat": "Memoria RAM",
        "accent": (168, 85, 247),
        "specs": "16GB (1x16GB) · DDR4 3200 MHz · Latencia CL16 · 1.35V",
        "desc": "Módulo individual de 16 GB DDR4 a 3200 MHz ideal para actualizaciones corporativas y sistemas de trabajo confiables. Compatible con perfiles Intel XMP y AMD Ryzen, disipador de calor compacto y operación de bajo consumo a 1.35V."
    },
    {
        "code": "PROD-015",
        "name": "G.Skill Trident Z5 RGB 64GB",
        "cat": "Memoria RAM",
        "accent": (168, 85, 247),
        "specs": "64GB (2x32GB) · DDR5 6000 MHz · CL30 · Iluminación RGB",
        "desc": "Kit premium de memoria DDR5 de 64 GB (2 x 32 GB) a 6000 MHz CL30. Diseñado para estaciones de cálculo avanzado y renderizado 3D, cuenta con barra de iluminación RGB personalizable y disipador de doble tono de alta disipación térmica."
    },
    {
        "code": "PROD-005",
        "name": "Samsung 990 PRO 2TB NVMe",
        "cat": "SSD",
        "accent": (16, 185, 129),  # Verde esmeralda
        "specs": "2TB NVMe M.2 2280 · Lectura 7450 MB/s · Escritura 6900 MB/s",
        "desc": "Unidad de estado sólido M.2 PCIe 4.0 NVMe de máxima velocidad. Ofrece tasas secuenciales de lectura de hasta 7450 MB/s y escritura de 6900 MB/s con memoria V-NAND de última generación y controlador térmico inteligente para cargas intensivas."
    },
    {
        "code": "PROD-006",
        "name": "WD Black SN850X 1TB NVMe",
        "cat": "SSD",
        "accent": (16, 185, 129),
        "specs": "1TB NVMe PCIe Gen4 · Lectura 7300 MB/s · Game Mode 2.0",
        "desc": "Unidad SSD PCIe Gen4 x4 optimizada para transferencias de alta velocidad y tiempos de carga mínimos. Alcanza velocidades de lectura de 7300 MB/s y escritura de 6300 MB/s, equipada con tecnología Game Mode 2.0 y caché dinámica SLC."
    },
    {
        "code": "PROD-016",
        "name": "Crucial P3 Plus 4TB NVMe",
        "cat": "SSD",
        "accent": (16, 185, 129),
        "specs": "4TB PCIe 4.0 3D NAND · Lectura 5000 MB/s · Gran Capacidad",
        "desc": "Almacenamiento masivo de estado sólido de 4 TB en factor de forma M.2 2280. Utiliza interfaz NVMe PCIe 4.0 con velocidades de lectura de hasta 5000 MB/s, ofreciendo amplia capacidad para bibliotecas multimedia y proyectos de ingeniería."
    },
    {
        "code": "PROD-020",
        "name": "Seagate IronWolf Pro 18TB",
        "cat": "Disco Duro",
        "accent": (245, 158, 11),  # Ámbar
        "specs": "18TB Enterprise NAS · 7200 RPM · 256MB Caché · Sensores RV",
        "desc": "Disco duro empresarial de 18 TB diseñado específicamente para sistemas de almacenamiento en red (NAS) de hasta 24 bahías. Velocidad de 7200 RPM, sensores de vibración rotacional (RV) integrados y límite de carga de trabajo de 300 TB/año."
    },
    {
        "code": "PROD-007",
        "name": "Cisco Catalyst 2960-X 24 Port",
        "cat": "Switch",
        "accent": (6, 182, 212),  # Cian
        "specs": "24x Gigabit RJ45 · 4x SFP 1G · Capa 2 Administrable · FlexStack",
        "desc": "Switch de nivel empresarial administrable de capa 2 con 24 puertos Gigabit Ethernet 10/100/1000 y 4 enlaces ascendentes SFP de 1G. Soporta apilamiento FlexStack-Plus y tecnología Cisco EnergyWise para ahorro de energía en infraestructura de red."
    },
    {
        "code": "PROD-008",
        "name": "Ubiquiti UniFi Switch 48 PoE",
        "cat": "Switch",
        "accent": (6, 182, 212),
        "specs": "48x Gigabit PoE+ · 4x SFP 1G · Pantalla LCM 1.3\" · UniFi OS",
        "desc": "Switch gestionable de 48 puertos Gigabit Ethernet con capacidad de entrega PoE+ (802.3at/af) y 4 puertos SFP de 1G. Integración nativa con la consola UniFi Network, pantalla táctil LCM de 1.3 pulgadas con información de estado en tiempo real."
    },
    {
        "code": "PROD-017",
        "name": "TP-Link TL-SG108E 8 Port",
        "cat": "Switch",
        "accent": (6, 182, 212),
        "specs": "8x Gigabit RJ45 · Easy Smart · QoS 802.1p · Chasis Metálico",
        "desc": "Switch inteligente para pequeñas oficinas con 8 puertos Gigabit RJ45. Proporciona monitoreo de red, priorización de tráfico (QoS 802.1p) y segmentación por VLAN (basada en puerto, etiqueta o MTU), con carcasa metálica robusta y silenciosa sin ventilador."
    },
    {
        "code": "PROD-009",
        "name": "Dell PowerEdge R750",
        "cat": "Servidor",
        "accent": (99, 102, 241),  # Indigo
        "specs": "Rack 2U · Dual Intel Xeon Scalable · Hot-Plug Redundante · iDRAC9",
        "desc": "Servidor empresarial en rack de 2U con soporte para dos procesadores Intel Xeon Scalable de 3ª generación. Diseñado para virtualización densa, bases de datos exigentes y cargas de análisis en la nube, con fuentes redundantes Hot-Plug Platinum y control iDRAC9."
    },
    {
        "code": "PROD-010",
        "name": "HPE ProLiant DL380 Gen10",
        "cat": "Servidor",
        "accent": (99, 102, 241),
        "specs": "Rack 2U · Intel Xeon Scalable · HPE iLO 5 · Silicon Root of Trust",
        "desc": "Servidor líder en la industria en formato rack 2U con capacidad para procesadores Intel Xeon Scalable, hasta 3 TB de memoria DDR4 y bahías SAS/SATA/NVMe escalables. Incorpora tecnología de gestión remota HPE iLO 5 con seguridad Silicon Root of Trust."
    },
    {
        "code": "PROD-018",
        "name": "Lenovo ThinkSystem SR650",
        "cat": "Servidor",
        "accent": (99, 102, 241),
        "specs": "Rack 2U · 24 Bahías 2.5\" · Alta Disponibilidad · XClarity",
        "desc": "Servidor en rack 2U de alta disponibilidad y flexibilidad de almacenamiento. Admite hasta 24 unidades de 2.5 pulgadas, múltiples tarjetas aceleradoras PCIe y memoria persistente, gestionado por el motor Lenovo XClarity Controller para entornos corporativos."
    },
    {
        "code": "PROD-011",
        "name": "ASUS ROG Maximus Z790 Hero",
        "cat": "Tarjeta Madre",
        "accent": (236, 72, 153),  # Rosa
        "specs": "LGA1700 · 20+1 Fases · PCIe 5.0 · Thunderbolt 4 · Wi-Fi 6E",
        "desc": "Tarjeta madre premium para procesadores Intel Core de 13ª y 14ª generación con zócalo LGA1700. Cuenta con etapa de potencia de 20+1 fases, soporte DDR5, 5 ranuras M.2 (una PCIe 5.0), conectividad Thunderbolt 4 dual y Wi-Fi 6E integrado."
    },
    {
        "code": "PROD-012",
        "name": "MSI MAG B650 Tomahawk WiFi",
        "cat": "Tarjeta Madre",
        "accent": (236, 72, 153),
        "specs": "AM5 · 14+2+1 Fases VRM · DDR5 6400+ OC · Wi-Fi 6E",
        "desc": "Tarjeta madre de alto valor para procesadores AMD Ryzen serie 7000 en zócalo AM5. Equipada con diseño de alimentación VRM de 14+2+1 fases, disipadores extendidos, soporte DDR5 hasta 6400+ MHz (OC), audio de alta definición y conectividad Wi-Fi 6E."
    },
    {
        "code": "PROD-019",
        "name": "Gigabyte X670E AORUS Master",
        "cat": "Tarjeta Madre",
        "accent": (236, 72, 153),
        "specs": "AM5 X670E · PCIe 5.0 Gráfica y M.2 · Fins-Array III · 2.5 GbE",
        "desc": "Tarjeta madre para estaciones avanzadas con chipset AMD X670E. Soporta PCIe 5.0 en ranuras gráficas y de almacenamiento M.2, disipador térmico Fins-Array III con tubo de calor Direct-Touch, LAN de 2.5 GbE y conectividad USB 3.2 Gen 2x2 Type-C."
    },
    {
        "code": "PROD-021",
        "name": "Logitech MX Keys",
        "cat": "Periféricos",
        "accent": (20, 184, 166),  # Teal
        "specs": "Inalámbrico · Bluetooth & USB · Retroiluminación · Recargable USB-C",
        "desc": "Teclado inalámbrico avanzado para profesionales y desarrolladores. Teclas cóncavas para escritura fluida y precisa, retroiluminación inteligente por proximidad de manos, emparejamiento con hasta tres dispositivos vía Bluetooth o receptor USB y batería recargable USB-C."
    },
]


def generar_imagen_producto(item, precio):
    """Genera una imagen digital elegante en 800x800 con Pillow y la devuelve en base64."""
    ancho, alto = 800, 800
    accent = item["accent"]

    # Fondo oscuro profesional con degradado sutil
    img = Image.new("RGB", (ancho, alto), color=(15, 23, 42))  # Slate 900
    draw = ImageDraw.Draw(img)

    # Marco exterior con esquina recortada y brillo de acento
    draw.rectangle([(24, 24), (ancho - 24, alto - 24)], outline=(30, 41, 59), width=3)
    draw.rectangle([(20, 20), (ancho - 20, alto - 20)], outline=accent, width=2)

    # Barra superior de marca
    draw.rectangle([(40, 40), (ancho - 40, 90)], fill=(30, 41, 59))
    draw.rectangle([(40, 88), (ancho - 40, 90)], fill=accent)

    # Cargar fuentes del sistema
    try:
        font_brand = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 26)
        font_code = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf", 20)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 36)
        font_cat = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 22)
        font_specs = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 20)
        font_price = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 34)
    except Exception:
        font_brand = ImageFont.load_default()
        font_code = font_brand
        font_title = font_brand
        font_cat = font_brand
        font_specs = font_brand
        font_price = font_brand

    # Texto marca y codigo
    draw.text((60, 52), "TECHCORE SOLUTIONS", fill=(255, 255, 255), font=font_brand)
    draw.text((ancho - 220, 55), item["code"], fill=accent, font=font_code)

    # Insignia de Categoria
    cat_text = item["cat"].upper()
    draw.rounded_rectangle([(60, 130), (320, 175)], radius=8, fill=accent)
    draw.text((80, 140), cat_text, fill=(255, 255, 255), font=font_cat)

    # Tarjeta central con sombra simulada
    draw.rounded_rectangle([(60, 210), (ancho - 60, 560)], radius=16, fill=(30, 41, 59), outline=(51, 65, 85), width=2)

    # Icono decorativo / grid geometrico en la tarjeta
    for offset in range(0, 240, 30):
        draw.line([(80 + offset, 230), (80 + offset, 270)], fill=(51, 65, 85), width=1)
        draw.line([(ancho - 80 - offset, 500), (ancho - 80 - offset, 540)], fill=(51, 65, 85), width=1)

    # Titulo de producto en el centro
    # Centrar o dividir en dos lineas si es muy largo
    nombre = item["name"]
    palabras = nombre.split()
    if len(nombre) > 24 and len(palabras) > 2:
        mitad = len(palabras) // 2
        linea1 = " ".join(palabras[:mitad])
        linea2 = " ".join(palabras[mitad:])
        draw.text((90, 310), linea1, fill=(255, 255, 255), font=font_title)
        draw.text((90, 360), linea2, fill=(255, 255, 255), font=font_title)
    else:
        draw.text((90, 340), nombre, fill=(255, 255, 255), font=font_title)

    # Sello de Hardware Certificado
    draw.rounded_rectangle([(90, 450), (340, 490)], radius=6, fill=(15, 23, 42), outline=accent, width=1)
    draw.text((105, 460), "HARDWARE GARANTIZADO", fill=accent, font=font_code)

    # Precio
    precio_str = "Q {:,.2f}".format(precio)
    draw.text((ancho - 290, 450), precio_str, fill=(52, 211, 153), font=font_price)

    # Barra inferior de especificaciones tecnicas
    draw.rounded_rectangle([(60, 600), (ancho - 60, 720)], radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    draw.text((80, 620), "ESPECIFICACIONES:", fill=(148, 163, 184), font=font_code)
    draw.text((80, 655), item["specs"], fill=(241, 245, 249), font=font_specs)

    # Guardar en buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def ejecutar():
    admin = env.ref("base.user_admin")
    e = env(user=admin)
    print("=== CONFIGURANDO E-COMMERCE TECHCORE (HITO A2) ===")

    # 1. Compania
    comp = e.company
    comp.write({
        "name": "TechCore Solutions Guatemala",
        "street": "Avenida Las Américas 15-00, Zona 14",
        "city": "Ciudad de Guatemala",
        "phone": "+502 2333-5000",
        "email": "contacto@techcore.gt",
        "website": "http://192.168.64.11:8069",
    })
    print("Compania actualizada a:", comp.name)

    # 2. Facturacion automatica y politicas
    settings = e["res.config.settings"].create({
        "automatic_invoice": True,
        "default_invoice_policy": "order",
    })
    settings.execute()
    print("Ajustes de facturacion aplicados (automatic_invoice=True, invoice_policy='order').")

    # 3. Metodos de pago simulados
    # 3.1 Demo
    demo = e["payment.provider"].search([("code", "=", "demo")], limit=1)
    if demo:
        demo.write({
            "state": "test",
            "is_published": True,
        })
        print("Proveedor Demo activado (state='test', is_published=True).")

    # 3.2 Wire Transfer (Transferencia Bancaria)
    wt = e["payment.provider"].search([("code", "=", "custom")], limit=1)
    if not wt:
        wt = e["payment.provider"].browse(15)
    if wt:
        msg_banco = """
        <div style="font-family: inherit; line-height: 1.6;">
            <p><strong>Instrucciones para Transferencia Bancaria Directa:</strong></p>
            <p>Por favor realice el depósito o transferencia electrónica a nuestra cuenta corporativa:</p>
            <ul>
                <li><strong>Banco:</strong> Banco Industrial</li>
                <li><strong>Tipo de Cuenta:</strong> Cuenta Monetaria en Quetzales</li>
                <li><strong>No. de Cuenta:</strong> 004-892104-1</li>
                <li><strong>Beneficiario:</strong> TechCore Solutions Guatemala, S.A.</li>
                <li><strong>Referencia:</strong> Indique el número de orden de compra asignado</li>
            </ul>
            <p>Al efectuar su transferencia, envíe el comprobante a <strong>pagos@techcore.gt</strong> para la confirmación inmediata y despacho de su pedido.</p>
        </div>
        """
        wt.write({
            "name": "Transferencia Bancaria",
            "state": "enabled",
            "is_published": True,
            "pending_msg": msg_banco,
        })
        print("Proveedor Transferencia Bancaria configurado y publicado.")

    # 4. Categorias publicas de eCommerce
    nombres_cat = [
        "Procesador", "Memoria RAM", "SSD", "Disco Duro",
        "Switch", "Servidor", "Tarjeta Madre", "Periféricos"
    ]
    cats_publicas = {}
    for seq, nom in enumerate(nombres_cat, 1):
        c = e["product.public.category"].search([("name", "=", nom)], limit=1)
        if not c:
            c = e["product.public.category"].create({
                "name": nom,
                "sequence": seq * 10,
            })
            print("Categoria publica creada:", nom)
        cats_publicas[nom] = c

    # 5. Publicar los 21 productos con ficha tecnica e imagenes generadas
    tax_iva = e["account.tax"].search([("type_tax_use", "=", "sale"), ("amount", "=", 12.0)], limit=1)

    for item in CATALOGO_DETALLE:
        code = item["code"]
        tmpl = e["product.template"].search([("default_code", "=", code)], limit=1)
        if not tmpl:
            print("AVISO: No se encontro producto:", code)
            continue

        cat_pub = cats_publicas.get(item["cat"])
        img_b64 = generar_imagen_producto(item, tmpl.list_price)

        vals_prod = {
            "website_published": True,
            "is_published": True,
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 5.0,
            "invoice_policy": "order",
            "description_sale": item["desc"],
            "image_1920": img_b64,
        }
        if cat_pub:
            vals_prod["public_categ_ids"] = [(6, 0, [cat_pub.id])]
        if tax_iva:
            vals_prod["taxes_id"] = [(6, 0, [tax_iva.id])]

        tmpl.write(vals_prod)
        print("Producto publicado y configurado:", code, "-", tmpl.name)

    # 6. Registro libre de clientes
    icp = e["ir.config_parameter"].sudo()
    icp.set_param("auth_signup.invitation_scope", "b2c")
    website = e["website"].search([], limit=1)
    if website and hasattr(website, "auth_signup_uninvited"):
        website.write({"auth_signup_uninvited": "b2c"})
    print("Registro libre de clientes (/web/signup) habilitado.")

    # 7. Accion automatizada CRM: De la compra web al Lead Web B2C
    # Modelo sale.order
    model_sale = e["ir.model"].search([("model", "=", "sale.order")], limit=1)
    if model_sale:
        auto_rule = e["base.automation"].search([
            ("name", "=", "Generar Lead CRM desde Pedido Web"),
        ], limit=1)

        codigo_accion = """
# Accion automatica: Al crearse una orden de venta desde el sitio web,
# crea automaticamente una oportunidad en el CRM con etiqueta Web B2C.
tag = env['crm.tag'].search([('name', '=', 'Web B2C')], limit=1)
if not tag:
    tag = env['crm.tag'].create({'name': 'Web B2C'})
lead_stage = env['crm.stage'].search([('name', '=', 'Lead')], limit=1)
if not lead_stage:
    lead_stage = env['crm.stage'].search([], order='sequence asc', limit=1)

for order in records:
    if order.website_id:
        existente = env['crm.lead'].search([('description', 'like', order.name)], limit=1)
        if not existente:
            env['crm.lead'].create({
                'name': f'Oportunidad Web: {order.name} - {order.partner_id.name}',
                'partner_id': order.partner_id.id,
                'expected_revenue': order.amount_total,
                'tag_ids': [(4, tag.id)],
                'stage_id': lead_stage.id if lead_stage else False,
                'type': 'opportunity',
                'description': f'Generado automaticamente desde orden eCommerce {order.name}',
            })
"""
        action_server = e["ir.actions.server"].search([
            ("name", "=", "Crear Lead Web B2C"),
            ("model_id", "=", model_sale.id),
        ], limit=1)
        if not action_server:
            action_server = e["ir.actions.server"].create({
                "name": "Crear Lead Web B2C",
                "model_id": model_sale.id,
                "state": "code",
                "code": codigo_accion,
            })
        else:
            action_server.write({"code": codigo_accion})

        vals_rule = {
            "name": "Generar Lead CRM desde Pedido Web",
            "model_id": model_sale.id,
            "trigger": "on_create",
            "filter_domain": "[('website_id', '!=', False)]",
            "action_server_ids": [(6, 0, [action_server.id])],
            "active": True,
        }
        if auto_rule:
            auto_rule.write(vals_rule)
            print("Regla de automatizacion CRM actualizada.")
        else:
            auto_rule = e["base.automation"].create(vals_rule)
            print("Regla de automatizacion CRM creada.")

    e.cr.commit()
    print("\n=== VERIFICACION HITO A2 ===")
    total_pub = e["product.template"].search_count([("is_published", "=", True)])
    total_cat_pub = e["product.public.category"].search_count([])
    provs_pub = e["payment.provider"].search([("is_published", "=", True)])
    print("Total productos publicados: {} / 21".format(total_pub))
    print("Total categorias publicas: {}".format(total_cat_pub))
    print("Metodos de pago publicados: {}".format([p.name for p in provs_pub]))


ejecutar()
