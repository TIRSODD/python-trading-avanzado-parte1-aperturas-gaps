"""
Capítulo 5: Estrategias Gap Fade
Script: Generación de señales y gestión de riesgo
"""
import pandas as pd
import numpy as np

def generar_señales_gap_fade(df, df_candidates):
    """Genera señales de entrada para estrategia Gap Fade."""
    señales = []
    for _, candidate in df_candidates.iterrows():
        fecha = candidate['fecha']
        datos_dia = df[df.index.date == fecha]
        if len(datos_dia) == 0:
            continue
            
        precio_entrada = datos_dia['Close'].iloc[0]
        timestamp_entrada = datos_dia.index[0]
        nivel_objetivo = candidate['close_anterior']
        
        if candidate['gap_alcista']:
            direccion = 'short'
            distancia_objetivo = (precio_entrada - nivel_objetivo) * 10000
        else:
            direccion = 'long'
            distancia_objetivo = (nivel_objetivo - precio_entrada) * 10000
            
        señales.append({
            'fecha': fecha,
            'timestamp_entrada': timestamp_entrada,
            'direccion': direccion,
            'precio_entrada': precio_entrada,
            'nivel_objetivo': nivel_objetivo,
            'gap_pips': candidate['gap_pips'],
            'distancia_objetivo_pips': distancia_objetivo
        })
        
    df_señales = pd.DataFrame(señales)
    print(f"\nTotal señales generadas: {len(df_señales)}")
    return df_señales

def calcular_niveles_salida(df_señales, multiplicador_stop=1.5, max_horas=8):
    """Calcula stop-loss y time-stop para cada señal."""
    señales_completas = []
    for _, señal in df_señales.iterrows():
        gap_size = abs(señal['gap_pips'])
        
        if señal['direccion'] == 'long':
            stop_loss = señal['precio_entrada'] - (gap_size / 10000) * multiplicador_stop
        else:
            stop_loss = señal['precio_entrada'] + (gap_size / 10000) * multiplicador_stop
            
        señal_completa = señal.copy()
        señal_completa['stop_loss'] = stop_loss
        señal_completa['stop_loss_pips'] = gap_size * multiplicador_stop
        señal_completa['tiempo_maximo_horas'] = max_horas
        señales_completas.append(señal_completa)
        
    return pd.DataFrame(señales_completas)

def calcular_tamaño_posicion_fade(señales, capital, riesgo_porcentaje=1.0):
    """Calcula tamaño de posición basado en riesgo fijo."""
    señales_con_posicion = []
    riesgo_monetario = capital * (riesgo_porcentaje / 100)
    
    for _, señal in señales.iterrows():
        stop_pips = señal['stop_loss_pips']
        if stop_pips == 0:
            continue
            
        tamaño_lotes = riesgo_monetario / (stop_pips * 10)
        señal_con_posicion = señal.copy()
        señal_con_posicion['tamaño_lotes'] = round(tamaño_lotes, 2)
        señal_con_posicion['riesgo_usd'] = riesgo_monetario
        señales_con_posicion.append(señal_con_posicion)
        
    return pd.DataFrame(señales_con_posicion)
