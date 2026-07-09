"""
Capítulo 1: Tests de Hipótesis (T-Test y Jarque-Bera)
"""
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats
from statsmodels.stats.stattools import jarque_bera

# Descargar datos
print("Descargando datos...")
ticker = yf.Ticker("EURGBP=X")
df = ticker.history(period="60d", interval="5m")
df['log_retorno'] = np.log(df['Close'] / df['Close'].shift(1))
df.dropna(inplace=True)

# Simular retornos de una estrategia (ejemplo)
np.random.seed(42)
retornos_estrategia = df['log_retorno'] * 1.5 + 0.0001

print("\n=== T-TEST: ¿ES REAL EL RETORNO? ===")
t_stat, p_valor = stats.ttest_1samp(retornos_estrategia, 0)
p_valor_una_cola = p_valor / 2 if t_stat > 0 else 1 - (p_valor / 2)

print(f"Estadístico t: {t_stat:.4f}")
print(f"P-valor (dos colas): {p_valor:.6f}")
print(f"P-valor (una cola): {p_valor_una_cola:.6f}")

if p_valor_una_cola < 0.05:
    print("\n✓ El retorno es estadísticamente significativo (95% confianza)")
else:
    print("\n✗ No podemos confirmar que el retorno sea real")

print("\n=== TEST DE JARQUE-BERA: ¿NORMALIDAD? ===")
jb_stat, jb_p_valor, _, _ = jarque_bera(df['log_retorno'].dropna())

print(f"Estadístico JB: {jb_stat:.2f}")
print(f"P-valor: {jb_p_valor:.6f}")

if jb_p_valor < 0.05:
    print("\n⚠️  Los retornos NO son normales (colas gordas)")
    print("Ajusta tu gestión de riesgo: eventos extremos son más probables")
else:
    print("\n✓ Los retornos son consistentes con distribución normal")
