-- Ajuste fino de fechas historicas para DEMO-SEED en TechCore_DB
DO $$
DECLARE
    r RECORD;
    v_fecha TIMESTAMP;
    v_fecha_date DATE;
BEGIN
    FOR r IN (SELECT id FROM sale_order WHERE client_order_ref = 'DEMO-SEED' ORDER BY id) LOOP
        v_fecha := (CURRENT_DATE - ((75 - r.id) * 1.15)::int * INTERVAL '1 day' + (9 + (r.id % 9)) * INTERVAL '1 hour' + (r.id * 7 % 60) * INTERVAL '1 minute');
        v_fecha_date := v_fecha::date;

        -- 1. Actualizar orden de venta
        UPDATE sale_order SET date_order = v_fecha WHERE id = r.id;

        -- 2. Actualizar albaranes y movimientos
        UPDATE stock_picking 
        SET date_done = v_fecha, scheduled_date = v_fecha 
        WHERE sale_id = r.id;

        UPDATE stock_move 
        SET date = v_fecha 
        WHERE picking_id IN (SELECT id FROM stock_picking WHERE sale_id = r.id);

        UPDATE stock_move_line 
        SET date = v_fecha 
        WHERE picking_id IN (SELECT id FROM stock_picking WHERE sale_id = r.id);

        -- 3. Actualizar facturas y lineas contables
        UPDATE account_move 
        SET date = v_fecha_date, invoice_date = v_fecha_date 
        WHERE id IN (
            SELECT DISTINCT move_id 
            FROM account_move_line aml 
            JOIN sale_order_line_invoice_rel rel ON rel.invoice_line_id = aml.id
            JOIN sale_order_line sol ON sol.id = rel.order_line_id
            WHERE sol.order_id = r.id
        );

        UPDATE account_move_line 
        SET date = v_fecha_date 
        WHERE move_id IN (
            SELECT DISTINCT move_id 
            FROM account_move_line aml 
            JOIN sale_order_line_invoice_rel rel ON rel.invoice_line_id = aml.id
            JOIN sale_order_line sol ON sol.id = rel.order_line_id
            WHERE sol.order_id = r.id
        );
    END LOOP;
END
$$;
