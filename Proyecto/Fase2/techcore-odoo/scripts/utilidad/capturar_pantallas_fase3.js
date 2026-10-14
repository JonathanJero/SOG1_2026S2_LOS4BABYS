const puppeteer = require('/tmp/puppeteer-capture/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = '/Users/jona/Desktop/USAC/4to_Anio/8vo Semestre/GERENCIALES/LAB/Practicas/P1/SOG1_2026S2_LOS4BABYS/Proyecto/Fase3/docu/capturas';
const BASE_URL = 'http://192.168.64.11:8069';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function run() {
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1400,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1400, height: 900 });

    console.log('1. Capturando portada...');
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_01_portada_ecommerce.jpg'), quality: 85 });

    console.log('2. Capturando catalogo de tienda...');
    await page.goto(`${BASE_URL}/shop`, { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_02_catalogo_tienda.jpg'), quality: 85 });

    console.log('3. Capturando ficha de producto...');
    const prodLink = await page.$('a[itemprop="name"]');
    if (prodLink) {
        await prodLink.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
        await sleep(2500);
        await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_03_ficha_producto.jpg'), quality: 85 });
    }

    console.log('4. Capturando formulario de registro...');
    await page.goto(`${BASE_URL}/web/signup`, { waitUntil: 'networkidle2' });
    await sleep(2000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_04_registro_cliente.jpg'), quality: 85 });

    console.log('5. Autenticando admin para capturar portal y CRM...');
    await page.goto(`${BASE_URL}/web/login`, { waitUntil: 'networkidle2' });
    await sleep(1500);
    await page.type('#login', 'admin@techcore.gt');
    await page.type('#password', '1234');
    await page.click('.oe_login_buttons button');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    await sleep(3500);

    console.log('6. Capturando portal /my...');
    await page.goto(`${BASE_URL}/my`, { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_07_portal_cliente.jpg'), quality: 85 });

    console.log('7. Capturando mis pedidos /my/orders...');
    await page.goto(`${BASE_URL}/my/orders`, { waitUntil: 'networkidle2' });
    await sleep(2500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_05_carrito_compras.jpg'), quality: 85 });

    console.log('8. Capturando CRM Kanban...');
    await page.goto(`${BASE_URL}/web#action=crm.crm_lead_action_pipeline`, { waitUntil: 'networkidle2' });
    await sleep(4500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_08_crm_oportunidades_web.jpg'), quality: 85 });

    console.log('9. Capturando metodos de pago...');
    await page.goto(`${BASE_URL}/web#action=payment.action_payment_provider`, { waitUntil: 'networkidle2' });
    await sleep(4000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'jonathan_f3_06_pasarela_pago.jpg'), quality: 85 });

    await browser.close();
    console.log('Capturas completadas con exito.');
}

run().catch(err => {
    console.error('Error durante captura:', err);
    process.exit(1);
});
