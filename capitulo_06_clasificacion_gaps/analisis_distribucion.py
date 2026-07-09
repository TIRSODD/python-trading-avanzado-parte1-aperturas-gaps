"""
Capítulo 6: Clasificación y Medición de Gaps
Script: Análisis de distribución y recomendaciones
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def analizar_distribucion_tamanos(df_gaps):
    """Analiza la distribución estadística del tamaño de los gaps."""
    tamaños = df_gaps['gap_pips'].abs()
    print("=== DISTRIBUCIÓN DEL TAMAÑO DE GAPS ===\n")
    print("Estadísticas básicas (en pips):")
    print(f"  Media: {tamaños.mean():.2f}")
    print(f"  Mediana: {tamaños.median():.2f}")
    print(f"  Desviación estándar: {tamaños.std():.2f}")
    print(f"  Asimetría: {tamaños.skew():.2f}")
    print(f"  Curtosis: {tamaños.kurtosis():.2f}\n")
    
    print("Percentiles:")
    for p in [25, 50, 75, 90, 95, 99]:
        print(f"  P{p}: {tamaños.quantile(p / 100):.2f} pips")
        
    stat, p_value = stats.jarque_bera(tamaños)
    print(f"\nTest de Jarque-Bera:")
    print(f"  Estadístico: {stat:.2f}")
    print(f"  P-valor: {p_value:.6f}")
    if p_value < 0.05:
        print("  → Los tamaños NO siguen distribución normal (colas gordas)")
    else:
        print("  → Los tamaños son consistentes con distribución normal")
    return tamaños

def comparar_tamanos_por_tipo(df_gaps_clasificados):
    """Compara la distribución de tamaños entre los diferentes tipos de gaps."""
    print("=== COMPARACIÓN DE TAMAÑOS POR TIPO DE GAP ===\n")
    tipos = ['comun', 'ruptura', 'continuacion', 'agotamiento']
    print(f"{'Tipo':<15} {'Media':>10} {'Mediana':>10} {'Std':>10}")
    print("-" * 50)
    
    for tipo in tipos:
        subset = df_gaps_clasificados[df_gaps_clasificados['tipo'] == tipo]
        if len(subset) == 0:
            continue
        tamaños = subset['gap_pips'].abs()
        print(f"{tipo.capitalize():<15} {tamaños.mean():>10.2f} {tamaños.median():>10.2f} {tamaños.std():>10.2f}")

def recomendar_estrategia_segun_tamaño(df_gaps_clasificados):
    """Recomienda tipo de estrategia según el tamaño del gap."""
    print("=== RECOMENDACIONES POR TAMAÑO DE GAP ===\n")
    tamaños = df_gaps_clasificados['gap_pips'].abs()
    p25 = tamaños.quantile(0.25)
    p75 = tamaños.quantile(0.75)
    p90 = tamaños.quantile(0.90)
    
    print(f"Gap pequeño (< P25 = {p25:.1f} pips):")
    print("  → Estrategia recomendada: GAP FADE")
    print("  → Alta probabilidad de llenado (>80%)\n")
    
    print(f"Gap moderado (P25-P75 = {p25:.1f}-{p75:.1f} pips):")
    print("  → Estrategia recomendada: Depende del tipo\n")
    
    print(f"Gap grande (> P75 = {p75:.1f} pips):")
    print("  → Estrategia recomendada: MOMENTUM")
    print("  → Baja probabilidad de llenado (<50%)\n")
    
    print(f"Gap extremo (> P90 = {p90:.1f} pips):")
    print("  → Estrategia recomendada: PRECAUCIÓN EXTREMA")
