USE MayaCodeDB;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

TRUNCATE TABLE dbo.Staging_Actividad;
GO

BULK INSERT dbo.Staging_Actividad
FROM '/data/practica1.csv'
WITH (
    FORMAT          = 'CSV',
    FIRSTROW        = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR   = '0x0a',
    FIELDQUOTE      = '"',
    TABLOCK
);
GO

-- Evidencia para el informe
SELECT COUNT(*) AS filas_cargadas FROM dbo.Staging_Actividad;

SELECT
    SUM(CASE WHEN [name] IS NULL OR LTRIM(RTRIM([name])) = '' THEN 1 ELSE 0 END) AS nombres_vacios,
    SUM(CASE WHEN [year]  IS NULL THEN 1 ELSE 0 END) AS anios_nulos,
    SUM(CASE WHEN [count] IS NULL THEN 1 ELSE 0 END) AS conteos_nulos,
    MIN([year]) AS anio_min, MAX([year]) AS anio_max,
    COUNT(DISTINCT LTRIM(RTRIM([name]))) AS lenguajes_distintos
FROM dbo.Staging_Actividad;

SELECT LTRIM(RTRIM([name])) AS lenguaje, [year], [quarter], COUNT(*) AS repeticiones
FROM dbo.Staging_Actividad
GROUP BY LTRIM(RTRIM([name])), [year], [quarter]
HAVING COUNT(*) > 1;
GO