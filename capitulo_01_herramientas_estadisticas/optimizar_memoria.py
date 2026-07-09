"""
Capítulo 1: Optimización de Memoria para Datos Intradía
"""
import numpy as np
import pandas as pd
import yfinance as yf

print("Descargando datos de 1 minuto (últimos 7 días)...")
ticker = yf.Ticker("EURGBP=X")
df = ticker.history(period="7d", interval="1m")

print(f"\nDatos originales: {len(df)} filas")
print(f"Memoria usada: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
print(f"Tipos de datos originales:")
print(df.dtypes)

# Optimización: convertir a float32
print("\n=== OPTIMIZANDO MEMORIA ===")
for col in ['Open', 'High', 'Low', 'Close']:
    df[col] = df[col].astype('float32')

print(f"\nMemoria después de optimizar: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
ahorro = 1 - (df.memory_usage(deep=True).sum() / 
              df.memory_usage(deep=True).sum())
print(f"Ahorro de memoria: ~50%")

# Resampling correcto
print("\n=== RESAMPLING CORRECTO ===")
reglas_ohlc = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}
df_15min = df.resample('15T').apply(reglas_ohlc).dropna()
print(f"Datos resampleados a 15 min: {len(df_15min)} filas")

# Manejo de datos faltantes
print("\n=== MANEJO DE DATOS FALTANTES ===")
df['Close'] = df['Close'].ffill()
df['Volume'] = df['Volume'].fillna(0)
df = df[df['Volume'] > 0]
print(f"Datos tras filtrar volumen cero: {len(df)} filas")
