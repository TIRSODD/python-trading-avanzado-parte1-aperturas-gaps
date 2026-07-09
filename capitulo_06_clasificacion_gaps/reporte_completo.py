"""
Capítulo 6: Clasificación y Medición de Gaps
Script: Reporte completo y análisis de propiedades estadísticas
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from clasificacion_gaps import clasificar_todos_los_gaps

def calcular_gaps_apertura(df):
    """Calcula los gaps de apertura para cada sesión."""
    gaps = []
    fechas_ordenadas = sorted(df.index.date)
    for i, fecha in enumerate(fechas_ordenadas):
        if i == 0: continue
        grupo = df[df.index.date == fecha]
        if len(grupo) == 0: continue
        open_hoy = grupo['close'].iloc[0]
        fecha_anterior = fechas_ordenadas[i - 1]
        grupo_anterior = df[df.index.date == fecha_anterior]
        if len(grupo_anterior) == 0: continue
        close_ayer = grupo_anterior['close'].iloc[-1]
        gap_absoluto = open_hoy - close_ayer
        gaps.append({
            'fecha': fecha, 'open': open_hoy, 'close_anterior': close_ayer,
            'gap_absoluto': gap_absoluto, 'gap_pips': gap_absoluto * 10000
        })
    df_gaps = pd.DataFrame(gaps)
    if len(df_gaps) > 0: df_gaps.set_index('fecha', inplace=True)
    return df_gaps

def analizar_frecuencia_por_dia_semana(df_gaps):
    """Analiza si hay patrones de gaps según el día de la semana."""
    print("=== FRECUENCIA DE GAPS POR DÍA DE LA SEMANA ===\n")
    df_gaps['dia_semana'] = pd.to_datetime(df_gaps.index).dayofweek
    dias_nombres = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes'}
    print(f"{'Día':<12} {'Total':>8} {'Gaps >2pip':>12} {'Frecuencia':>12}")
    print("-" * 50)
    for dia_num, dia_nombre in dias_nombres.items():
        subset = df_gaps[df_gaps['dia_semana'] == dia_num]
        total = len(subset)
        gaps_sig = len(subset[subset['gap_pips'].abs() > 2.0])
        frecuencia = 100 * gaps_sig / total if total > 0 else 0
        print(f"{dia_nombre:<12} {total:>8} {gaps_sig:>12} {frecuencia:>11.1f}%")

def analizar_autocorrelacion_gaps(df_gaps):
    """Analiza si hay autocorrelación en la serie de gaps."""
    print("\n=== AUTOCORRELACIÓN DE GAPS ===\n")
    tamaños = df_gaps['gap_pips'].abs()
    acf_values = []
    for lag in range(1, 11):
        acf_values.append(tamaños.autocorr(lag=lag))
    print("Autocorrelación por lag (días):")
    for i, acf in enumerate(acf_values, 1):
        print(f"  Lag {i}: {acf:.4f}")

def analizar_persistencia_gaps(df_gaps, umbral_grande=10):
    """Analiza si los gaps grandes tienden a agruparse."""
    print("\n=== PERSISTENCIA DE GAPS GRANDES ===\n")
    df_gaps['es_grande'] = df_gaps['gap_pips'].abs() > umbral_grande
    indices_grandes = df_gaps[df_gaps['es_grande']].index
    if len(indices_grandes) < 2:
        print("No hay suficientes gaps grandes para analizar"); return
    dias_entre_gaps = [(indices_grandes[i] - indices_grandes[i-1]).days for i in range(1, len(indices_grandes))]
    dias_entre_gaps = np.array(dias_entre_gaps)
    print(f"Total gaps grandes (> {umbral_grande} pips): {len(indices_grandes)}")
    print(f"Días entre gaps grandes consecutivos:")
    print(f"  Media: {dias_entre_gaps.mean():.1f} días")
    print(f"  Mediana: {np.median(dias_entre_gaps):.1f} días")

def reporte_completo_gaps(df, nombre_instrumento='EUR/GBP'):
    """Genera un reporte completo de análisis de gaps para un instrumento."""
    print(f"\n{'='*70}")
    print(f"REPORTE COMPLETO DE ANÁLISIS DE GAPS - {nombre_instrumento}")
    print(f"{'='*70}\n")
    
    print("1. CALCULANDO GAPS BÁSICOS...")
    df_gaps = calcular_gaps_apertura(df)
    
    print("\n2. CLASIFICACIÓN POR TIPO...")
    df_gaps_clasificados = clasificar_todos_los_gaps(df_gaps, df)
    
    print("\n3. FRECUENCIA POR DÍA DE LA SEMANA...")
    analizar_frecuencia_por_dia_semana(df_gaps)
    
    print("\n4. AUTOCORRELACIÓN...")
    analizar_autocorrelacion_gaps(df_gaps)
    
    print("\n5. PERSISTENCIA...")
    analizar_persistencia_gaps(df_gaps)
    
    print(f"\n{'='*70}")
    print(f"FIN DEL REPORTE - {nombre_instrumento}")
    print(f"{'='*70}\n")
    return df_gaps, df_gaps_clasificados

# Uso
# df_gaps, df_gaps_clasificados = reporte_completo_gaps(df_eurgbp, 'EUR/GBP')
