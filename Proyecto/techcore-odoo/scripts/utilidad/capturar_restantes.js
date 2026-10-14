const puppeteer = require('/tmp/puppeteer-capture/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = '/Users/jona/Desktop/USAC/4to_Anio/8vo Semestre/GERENCIALES/LAB/Practicas/P1/SOG1_2026S2_LOS4BABYS/Proyecto/Fase3/docu/capturas';
const BASE_URL = 'http://192.168.64.11:8069';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1400,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1400, height: 900 });

    // 1. Carrito de compras /shop/cart
    console.log('Capturando carrito...');
    try {
        await page.goto(`${BASE_URL}/shop`, { waitUntil: 'networkidle2' });
        await sleep(2000);
        // Entrar al primer producto y añadir al carrito
        const prodLink = await page.$('a[itemprop="name"]');
        if (prodLink) {
            await prodLink.click();
            await sleep(3000);
            const addBtn = await page.$('#add_to_cart');
            if (addBtn) {
                await addBtn.click();
                await sleep(3000);
            }
        }
        await page.goto(`${BASE_URL}/shop/cart`, { waitUntil: 'networkidle2' });
        await sleep(2500);
        await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_05_carrito_compras.jpg'), quality: 85 });
        console.log('[OK] jonathan_f3_05_carrito_compras.jpg');
    } catch (e) {
        console.error('Error carrito:', e);
    }

    // 2. Login de admin
    console.log('Autenticando admin...');
    await page.goto(`${BASE_URL}/web/login`, { waitUntil: 'networkidle2' });
    await sleep(2000);
    await page.type('#login', 'admin@techcore.gt');
    await page.type('#password', '1234');
    await page.click('.oe_login_buttons button');
    await sleep(5000);

    // 3. Pasarela de pago en Odoo
    console.log('Capturando proveedores de pago...');
    try {
        await page.goto(`${BASE_URL}/web#action=payment.action_payment_provider`, { waitUntil: 'networkidle2' });
        await sleep(5000);
        await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_06_pasarela_pago.jpg'), quality: 85 });
        console.log('[OK] jonathan_f3_06_pasarela_pago.jpg');
    } catch (e) {
        console.error('Error pago:', e);
    }

    // 4. CRM Pipeline con Oportunidades Web
    console.log('Capturando CRM Pipeline...');
    try {
        await page.goto(`${BASE_URL}/web#action=crm.crm_lead_action_pipeline`, { waitUntil: 'networkidle2' });
        await sleep(5000);
        await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_08_crm_oportunidades_web.jpg'), quality: 85 });
        console.log('[OK] jonathan_f3_08_crm_oportunidades_web.jpg');
    } catch (e) {
        console.error('Error CRM:', e);
    }

    await browser.close();
    console.log('Completado.');
}

run();
