"""
Capítulo 7: Gaps Inter-Sesión y Estrategias
Script: Implementación de estrategias de trading inter-sesión
"""
import pandas as pd
import numpy as np

def estrategia_gap_fade_overnight(df, df_gaps_overnight, capital=10000, riesgo_pct=1.0):
    """Estrategia de Gap Fade para gaps overnight."""
    df_gaps_sig = df_gaps_overnight[df_gaps_overnight['gap_pips'].abs().between(2, 8)]
    señales = []
    
    for fecha, gap in df_gaps_sig.iterrows():
        precio_entrada = gap['open_hoy']
        timestamp_entrada = gap['timestamp_apertura']
        nivel_objetivo = gap['close_anterior']
        
        if gap['gap_pips'] > 0:
            direccion = 'short'
        else:
            direccion = 'long'
            
        gap_size = abs(gap['gap_pips'])
        if direccion == 'long':
            stop_loss = precio_entrada - (gap_size / 10000) * 1.5
        else:
            stop_loss = precio_entrada + (gap_size / 10000) * 1.5
            
        riesgo_monetario = capital * (riesgo_pct / 100)
        stop_pips = gap_size * 1.5
        tamaño_lotes = riesgo_monetario / (stop_pips * 10) if stop_pips > 0 else 0
        
        señales.append({
            'fecha': fecha,
            'timestamp_entrada': timestamp_entrada,
            'direccion': direccion,
            'precio_entrada': precio_entrada,
            'nivel_objetivo': nivel_objetivo,
            'stop_loss': stop_loss,
            'gap_pips': gap['gap_pips'],
            'tamaño_lotes': round(tamaño_lotes, 2)
        })
        
    return pd.DataFrame(señales)

def estrategia_ruptura_rango_asia(df, capital=10000, riesgo_pct=1.0):
    """Estrategia de ruptura del rango de la sesión asiática."""
    señales = []
    for fecha, grupo in df.groupby(df.index.date):
        sesion_asia = grupo.between_time('00:00', '07:00')
        if len(sesion_asia) < 10:
            continue
            
        rango_high = sesion_asia['high'].max()
        rango_low = sesion_asia['low'].min()
        rango_size = rango_high - rango_low
        volumen_prom_asia = sesion_asia['volume'].mean()
        
        sesion_europa = grupo.between_time('07:00', '16:00')
        if len(sesion_europa) == 0:
            continue
            
        ruptura_detectada = False
        for timestamp, vela in sesion_europa.iterrows():
            if ruptura_detectada:
                break
            if vela['high'] > rango_high and vela['volume'] > volumen_prom_asia * 1.5:
                precio_entrada = rango_high
                stop_loss = rango_low
                take_profit = rango_high + (rango_size * 2)
                direccion = 'long'
                ruptura_detectada = True
            elif vela['low'] < rango_low and vela['volume'] > volumen_prom_asia * 1.5:
                precio_entrada = rango_low
                stop_loss = rango_high
                take_profit = rango_low - (rango_size * 2)
                direccion = 'short'
                ruptura_detectada = True
                
            if ruptura_detectada:
                riesgo_pips = abs(precio_entrada - stop_loss) * 10000
                riesgo_monetario = capital * (riesgo_pct / 100)
                tamaño_lotes = riesgo_monetario / (riesgo_pips * 10) if riesgo_pips > 0 else 0
                señales.append({
                    'fecha': fecha,
                    'timestamp_entrada': timestamp,
                    'direccion': direccion,
                    'precio_entrada': precio_entrada,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'rango_size': rango_size,
                    'tamaño_lotes': round(tamaño_lotes, 2)
                })
    return pd.DataFrame(señales)

def estrategia_momentum_overlap(df, capital=10000, riesgo_pct=1.0):
    """Estrategia de momentum en el overlap Londres-Nueva York."""
    señales = []
    for fecha, grupo in df.groupby(df.index.date):
        pre_overlap = grupo.between_time('11:00', '13:00')
        if len(pre_overlap) < 10:
            continue
            
        precio_inicio = pre_overlap['close'].iloc[0]
        precio_fin = pre_overlap['close'].iloc[-1]
        cambio = precio_fin - precio_inicio
        
        if abs(cambio) < 0.0010:
            continue
            
        direccion = 'long' if cambio > 0 else 'short'
        
        pre_overlap['tr'] = np.maximum(
            pre_overlap['high'] - pre_overlap['low'],
            np.maximum(
                abs(pre_overlap['high'] - pre_overlap['close'].shift(1)),
                abs(pre_overlap['low'] - pre_overlap['close'].shift(1))
            )
        )
        atr = pre_overlap['tr'].rolling(14).mean().iloc[-1]
        volumen_prom = pre_overlap['volume'].mean()
        
        overlap_inicio = grupo.between_time('13:00', '13:05')
        if len(overlap_inicio) == 0:
            continue
            
        primera_vela = overlap_inicio.iloc[0]
        if primera_vela['volume'] < volumen_prom * 2:
            continue
            
        precio_entrada = primera_vela['close']
        timestamp_entrada = primera_vela.name
        
        if direccion == 'long':
            stop_loss = precio_entrada - (atr * 1.5)
            take_profit = precio_entrada + (atr * 3)
        else:
            stop_loss = precio_entrada + (atr * 1.5)
            take_profit = precio_entrada - (atr * 3)
            
        riesgo_pips = abs(precio_entrada - stop_loss) * 10000
        riesgo_monetario = capital * (riesgo_pct / 100)
        tamaño_lotes = riesgo_monetario / (riesgo_pips * 10) if riesgo_pips > 0 else 0
        
        señales.append({
            'fecha': fecha,
            'timestamp_entrada': timestamp_entrada,
            'direccion': direccion,
            'precio_entrada': precio_entrada,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': atr,
            'tamaño_lotes': round(tamaño_lotes, 2)
        })
    return pd.DataFrame(señales)
