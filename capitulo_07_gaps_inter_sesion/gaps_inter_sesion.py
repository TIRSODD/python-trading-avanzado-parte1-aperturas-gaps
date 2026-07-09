"""
Capítulo 7: Gaps Inter-Sesión y Estrategias
Script: Análisis de transiciones, gaps overnight y probabilidad de llenado
"""
import pandas as pd
import numpy as np

def analizar_transiciones_sesion(df):
    """Analiza el comportamiento del precio en las transiciones entre sesiones."""
    transiciones = {
        'Asia_Londres': ('06:30', '07:30'),
        'Londres_NY': ('12:30', '13:30'),
        'NY_Asia': ('21:30', '22:30')
    }
    resultados = {}
    for nombre, (inicio, fin) in transiciones.items():
        df_trans = df.between_time(inicio, fin)
        if len(df_trans) == 0:
            continue
        volumen_prom = df_trans['volume'].mean()
        volatilidad = (df_trans['high'] - df_trans['low']).mean()
        df_trans['cambio'] = df_trans['close'].diff().abs()
        atr = df_trans['high'].rolling(14).max() - df_trans['low'].rolling(14).min()
        atr_prom = atr.mean()
        gaps = (df_trans['cambio'] > 2 * atr_prom).sum() if not pd.isna(atr_prom) else 0
        frecuencia_gaps = gaps / len(df_trans) * 100 if len(df_trans) > 0 else 0
        resultados[nombre] = {
            'volumen': volumen_prom,
            'volatilidad': volatilidad,
            'frecuencia_gaps': frecuencia_gaps
        }
    return resultados

def calcular_gaps_overnight(df):
    """Calcula los gaps que ocurren entre sesiones (overnight)."""
    gaps_overnight = []
    fechas_ordenadas = sorted(df.index.date)
    
    for i, fecha in enumerate(fechas_ordenadas):
        if i == 0:
            continue
        grupo = df[df.index.date == fecha]
        if len(grupo) == 0:
            continue
            
        fecha_anterior = fechas_ordenadas[i - 1]
        grupo_anterior = df[df.index.date == fecha_anterior]
        if len(grupo_anterior) == 0:
            continue
            
        close_anterior = grupo_anterior['close'].iloc[-1]
        timestamp_cierre = grupo_anterior.index[-1]
        open_hoy = grupo['open'].iloc[0]
        timestamp_apertura = grupo.index[0]
        
        gap_absoluto = open_hoy - close_anterior
        gap_porcentual = (gap_absoluto / close_anterior) * 100
        gap_pips = gap_absoluto * 10000
        tiempo_horas = (timestamp_apertura - timestamp_cierre).total_seconds() / 3600
        
        gaps_overnight.append({
            'fecha': fecha,
            'timestamp_cierre': timestamp_cierre,
            'timestamp_apertura': timestamp_apertura,
            'close_anterior': close_anterior,
            'open_hoy': open_hoy,
            'gap_absoluto': gap_absoluto,
            'gap_porcentual': gap_porcentual,
            'gap_pips': gap_pips,
            'tiempo_horas': tiempo_horas
        })
        
    df_gaps = pd.DataFrame(gaps_overnight)
    if len(df_gaps) > 0:
        df_gaps.set_index('fecha', inplace=True)
    return df_gaps

def analizar_gaps_overnight(df_gaps, umbral_minimo_pips=2.0):
    """Analiza estadísticamente los gaps overnight."""
    df_gaps_sig = df_gaps[df_gaps['gap_pips'].abs() > umbral_minimo_pips]
    print("=== ANÁLISIS DE GAPS OVERNIGHT ===\n")
    print(f"Total de sesiones analizadas: {len(df_gaps)}")
    print(f"Gaps overnight significativos (>{umbral_minimo_pips} pips): {len(df_gaps_sig)}")
    print(f"Porcentaje de días con gap overnight: {100*len(df_gaps_sig)/len(df_gaps):.1f}%\n")
    
    if len(df_gaps_sig) > 0:
        print("Estadísticas de gaps overnight (en pips):")
        print(f"  Media: {df_gaps_sig['gap_pips'].mean():.2f}")
        print(f"  Mediana: {df_gaps_sig['gap_pips'].median():.2f}")
        print(f"  Desviación estándar: {df_gaps_sig['gap_pips'].std():.2f}")
    return df_gaps_sig

def analizar_llenado_gaps_overnight(df, df_gaps, horas_maximas=12):
    """Analiza qué porcentaje de gaps overnight se llenan y en cuánto tiempo."""
    df_gaps_sig = df_gaps[df_gaps['gap_pips'].abs() > 2.0]
    resultados = []
    
    for fecha, gap in df_gaps_sig.iterrows():
        timestamp_inicio = gap['timestamp_apertura']
        timestamp_fin = timestamp_inicio + pd.Timedelta(hours=horas_maximas)
        datos_post = df[(df.index >= timestamp_inicio) & (df.index <= timestamp_fin)]
        
        if len(datos_post) == 0:
            continue
            
        nivel_referencia = gap['close_anterior']
        gap_alcista = gap['gap_pips'] > 0
        llenado = False
        tiempo_llenado = None
        
        for timestamp, vela in datos_post.iterrows():
            if timestamp == timestamp_inicio:
                continue
            if gap_alcista and vela['low'] <= nivel_referencia:
                llenado = True
                tiempo_llenado = (timestamp - timestamp_inicio).total_seconds() / 3600
                break
            elif not gap_alcista and vela['high'] >= nivel_referencia:
                llenado = True
                tiempo_llenado = (timestamp - timestamp_inicio).total_seconds() / 3600
                break
                
        resultados.append({
            'fecha': fecha,
            'gap_pips': gap['gap_pips'],
            'gap_alcista': gap_alcista,
            'llenado': llenado,
            'tiempo_llenado_horas': tiempo_llenado
        })
        
    df_resultados = pd.DataFrame(resultados)
    if len(df_resultados) > 0:
        total_gaps = len(df_resultados)
        gaps_llenados = df_resultados['llenado'].sum()
        porcentaje_llenado = 100 * gaps_llenados / total_gaps
        print("\n=== ANÁLISIS DE LLENADO DE GAPS OVERNIGHT ===\n")
        print(f"Total gaps overnight analizados: {total_gaps}")
        print(f"Gaps llenados: {gaps_llenados} ({porcentaje_llenado:.1f}%)")
        
    return df_resultados
