"""
Capítulo 5: Estrategias Gap Fade
Script: Análisis estadístico y filtrado de gaps de apertura
"""
import pandas as pd
import numpy as np

def calcular_gaps_apertura(df):
    """Calcula los gaps de apertura para cada sesión."""
    gaps = []
    fechas_ordenadas = sorted(df.index.date)
    
    for i, fecha in enumerate(fechas_ordenadas):
        if i == 0:
            continue
            
        grupo = df[df.index.date == fecha]
        if len(grupo) == 0:
            continue
            
        open_hoy = grupo['Close'].iloc[0]
        fecha_anterior = fechas_ordenadas[i - 1]
        grupo_anterior = df[df.index.date == fecha_anterior]
        
        if len(grupo_anterior) == 0:
            continue
            
        close_ayer = grupo_anterior['Close'].iloc[-1]
        gap_absoluto = open_hoy - close_ayer
        gap_porcentual = (gap_absoluto / close_ayer) * 100
        
        gaps.append({
            'fecha': fecha,
            'open': open_hoy,
            'close_anterior': close_ayer,
            'gap_absoluto': gap_absoluto,
            'gap_porcentual': gap_porcentual,
            'gap_pips': gap_absoluto * 10000
        })
        
    df_gaps = pd.DataFrame(gaps)
    if len(df_gaps) > 0:
        df_gaps.set_index('fecha', inplace=True)
    return df_gaps

def analizar_estadisticas_gaps(df_gaps, umbral_minimo_pips=2.0):
    """Analiza estadísticas de los gaps, filtrando los demasiado pequeños."""
    df_gaps_sig = df_gaps[df_gaps['gap_pips'].abs() > umbral_minimo_pips]
    
    print("=== ANÁLISIS ESTADÍSTICO DE GAPS ===\n")
    print(f"Total de sesiones analizadas: {len(df_gaps)}")
    print(f"Gaps significativos (>{umbral_minimo_pips} pips): {len(df_gaps_sig)}")
    print(f"Porcentaje de días con gap: {100*len(df_gaps_sig)/len(df_gaps):.1f}%\n")
    
    if len(df_gaps_sig) > 0:
        print("Estadísticas de gaps (en pips):")
        print(f"  Media: {df_gaps_sig['gap_pips'].mean():.2f}")
        print(f"  Mediana: {df_gaps_sig['gap_pips'].median():.2f}")
        print(f"  Desviación estándar: {df_gaps_sig['gap_pips'].std():.2f}")
        
    return df_gaps_sig

def filtrar_gaps_para_fade(df, df_gaps, df_gaps_sig, 
                           max_gap_pips=15, max_ratio_volumen=2.5,
                           periodos_ma_tendencia=100):
    """Filtra gaps que son candidatos para estrategia fade."""
    candidates = []
    df['ma_tendencia'] = df['Close'].rolling(periodos_ma_tendencia).mean()
    
    for fecha, gap in df_gaps_sig.iterrows():
        if abs(gap['gap_pips']) > max_gap_pips:
            continue
            
        datos_dia = df[df.index.date == fecha]
        if len(datos_dia) == 0:
            continue
            
        primera_vela = datos_dia.iloc[0]
        volumen_promedio = df[df.index.date < fecha]['Volume'].tail(20).mean()
        ratio_volumen = primera_vela['Volume'] / volumen_promedio if volumen_promedio > 0 else 0
        
        if ratio_volumen > max_ratio_volumen:
            continue
            
        precio_actual = primera_vela['Close']
        ma_actual = df.loc[df.index.date == fecha, 'ma_tendencia']
        if len(ma_actual) == 0 or pd.isna(ma_actual.iloc[0]):
            continue
        ma_actual = ma_actual.iloc[0]
        
        gap_alcista = gap['gap_pips'] > 0
        if gap_alcista and precio_actual < ma_actual:
            continue
        if not gap_alcista and precio_actual > ma_actual:
            continue
            
        candidates.append({
            'fecha': fecha,
            'gap_pips': gap['gap_pips'],
            'gap_alcista': gap_alcista,
            'open': gap['open'],
            'close_anterior': gap['close_anterior'],
            'ratio_volumen': ratio_volumen
        })
        
    df_candidates = pd.DataFrame(candidates)
    print(f"=== FILTRADO DE GAPS PARA FADE ===\n")
    print(f"Gaps significativos: {len(df_gaps_sig)}")
    print(f"Candidatos para fade: {len(df_candidates)}")
    
    return df_candidates
