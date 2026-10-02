USE MayaCodeDB;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

/* ============ PASO 3: DIMENSIONES (idempotente) ============ */
INSERT INTO dbo.Dim_Lenguaje (nombre)
SELECT DISTINCT LTRIM(RTRIM(s.[name]))
FROM dbo.Staging_Actividad s
WHERE s.[name] IS NOT NULL
  AND LTRIM(RTRIM(s.[name])) <> ''
  AND NOT EXISTS (SELECT 1 FROM dbo.Dim_Lenguaje l
                  WHERE l.nombre = LTRIM(RTRIM(s.[name])));
GO

INSERT INTO dbo.Dim_Periodo (anio, trimestre)
SELECT DISTINCT s.[year], s.[quarter]
FROM dbo.Staging_Actividad s
WHERE s.[year] IS NOT NULL AND s.[quarter] IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM dbo.Dim_Periodo p
                  WHERE p.anio = s.[year] AND p.trimestre = s.[quarter]);
GO

/* ============ PASO 4: TABLA DE HECHOS (agregada) ============ */
DELETE FROM dbo.Hecho_Actividad;
GO

INSERT INTO dbo.Hecho_Actividad (id_lenguaje, id_periodo, conteo)
SELECT l.id_lenguaje, p.id_periodo, SUM(ISNULL(s.[count], 0))
FROM dbo.Staging_Actividad s
JOIN dbo.Dim_Lenguaje l ON l.nombre = LTRIM(RTRIM(s.[name]))
JOIN dbo.Dim_Periodo  p ON p.anio = s.[year] AND p.trimestre = s.[quarter]
GROUP BY l.id_lenguaje, p.id_periodo;
GO

/* ============ VISTA BASE ============ */
CREATE OR ALTER VIEW dbo.vw_Actividad AS
SELECT l.id_lenguaje, l.nombre AS lenguaje,
       p.anio, p.trimestre, h.conteo
FROM dbo.Hecho_Actividad h
JOIN dbo.Dim_Lenguaje l ON l.id_lenguaje = h.id_lenguaje
JOIN dbo.Dim_Periodo  p ON p.id_periodo  = h.id_periodo;
GO

/* ---- R1: Top 10 MÁS usados 2011–2022 ---- */
CREATE OR ALTER VIEW dbo.vw_Top10_Mas_Usados AS
SELECT TOP 10
       ROW_NUMBER() OVER (ORDER BY SUM(conteo) DESC) AS ranking,
       lenguaje,
       SUM(conteo) AS total_actividad,
       CAST(100.0 * SUM(conteo)
            / (SELECT SUM(conteo) FROM dbo.vw_Actividad WHERE anio BETWEEN 2011 AND 2022)
            AS DECIMAL(6,3)) AS porcentaje_participacion
FROM dbo.vw_Actividad
WHERE anio BETWEEN 2011 AND 2022
GROUP BY lenguaje
ORDER BY total_actividad DESC;
GO

/* ---- R2: Top 10 MENOS usados 2011–2022 ---- */
-- Criterio: solo lenguajes con actividad > 0 y presencia en al menos 4 trimestres,
-- para no premiar registros anecdóticos de un solo trimestre.
CREATE OR ALTER VIEW dbo.vw_Top10_Menos_Usados AS
SELECT TOP 10
       ROW_NUMBER() OVER (ORDER BY SUM(conteo) ASC) AS ranking,
       lenguaje,
       SUM(conteo) AS total_actividad,
       COUNT(*)    AS trimestres_con_registro
FROM dbo.vw_Actividad
WHERE anio BETWEEN 2011 AND 2022
GROUP BY lenguaje
HAVING SUM(conteo) > 0 AND COUNT(*) >= 4
ORDER BY total_actividad ASC;
GO

/* ---- R3: Top 5 con más actividad en Q4-2022 ---- */
CREATE OR ALTER VIEW dbo.vw_Top5_Q4_2022 AS
SELECT TOP 5
       ROW_NUMBER() OVER (ORDER BY SUM(conteo) DESC) AS ranking,
       lenguaje,
       SUM(conteo) AS actividad_q4_2022
FROM dbo.vw_Actividad
WHERE anio = 2022 AND trimestre = 4
GROUP BY lenguaje
ORDER BY actividad_q4_2022 DESC;
GO

/* ---- R4: Top 5 del último trimestre ---- */

CREATE OR ALTER VIEW dbo.vw_Top5_Ultimo_Trimestre AS
SELECT TOP 5
       ROW_NUMBER() OVER (ORDER BY SUM(conteo) DESC) AS ranking,
       lenguaje, anio, trimestre,
       SUM(conteo) AS actividad
FROM dbo.vw_Actividad
WHERE (anio * 10 + trimestre) = (SELECT MAX(anio * 10 + trimestre) FROM dbo.vw_Actividad)
GROUP BY lenguaje, anio, trimestre
ORDER BY actividad DESC;
GO