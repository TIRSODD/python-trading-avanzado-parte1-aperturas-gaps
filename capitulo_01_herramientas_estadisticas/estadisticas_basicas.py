"""
Capítulo 1: Herramientas Estadísticas para Análisis Intradía
Script: Análisis básico de retornos y momentos estadísticos
"""
import numpy as np
import pandas as pd
import yfinance as yf

# Descargar datos de ejemplo
print("Descargando datos de EUR/GBP...")
ticker = yf.Ticker("EURGBP=X")
df = ticker.history(period="60d", interval="5m")

# Calcular log-retornos
df['log_retorno'] = np.log(df['Close'] / df['Close'].shift(1))
df.dropna(inplace=True)

# Cuatro momentos estadísticos
print("\n=== MOMENTOS ESTADÍSTICOS ===")
print(f"Media (rendimiento esperado): {df['log_retorno'].mean():.6f}")
print(f"Desviación estándar (riesgo): {df['log_retorno'].std():.6f}")
print(f"Asimetría (Skewness): {df['log_retorno'].skew():.4f}")
print(f"Curtosis: {df['log_retorno'].kurtosis():.4f}")
print(f"Curtosis normal (referencia): 0.0")

if df['log_retorno'].kurtosis() > 3:
    print("\n⚠️  ALERTA: Colas gordas detectadas")
    print("Los eventos extremos ocurren con más frecuencia de lo normal")
else:
    print("\n✓ Distribución cercana a la normal")
