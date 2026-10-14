-- =============================================================================
-- TechCore Solutions Guatemala - Vistas de Business Intelligence (Fase 3)
-- =============================================================================
-- Vistas analíticas diseñadas para conexión directa desde Microsoft Power BI
-- Desktop y herramientas analíticas mediante el usuario 'bi_reader'.
-- =============================================================================

-- 1. Rol de usuario analítico de solo lectura (bi_reader)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bi_reader') THEN
        CREATE ROLE bi_reader WITH LOGIN PASSWORD 'bi_reader_techcore';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE "TechCore_DB" TO bi_reader;
GRANT USAGE ON SCHEMA public TO bi_reader;
REVOKE CREATE ON SCHEMA public FROM PUBLIC, bi_reader;

-- 2. Vista: Detalle de Ventas (v_bi_ventas_detalle)
-- Muestra cada línea de venta confirmada con segmentación B2B/B2C, canal y temporalidad.
CREATE OR REPLACE VIEW v_bi_ventas_detalle AS
SELECT 
    so.name AS orden,
    so.date_order::date AS fecha,
    EXTRACT(YEAR FROM so.date_order)::integer AS anio,
    EXTRACT(MONTH FROM so.date_order)::integer AS mes,
    EXTRACT(WEEK FROM so.date_order)::integer AS semana,
    rp.name AS cliente,
    CASE 
        WHEN rp.is_company = true THEN 'B2B'
        WHEN EXISTS (
            SELECT 1 FROM res_partner_res_partner_category_rel rel
            JOIN res_partner_category rpc ON rpc.id = rel.category_id
            WHERE rel.partner_id = rp.id AND (rpc.name->>'en_US' = 'B2B' OR rpc.name->>'es_GT' = 'B2B')
        ) THEN 'B2B'
        WHEN EXISTS (
            SELECT 1 FROM res_partner_res_partner_category_rel rel
            JOIN res_partner_category rpc ON rpc.id = rel.category_id
            WHERE rel.partner_id = rp.id AND (rpc.name->>'en_US' = 'B2C' OR rpc.name->>'es_GT' = 'B2C')
        ) THEN 'B2C'
        ELSE 'Sin segmento'
    END AS segmento,
    CASE 
        WHEN so.website_id IS NOT NULL THEN 'Web'
        ELSE 'Cotización'
    END AS canal,
    pt.default_code AS codigo_producto,
    COALESCE(pt.name->>'es_GT', pt.name->>'en_US') AS producto,
    pc.name AS categoria,
    sol.product_uom_qty AS cantidad,
    ROUND(sol.price_unit::numeric, 2) AS precio_unitario,
    ROUND(sol.price_subtotal::numeric, 2) AS subtotal,
    so.state AS estado
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id
JOIN res_partner rp ON rp.id = so.partner_id
JOIN product_product pp ON pp.id = sol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN product_category pc ON pc.id = pt.categ_id
WHERE so.state IN ('sale', 'done')
ORDER BY so.date_order DESC;

-- 3. Vista: Inventario y Alertas de Stock (v_bi_inventario)
-- Muestra existencias actuales en almacén principal, umbrales de reposición y valoración monetaria.
CREATE OR REPLACE VIEW v_bi_inventario AS
SELECT 
    pt.default_code AS codigo_producto,
    COALESCE(pt.name->>'es_GT', pt.name->>'en_US') AS producto,
    pc.name AS categoria,
    COALESCE(SUM(sq.quantity), 0) AS existencias,
    COALESCE(op.product_min_qty, 0) AS stock_minimo,
    COALESCE(op.product_max_qty, 0) AS stock_maximo,
    CASE 
        WHEN op.id IS NULL THEN 'Sin regla'
        WHEN COALESCE(SUM(sq.quantity), 0) <= op.product_min_qty THEN 'Bajo'
        ELSE 'Normal'
    END AS estado_stock,
    ROUND(COALESCE((
        SELECT prop.value_float 
        FROM ir_property prop 
        WHERE prop.name = 'standard_price' 
          AND prop.res_id = 'product.product,' || pp.id 
        LIMIT 1
    ), 0.0)::numeric, 2) AS costo,
    ROUND(pt.list_price::numeric, 2) AS precio_venta,
    ROUND((COALESCE(SUM(sq.quantity), 0) * COALESCE((
        SELECT prop.value_float 
        FROM ir_property prop 
        WHERE prop.name = 'standard_price' 
          AND prop.res_id = 'product.product,' || pp.id 
        LIMIT 1
    ), 0.0))::numeric, 2) AS valor_inventario,
    COALESCE((
        SELECT SUM(pol.product_qty - pol.qty_received)
        FROM purchase_order_line pol
        JOIN purchase_order po ON po.id = pol.order_id
        WHERE pol.product_id = pp.id 
          AND po.state IN ('purchase', 'done')
          AND pol.product_qty > pol.qty_received
    ), 0) AS cantidad_por_recibir
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pc.id = pt.categ_id
LEFT JOIN stock_quant sq ON sq.product_id = pp.id 
  AND sq.location_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
LEFT JOIN stock_warehouse_orderpoint op ON op.product_id = pp.id
WHERE pt.default_code LIKE 'PROD-%'
GROUP BY pt.id, pt.default_code, pt.name, pc.name, op.id, op.product_min_qty, op.product_max_qty, pt.list_price, pp.id
ORDER BY pt.default_code;

-- 4. Vista: Ranking de Productos más Vendidos (v_bi_top_productos)
-- Totaliza unidades e ingresos por producto y calcula su posición de ranking densa.
CREATE OR REPLACE VIEW v_bi_top_productos AS
SELECT 
    pt.default_code AS codigo_producto,
    COALESCE(pt.name->>'es_GT', pt.name->>'en_US') AS producto,
    pc.name AS categoria,
    COALESCE(SUM(sol.product_uom_qty), 0) AS unidades_vendidas,
    ROUND(COALESCE(SUM(sol.price_subtotal), 0)::numeric, 2) AS ingresos,
    DENSE_RANK() OVER (ORDER BY COALESCE(SUM(sol.price_subtotal), 0) DESC) AS ranking
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pc.id = pt.categ_id
LEFT JOIN sale_order_line sol ON sol.product_id = pp.id AND sol.state IN ('sale', 'done')
LEFT JOIN sale_order so ON so.id = sol.order_id AND so.state IN ('sale', 'done')
WHERE pt.default_code LIKE 'PROD-%'
GROUP BY pt.id, pt.default_code, pt.name, pc.name
ORDER BY ingresos DESC;

-- 5. Vista: Gestión de Compras y Proveedores (v_bi_compras)
-- Registro de compras históricas y recepciones de mercancía.
CREATE OR REPLACE VIEW v_bi_compras AS
SELECT 
    po.name AS orden,
    po.date_order::date AS fecha,
    rp.name AS proveedor,
    COALESCE(pt.name->>'es_GT', pt.name->>'en_US') AS producto,
    pol.product_qty AS cantidad,
    pol.qty_received AS cantidad_recibida,
    ROUND(pol.price_subtotal::numeric, 2) AS subtotal,
    po.state AS estado
FROM purchase_order po
JOIN purchase_order_line pol ON pol.order_id = po.id
JOIN res_partner rp ON rp.id = po.partner_id
JOIN product_product pp ON pp.id = pol.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id
ORDER BY po.date_order DESC;

-- 6. Concesión de permisos al rol de Business Intelligence
GRANT SELECT ON v_bi_ventas_detalle TO bi_reader;
GRANT SELECT ON v_bi_inventario TO bi_reader;
GRANT SELECT ON v_bi_top_productos TO bi_reader;
GRANT SELECT ON v_bi_compras TO bi_reader;
