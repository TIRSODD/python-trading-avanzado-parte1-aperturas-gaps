"""
Capítulo 6: Clasificación y Medición de Gaps
Script: Clasificación de gaps en 4 tipos fundamentales
"""
import pandas as pd
import numpy as np

def calcular_niveles_soporte_resistencia(df, ventana=50, num_niveles=5):
    """Calcula niveles de soporte y resistencia usando máximos y mínimos locales."""
    niveles = []
    for i in range(ventana, len(df) - ventana):
        ventana_datos = df.iloc[i-ventana:i+ventana+1]
        if df.iloc[i]['high'] == ventana_datos['high'].max():
            niveles.append(df.iloc[i]['high'])
        if df.iloc[i]['low'] == ventana_datos['low'].min():
            niveles.append(df.iloc[i]['low'])
            
    niveles_unicos = []
    niveles = sorted(niveles)
    for nivel in niveles:
        if len(niveles_unicos) == 0:
            niveles_unicos.append([nivel])
        else:
            ultimo_grupo = niveles_unicos[-1]
            if abs(nivel - np.mean(ultimo_grupo)) < 0.0050:
                ultimo_grupo.append(nivel)
            else:
                niveles_unicos.append([nivel])
                
    niveles_finales = [np.mean(grupo) for grupo in niveles_unicos]
    return niveles_finales[-num_niveles:]

def clasificar_gap_comun(df_gaps, df, ventana_volumen=20, umbral_tamaño=5):
    """Identifica gaps comunes: pequeños, en mercado lateral, se llenan rápido."""
    gaps_comunes = []
    for fecha, gap in df_gaps.iterrows():
        if abs(gap['gap_pips']) > umbral_tamaño:
            continue
        datos_historicos = df[df.index.date < fecha].tail(ventana_volumen)
        if len(datos_historicos) == 0:
            continue
        ma = datos_historicos['close'].mean()
        precio_anterior = gap['close_anterior']
        distancia_a_ma = abs(precio_anterior - ma) / ma * 100
        if distancia_a_ma > 1.0:
            continue
        volumen_actual = df[df.index.date == fecha]['volume'].iloc[0]
        volumen_promedio = datos_historicos['volume'].mean()
        if volumen_promedio == 0:
            continue
        ratio_volumen = volumen_actual / volumen_promedio
        if ratio_volumen > 1.5:
            continue
        gaps_comunes.append({
            'fecha': fecha, 'gap_pips': gap['gap_pips'], 'tipo': 'comun',
            'ratio_volumen': ratio_volumen, 'distancia_a_ma': distancia_a_ma
        })
    return pd.DataFrame(gaps_comunes)

def clasificar_gap_ruptura(df_gaps, df, niveles_sr, umbral_tamaño=8, multiplicador_volumen=2.0):
    """Identifica gaps de ruptura: rompen niveles clave con volumen alto."""
    gaps_ruptura = []
    for fecha, gap in df_gaps.iterrows():
        if abs(gap['gap_pips']) < umbral_tamaño:
            continue
        precio_anterior = gap['close_anterior']
        precio_actual = gap['open']
        rompe_nivel = False
        nivel_roto = None
        for nivel in niveles_sr:
            if gap['gap_pips'] > 0 and precio_anterior < nivel < precio_actual:
                rompe_nivel = True; nivel_roto = nivel; break
            elif gap['gap_pips'] < 0 and precio_anterior > nivel > precio_actual:
                rompe_nivel = True; nivel_roto = nivel; break
        if not rompe_nivel:
            continue
        datos_historicos = df[df.index.date < fecha].tail(20)
        volumen_actual = df[df.index.date == fecha]['volume'].iloc[0]
        volumen_promedio = datos_historicos['volume'].mean()
        if volumen_promedio == 0:
            continue
        ratio_volumen = volumen_actual / volumen_promedio
        if ratio_volumen < multiplicador_volumen:
            continue
        gaps_ruptura.append({
            'fecha': fecha, 'gap_pips': gap['gap_pips'], 'tipo': 'ruptura',
            'ratio_volumen': ratio_volumen, 'nivel_roto': nivel_roto
        })
    return pd.DataFrame(gaps_ruptura)

def clasificar_gap_continuacion(df_gaps, df, periodos_ma=50, umbral_tendencia=2.0, umbral_tamaño=5):
    """Identifica gaps de continuación: ocurren en tendencias fuertes."""
    gaps_continuacion = []
    df['ma'] = df['close'].rolling(periodos_ma).mean()
    df['pendiente_ma'] = df['ma'].diff(10) / df['ma'].shift(10) * 100
    
    for fecha, gap in df_gaps.iterrows():
        if abs(gap['gap_pips']) < umbral_tamaño:
            continue
        datos_historicos = df[df.index.date <= fecha]
        if len(datos_historicos) < periodos_ma:
            continue
        pendiente = datos_historicos['pendiente_ma'].iloc[-1]
        if pd.isna(pendiente) or abs(pendiente) < umbral_tendencia:
            continue
        gap_alcista = gap['gap_pips'] > 0
        tendencia_alcista = pendiente > 0
        if gap_alcista != tendencia_alcista:
            continue
        volumen_actual = df[df.index.date == fecha]['volume'].iloc[0]
        volumen_promedio = df[df.index.date < fecha].tail(20)['volume'].mean()
        if volumen_promedio == 0:
            continue
        ratio_volumen = volumen_actual / volumen_promedio
        if ratio_volumen < 1.5:
            continue
        gaps_continuacion.append({
            'fecha': fecha, 'gap_pips': gap['gap_pips'], 'tipo': 'continuacion',
            'ratio_volumen': ratio_volumen, 'pendiente_tendencia': pendiente
        })
    return pd.DataFrame(gaps_continuacion)

def clasificar_gap_agotamiento(df_gaps, df, periodos_ma=50, umbral_tamaño=10, umbral_volumen=3.0):
    """Identifica gaps de agotamiento: al final de tendencias, volumen extremo."""
    gaps_agotamiento = []
    df['ma'] = df['close'].rolling(periodos_ma).mean()
    df['pendiente_ma'] = df['ma'].diff(10) / df['ma'].shift(10) * 100
    
    for fecha, gap in df_gaps.iterrows():
        if abs(gap['gap_pips']) < umbral_tamaño:
            continue
        datos_historicos = df[df.index.date <= fecha]
        if len(datos_historicos) < periodos_ma:
            continue
        pendiente = datos_historicos['pendiente_ma'].iloc[-1]
        if pd.isna(pendiente) or abs(pendiente) < 2.0:
            continue
        volumen_actual = df[df.index.date == fecha]['volume'].iloc[0]
        volumen_promedio = df[df.index.date < fecha].tail(20)['volume'].mean()
        if volumen_promedio == 0:
            continue
        ratio_volumen = volumen_actual / volumen_promedio
        if ratio_volumen < umbral_volumen:
            continue
        gap_alcista = gap['gap_pips'] > 0
        tendencia_alcista = pendiente > 0
        if gap_alcista != tendencia_alcista:
            continue
        gaps_agotamiento.append({
            'fecha': fecha, 'gap_pips': gap['gap_pips'], 'tipo': 'agotamiento',
            'ratio_volumen': ratio_volumen, 'pendiente_tendencia': pendiente
        })
    return pd.DataFrame(gaps_agotamiento)

def clasificar_todos_los_gaps(df_gaps, df, niveles_sr=None):
    """Clasifica todos los gaps en los cuatro tipos."""
    print("=== CLASIFICACIÓN DE GAPS ===\n")
    if niveles_sr is None:
        niveles_sr = calcular_niveles_soporte_resistencia(df)
        
    gaps_comunes = clasificar_gap_comun(df_gaps, df)
    gaps_ruptura = clasificar_gap_ruptura(df_gaps, df, niveles_sr)
    gaps_continuacion = clasificar_gap_continuacion(df_gaps, df)
    gaps_agotamiento = clasificar_gap_agotamiento(df_gaps, df)
    
    todos_los_gaps = pd.concat([
        gaps_comunes.assign(tipo='comun'),
        gaps_ruptura.assign(tipo='ruptura'),
        gaps_continuacion.assign(tipo='continuacion'),
        gaps_agotamiento.assign(tipo='agotamiento')
    ])
    
    print(f"Total gaps clasificados: {len(todos_los_gaps)}")
    print(f"\nDistribución por tipo:")
    for tipo in ['comun', 'ruptura', 'continuacion', 'agotamiento']:
        subset = todos_los_gaps[todos_los_gaps['tipo'] == tipo]
        print(f"  {tipo.capitalize()}: {len(subset)} ({100*len(subset)/len(todos_los_gaps):.1f}%)")
        
    return todos_los_gaps
