"""
Capítulo 1: Test de Estacionariedad (Dickey-Fuller Aumentado)
"""
import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller

# Descargar datos
print("Descargando datos...")
ticker = yf.Ticker("EURGBP=X")
df = ticker.history(period="60d", interval="5m")

# Calcular log-retornos
df['log_retorno'] = np.log(df['Close'] / df['Close'].shift(1))
df.dropna(inplace=True)

# Test ADF
print("\n=== TEST DE DICKEY-FULLER AUMENTADO ===")
resultado = adfuller(df['log_retorno'].dropna())

print(f"Estadístico ADF: {resultado[0]:.4f}")
print(f"P-valor: {resultado[1]:.6f}")
print(f"Lags usados: {resultado[2]}")
print(f"Observaciones: {resultado[3]}")

print("\nValores críticos:")
for key, value in resultado[4].items():
    print(f"  {key}: {value:.4f}")

p_valor = resultado[1]
if p_valor <= 0.05:
    print("\n✓ La serie ES estacionaria (p-valor < 0.05)")
    print("Podemos aplicar modelos ARIMA, GARCH, etc.")
else:
    print("\n✗ La serie NO es estacionaria (p-valor >= 0.05)")
    print("Necesitamos diferenciar o transformar los datos")
