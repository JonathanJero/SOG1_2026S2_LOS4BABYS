#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de generación de PDF académico formal en blanco y negro para el Manual Técnico Consolidado de Fase 3.
Requerimientos estrictos:
- Tipografía: Times New Roman
- Interlineado: 1.5
- Estilo: Blanco y negro riguroso, formal universitario (USAC), sin estética de IA
- Manejo de saltos de página: evitar cortes de tablas, figuras, bloques de código y encabezados huérfanos.
- Imágenes embebidas en base64 para carga 100% garantizada en todas las 27 capturas.
- Sin encabezados/pies de página de navegador (sin fechas ni URLs en los bordes).
"""

import base64
import mimetypes
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE_DIR, "manual_tecnico_consolidado_fase3.md")
HTML_PATH = os.path.join(BASE_DIR, "manual_tecnico_consolidado_fase3.html")
PDF_PATH = os.path.join(BASE_DIR, "manual_tecnico_consolidado_fase3.pdf")
CAPTURAS_DIR = os.path.join(BASE_DIR, "capturas")

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def to_base64(path):
    if not os.path.exists(path):
        return None
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def main():
    print("Iniciando procesamiento de documento para conversion a PDF...")
    if not os.path.exists(MD_PATH):
        print(f"Error: No existe el archivo {MD_PATH}")
        sys.exit(1)

    # 1. Ejecutar marked para obtener el HTML base
    tmp_raw = "/tmp/marked_consolidado.html"
    cmd_marked = ["npx", "-y", "marked", MD_PATH, "-o", tmp_raw]
    res = subprocess.run(cmd_marked, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error ejecutando marked: {res.stderr}")
        sys.exit(1)

    with open(tmp_raw, "r", encoding="utf-8") as f:
        raw_html = f.read()

    # 2. Desempaquetar parrafos <p> que contienen imagenes y reemplazar en UNA sola pasada limpia
    def repl_img(m):
        src = m.group(1).strip()
        alt = m.group(2).strip()
        if src.startswith("data:"):
            return m.group(0)
        clean = src.replace("capturas/", "").strip()
        path = os.path.join(CAPTURAS_DIR, clean)
        if not os.path.exists(path):
            path = os.path.join(BASE_DIR, src)
        
        b64 = to_base64(path)
        if not b64:
            print(f"Advertencia: no se encontro la imagen: {path}")
            b64 = ""

        return (
            f'<div class="figure-container">\n'
            f'  <img src="{b64}" alt="{alt}" />\n'
            f'  <div class="figure-caption">{alt}</div>\n'
            f'</div>'
        )

    # Desenvolver imagenes de parrafos <p>
    html_unwrapped = re.sub(r'<p>\s*(<img[^>]+>)\s*</p>', r'\1', raw_html)
    html_unwrapped = re.sub(r'<p>((?:\s*<img[^>]+>\s*)+)</p>', r'\1', html_unwrapped)

    # Reemplazo de cada etiqueta <img> de forma unica
    processed_html = re.sub(
        r'<img\s+src="([^"]+)"\s+alt="([^"]*)"\s*/?>',
        repl_img,
        html_unwrapped
    )

    # 3. Remover el bloque inicial del markdown (se reemplazará por la portada formal)
    split_token = "<h2>Videos Demostrativos de Fase 3</h2>"
    if split_token in processed_html:
        parts = processed_html.split(split_token, 1)
        body_content = split_token + parts[1]
    else:
        body_content = processed_html

    # 4. Construcción de la Portada Formal Universitaria
    cover_html = """
    <div class="cover-page">
      <div class="cover-header">
        <div class="univ-title">UNIVERSIDAD DE SAN CARLOS DE GUATEMALA</div>
        <div class="fac-title">FACULTAD DE INGENIERÍA</div>
        <div class="esc-title">ESCUELA DE CIENCIAS Y SISTEMAS</div>
        <div class="course-title">SISTEMAS ORGANIZACIONALES Y GERENCIALES 1 — SECCIÓN A</div>
        <div class="term-title">SEGUNDO SEMESTRE 2026</div>
      </div>

      <div class="cover-divider-thick"></div>
      <div class="cover-divider-thin"></div>

      <div class="cover-main">
        <div class="doc-main-title">MANUAL TÉCNICO CONSOLIDADO DE FASE 3</div>
        <div class="doc-sub-title">E-Commerce, Integración ERP/CRM, Business Intelligence, Pruebas End-to-End y Escalabilidad</div>
        
        <div class="doc-project-box">
          <p><strong>EMPRESA:</strong> TECHCORE SOLUTIONS GUATEMALA</p>
          <p><strong>PROYECTO:</strong> TRANSFORMACIÓN DIGITAL EN E-COMMERCE CON ERP, CRM Y BI (QUETZALDEV)</p>
          <p><strong>FASE EVALUADA:</strong> FASE 3 — FINALIZACIÓN, OPTIMIZACIÓN Y ANÁLISIS FINAL</p>
          <p><strong>PONDERACIÓN:</strong> 100 PUNTOS</p>
        </div>
      </div>

      <div class="cover-team-section">
        <div class="team-title">GRUPO NO. 7 — INTEGRANTES DEL EQUIPO</div>
        <table class="cover-table">
          <thead>
            <tr>
              <th style="width: 44%;">Nombre del Estudiante</th>
              <th style="width: 20%; text-align: center;">Carnet</th>
              <th style="width: 36%;">Rol y Especialidad</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Jonathan Eliud Jerónimo Salguero</strong></td>
              <td style="text-align: center;">202300353</td>
              <td>Infraestructura, E-Commerce y Consolidación</td>
            </tr>
            <tr>
              <td><strong>Francisco Gerardo Castillo Sagastume</strong></td>
              <td style="text-align: center;">202300653</td>
              <td>Ingeniería de Datos y Business Intelligence</td>
            </tr>
            <tr>
              <td><strong>Julio Alfredo Herrera Orantes</strong></td>
              <td style="text-align: center;">202300850</td>
              <td>Aseguramiento de Calidad, Pruebas y Cierre</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="cover-footer">
        <div>Ciudad de Guatemala, Guatemala</div>
        <div>Octubre de 2026</div>
      </div>
    </div>
    """

    # 5. CSS Formal Académico Blanco y Negro
    academic_css = """
    @page {
      size: letter;
      margin: 18mm 18mm 18mm 18mm;
    }

    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    body {
      font-family: "Times New Roman", Times, "Nimbus Roman No9 L", serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #000000;
      background-color: #ffffff;
      margin: 0;
      padding: 0;
    }

    /* Portada Formal */
    .cover-page {
      page-break-after: always;
      break-after: page;
      text-align: center;
      padding-top: 5mm;
      padding-bottom: 5mm;
    }

    .cover-header {
      margin-bottom: 12pt;
    }

    .univ-title {
      font-size: 13.5pt;
      font-weight: bold;
      letter-spacing: 0.5pt;
      margin-bottom: 2pt;
    }

    .fac-title {
      font-size: 12pt;
      font-weight: bold;
      margin-bottom: 2pt;
    }

    .esc-title {
      font-size: 11pt;
      font-weight: bold;
      margin-bottom: 2pt;
    }

    .course-title {
      font-size: 10.5pt;
      font-weight: bold;
      margin-bottom: 1pt;
    }

    .term-title {
      font-size: 10pt;
      font-style: italic;
    }

    .cover-divider-thick {
      border-top: 2pt solid #000000;
      margin-top: 10pt;
      margin-bottom: 2pt;
    }

    .cover-divider-thin {
      border-top: 0.75pt solid #000000;
      margin-bottom: 16pt;
    }

    .cover-main {
      margin: 10pt 0 16pt 0;
    }

    .doc-main-title {
      font-size: 15.5pt;
      font-weight: bold;
      letter-spacing: 0.5pt;
      line-height: 1.25;
      margin-bottom: 6pt;
    }

    .doc-sub-title {
      font-size: 11pt;
      font-style: italic;
      line-height: 1.35;
      margin-bottom: 14pt;
      max-width: 90%;
      margin-left: auto;
      margin-right: auto;
    }

    .doc-project-box {
      border: 1pt solid #000000;
      padding: 8pt 14pt;
      margin: 10pt auto 16pt auto;
      max-width: 90%;
      text-align: left;
      font-size: 9.5pt;
      line-height: 1.4;
      background: #fafafa;
    }

    .doc-project-box p {
      margin: 2pt 0;
      text-align: left;
    }

    .cover-team-section {
      margin: 12pt 0 16pt 0;
    }

    .team-title {
      font-size: 10.5pt;
      font-weight: bold;
      letter-spacing: 0.5pt;
      margin-bottom: 6pt;
    }

    .cover-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 9.5pt;
      margin: 0 auto;
      border-top: 1.25pt solid #000000;
      border-bottom: 1.25pt solid #000000;
    }

    .cover-table th {
      border-bottom: 1pt solid #000000;
      padding: 4pt 5pt;
      background: #f0f0f0;
      font-weight: bold;
      text-align: left;
    }

    .cover-table td {
      border-bottom: 0.5pt solid #cccccc;
      padding: 3.5pt 5pt;
      text-align: left;
    }

    .cover-footer {
      font-size: 9.5pt;
      font-weight: bold;
      line-height: 1.35;
      margin-top: 18pt;
      border-top: 0.75pt solid #666666;
      padding-top: 6pt;
    }

    /* Tipografía de Contenido */
    h1 {
      font-size: 13pt;
      font-weight: bold;
      text-transform: uppercase;
      border-bottom: 1.25pt solid #000000;
      padding-bottom: 2pt;
      margin-top: 16pt;
      margin-bottom: 6pt;
      page-break-after: avoid;
      break-after: avoid;
      line-height: 1.25;
    }

    h2 {
      font-size: 11.5pt;
      font-weight: bold;
      border-bottom: 0.5pt solid #444444;
      padding-bottom: 1.5pt;
      margin-top: 13pt;
      margin-bottom: 5pt;
      page-break-after: avoid;
      break-after: avoid;
      line-height: 1.25;
    }

    h3 {
      font-size: 10.5pt;
      font-weight: bold;
      font-style: italic;
      margin-top: 9pt;
      margin-bottom: 3pt;
      page-break-after: avoid;
      break-after: avoid;
      line-height: 1.25;
    }

    h4 {
      font-size: 10pt;
      font-weight: bold;
      margin-top: 8pt;
      margin-bottom: 2pt;
      page-break-after: avoid;
      break-after: avoid;
    }

    p {
      text-align: justify;
      text-justify: inter-word;
      margin-top: 0;
      margin-bottom: 5.5pt;
      orphans: 3;
      widows: 3;
    }

    ul, ol {
      margin-top: 0;
      margin-bottom: 5.5pt;
      padding-left: 18pt;
    }

    li {
      margin-bottom: 2pt;
      text-align: justify;
    }

    /* Tablas Académicas */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 8pt 0;
      font-size: 8.5pt;
      line-height: 1.28;
      page-break-inside: avoid;
      break-inside: avoid;
      border-top: 1.25pt solid #000000;
      border-bottom: 1.25pt solid #000000;
    }

    th {
      border-bottom: 1pt solid #000000;
      padding: 3.5pt 4.5pt;
      background-color: #f0f0f0;
      font-weight: bold;
      text-align: left;
    }

    td {
      border-bottom: 0.5pt solid #d0d0d0;
      padding: 3pt 4.5pt;
      vertical-align: top;
      text-align: left;
    }

    tr {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* Figuras e Imágenes en Blanco y Negro */
    .figure-container {
      page-break-inside: avoid;
      break-inside: avoid;
      margin: 8pt auto;
      text-align: center;
      max-width: 100%;
    }

    .figure-container img {
      display: block;
      margin: 0 auto;
      max-width: 88%;
      max-height: 235px;
      object-fit: contain;
      border: 0.75pt solid #333333;
      padding: 1.5pt;
      background: #ffffff;
      filter: grayscale(100%) contrast(108%);
    }

    .figure-caption {
      font-size: 8.5pt;
      font-style: italic;
      color: #111111;
      margin-top: 2.5pt;
      text-align: center;
      page-break-after: avoid;
      break-after: avoid;
    }

    /* Diagramas ASCII y Bloques de Código */
    pre {
      background: #f7f7f7;
      border: 0.75pt solid #333333;
      padding: 5pt 7pt;
      font-family: "Courier New", Courier, monospace;
      font-size: 7.2pt;
      line-height: 1.2;
      page-break-inside: avoid;
      break-inside: avoid;
      overflow-x: hidden;
      white-space: pre;
      margin: 6pt 0;
      color: #000000;
    }

    code {
      font-family: "Courier New", Courier, monospace;
      font-size: 8.5pt;
      background: #f0f0f0;
      padding: 1pt 2pt;
      border: 0.5pt solid #cccccc;
      border-radius: 1.5pt;
      color: #000000;
    }

    pre code {
      background: transparent;
      padding: 0;
      border: none;
      font-size: inherit;
    }

    blockquote {
      border-left: 2pt solid #000000;
      margin: 7pt 0 7pt 14pt;
      padding-left: 9pt;
      font-style: italic;
      page-break-inside: avoid;
      break-inside: avoid;
    }

    hr {
      border: none;
      border-top: 0.75pt solid #666666;
      margin: 12pt 0;
    }

    a {
      color: #000000;
      text-decoration: underline;
    }
    """

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Manual Técnico Consolidado de Fase 3 — TechCore Solutions</title>
  <style>
{academic_css}
  </style>
</head>
<body>
{cover_html}
<div class="content-body">
{body_content}
</div>
</body>
</html>
"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"HTML intermedio generado en: {HTML_PATH}")

    # 6. Ejecución de Chrome Headless con --no-pdf-header-footer
    chrome_cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--allow-file-access-from-files",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]

    print("Compilando PDF con Google Chrome Headless...")
    res = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error al compilar PDF: {res.stderr}")
        sys.exit(1)

    print(f"PDF generado exitosamente en: {PDF_PATH}")
    size = os.path.getsize(PDF_PATH)
    print(f"Tamaño del PDF: {size:,} bytes ({size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
