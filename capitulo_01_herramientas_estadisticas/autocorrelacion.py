"""
Capítulo 1: Análisis de Autocorrelación (ACF)
"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

# Descargar datos
print("Descargando datos...")
ticker = yf.Ticker("EURGBP=X")
df = ticker.history(period="60d", interval="5m")
df['log_retorno'] = np.log(df['Close'] / df['Close'].shift(1))
df.dropna(inplace=True)

# Gráfico ACF
plt.figure(figsize=(12, 5))
plot_acf(df['log_retorno'], lags=40, alpha=0.05)
plt.title('Autocorrelación de Log-Retornos EUR/GBP')
plt.xlabel('Lag (períodos)')
plt.ylabel('Autocorrelación')
plt.tight_layout()
plt.savefig('acf_retornos.png', dpi=150)
print("\n✓ Gráfico guardado: acf_retornos.png")

# Interpretación
acf_values = df['log_retorno'].autocorr(lag=1)
print(f"\nAutocorrelación lag 1: {acf_values:.4f}")

if abs(acf_values) > 0.05:
    print("→ Existe dependencia estadística en los retornos")
    print("→ Posible oportunidad para estrategias de momentum")
else:
    print("→ Los retornos se comportan como ruido blanco")
    print("→ Las estrategias de momentum tendrán dificultades")
