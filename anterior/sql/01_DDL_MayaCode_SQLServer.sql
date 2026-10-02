-- =============================================================================
-- PRÁCTICA 1: SISTEMAS GERENCIALES / LABORATORIO
-- RESPONSABLE: Jonathan (Rol A - Arquitecto de Base de Datos y Modelado)
-- MOTOR DE BASE DE DATOS: Microsoft SQL Server (T-SQL)
-- =============================================================================

-- 1. CREACIÓN DE LA BASE DE DATOS
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'MayaCodeDB')
BEGIN
    CREATE DATABASE MayaCodeDB;
END
GO

USE MayaCodeDB;
GO
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

-- =============================================================================
-- 2. TABLA STAGING (PREPARACIÓN PARA ROL B - CARGA MASIVA)
-- Tabla plana sin restricciones complejas para recibir la carga bruta (BULK INSERT)
-- =============================================================================
IF OBJECT_ID('dbo.Staging_Actividad', 'U') IS NOT NULL 
    DROP TABLE dbo.Staging_Actividad;
GO

CREATE TABLE dbo.Staging_Actividad (
    name VARCHAR(150) NULL,
    year INT NULL,
    quarter INT NULL,
    count BIGINT NULL
);
GO

-- =============================================================================
-- 3. CREACIÓN DEL MODELO RELACIONAL (ESQUEMA ESTRELLA / NORMALIZADO EN 3NF)
-- =============================================================================

-- Eliminar tablas relacionales si ya existen (en orden inverso a dependencias FK)
IF OBJECT_ID('dbo.Hecho_Actividad', 'U') IS NOT NULL 
    DROP TABLE dbo.Hecho_Actividad;
GO

IF OBJECT_ID('dbo.Dim_Periodo', 'U') IS NOT NULL 
    DROP TABLE dbo.Dim_Periodo;
GO

IF OBJECT_ID('dbo.Dim_Lenguaje', 'U') IS NOT NULL 
    DROP TABLE dbo.Dim_Lenguaje;
GO

-- -----------------------------------------------------------------------------
-- 3.1. ENTIDAD: Dim_Lenguaje (Dimensión de Lenguajes de Programación)
-- -----------------------------------------------------------------------------
CREATE TABLE dbo.Dim_Lenguaje (
    id_lenguaje INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT PK_Dim_Lenguaje PRIMARY KEY CLUSTERED (id_lenguaje),
    CONSTRAINT UQ_Lenguaje_Nombre UNIQUE NONCLUSTERED (nombre)
);
GO

-- -----------------------------------------------------------------------------
-- 3.2. ENTIDAD: Dim_Periodo (Dimensión Temporal por Año y Trimestre)
-- -----------------------------------------------------------------------------
CREATE TABLE dbo.Dim_Periodo (
    id_periodo INT IDENTITY(1,1) NOT NULL,
    anio SMALLINT NOT NULL,
    trimestre TINYINT NOT NULL,
    -- Campo computado y persistido para facilitar reportes en SQL y Power BI (ej. "Q3-2011")
    codigo_periodo AS (CAST(('Q' + CAST(trimestre AS VARCHAR(2)) + '-' + CAST(anio AS VARCHAR(4))) AS VARCHAR(15))) PERSISTED,
    CONSTRAINT PK_Dim_Periodo PRIMARY KEY CLUSTERED (id_periodo),
    CONSTRAINT CHK_Trimestre CHECK (trimestre BETWEEN 1 AND 4),
    CONSTRAINT CHK_Anio CHECK (anio >= 1900 AND anio <= 2100),
    CONSTRAINT UQ_Anio_Trimestre UNIQUE NONCLUSTERED (anio, trimestre)
);
GO

-- -----------------------------------------------------------------------------
-- 3.3. ENTIDAD: Hecho_Actividad (Tabla de Hechos - Registro de Uso de Lenguajes)
-- -----------------------------------------------------------------------------
CREATE TABLE dbo.Hecho_Actividad (
    id_actividad BIGINT IDENTITY(1,1) NOT NULL,
    id_lenguaje INT NOT NULL,
    id_periodo INT NOT NULL,
    conteo BIGINT NOT NULL,
    CONSTRAINT PK_Hecho_Actividad PRIMARY KEY CLUSTERED (id_actividad),
    CONSTRAINT FK_Hecho_Lenguaje FOREIGN KEY (id_lenguaje) 
        REFERENCES dbo.Dim_Lenguaje(id_lenguaje)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_Hecho_Periodo FOREIGN KEY (id_periodo) 
        REFERENCES dbo.Dim_Periodo(id_periodo)
        ON DELETE CASCADE ON UPDATE CASCADE,
    -- Evita duplicidad de registros del mismo lenguaje en el mismo trimestre y año
    CONSTRAINT UQ_Lenguaje_Periodo UNIQUE NONCLUSTERED (id_lenguaje, id_periodo),
    CONSTRAINT CHK_Conteo_Positivo CHECK (conteo >= 0)
);
GO

-- =============================================================================
-- 4. CREACIÓN DE ÍNDICES NO AGRUPADOS (OPTIMIZACIÓN PARA CONSULTAS Y POWER BI)
-- =============================================================================
-- Índice para acelerar los JOINs y agrupaciones por lenguaje de programación
CREATE NONCLUSTERED INDEX IX_Hecho_Actividad_Lenguaje ON dbo.Hecho_Actividad(id_lenguaje)
INCLUDE (conteo, id_periodo);
GO

-- Índice para acelerar filtros temporales y JOINs por periodo (ej. Q4-2022 o tendencias)
CREATE NONCLUSTERED INDEX IX_Hecho_Actividad_Periodo ON dbo.Hecho_Actividad(id_periodo)
INCLUDE (conteo, id_lenguaje);
GO


