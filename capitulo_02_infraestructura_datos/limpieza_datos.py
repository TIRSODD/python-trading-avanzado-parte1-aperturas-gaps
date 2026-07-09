"""
Capítulo 2: Infraestructura de Datos
Script: Limpieza y preprocesamiento de datos intradía
"""
import pandas as pd
import numpy as np
import yfinance as yf

def detectar_outliers(df, columna='Close', umbral_z=5):
    """Detecta outliers usando Z-score."""
    media = df[columna].mean()
    std = df[columna].std()
    df['z_score'] = (df[columna] - media) / std
    df['es_outlier'] = df['z_score'].abs() > umbral_z
    outliers = df[df['es_outlier']]
    print(f"Detectados {len(outliers)} valores atípicos ({100*len(outliers)/len(df):.2f}%)")
    return df

def verificar_integridad(df, frecuencia='5min'):
    """Verifica que no haya huecos en la serie temporal."""
    indice_completo = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=frecuencia
    )
    df_completo = df.reindex(indice_completo)
    huecos = df_completo[df_completo['Close'].isna()]
    print(f"Períodos esperados: {len(indice_completo)}")
    print(f"Períodos con datos: {len(df)}")
    print(f"Huecos detectados: {len(huecos)}")
    return df_completo, huecos

def unificar_zona_horaria(df, zona_origen='UTC', zona_destino='Europe/Madrid'):
    """Convierte el índice a la zona horaria deseada."""
    if df.index.tz is None:
        df.index = df.index.tz_localize(zona_origen)
    df.index = df.index.tz_convert(zona_destino)
    print(f"Zona horaria final: {df.index.tz}")
    return df

# Uso de ejemplo
if __name__ == "__main__":
    ticker = yf.Ticker("EURGBP=X")
    df = ticker.history(period="7d", interval="5m")
    
    print("=== DETECCIÓN DE OUTLIERS ===")
    df = detectar_outliers(df)
    
    print("\n=== INTEGRIDAD TEMPORAL ===")
    df_completo, huecos = verificar_integridad(df)
    
    print("\n=== ZONA HORARIA ===")
    df = unificar_zona_horaria(df)
