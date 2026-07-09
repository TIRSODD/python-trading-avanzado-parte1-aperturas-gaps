"""
Capítulo 4: Estrategias ORB
Script: Cálculo de rangos, detección y filtrado de rupturas
"""
import pandas as pd
import numpy as np

def calcular_opening_range_multiple(df, minutos_ranges=[5, 15, 30, 60], hora_apertura='07:00'):
    """Calcula el Opening Range para múltiples temporalidades."""
    resultados = []
    # Ajustar la hora de apertura según el activo (07:00 UTC para Londres en Forex)
    for fecha, grupo in df.groupby(df.index.date):
        sesion = grupo[grupo.index.time >= pd.to_datetime(hora_apertura).time()]
        if len(sesion) == 0:
            continue
        primer_timestamp = sesion.index[0]
        for minutos in minutos_ranges:
            fin_ventana = primer_timestamp + pd.Timedelta(minutes=minutos)
            ventana = sesion[sesion.index <= fin_ventana]
            if len(ventana) == 0:
                continue
            rango_data = {
                'fecha': fecha,
                'temporalidad': minutos,
                'high': ventana['High'].max(),
                'low': ventana['Low'].min(),
                'open': ventana['Open'].iloc[0],
                'close': ventana['Close'].iloc[-1],
                'rango': ventana['High'].max() - ventana['Low'].min(),
                'volumen': ventana['Volume'].sum()
            }
            resultados.append(rango_data)
    df_ranges = pd.DataFrame(resultados)
    if len(df_ranges) > 0:
        df_ranges.set_index('fecha', inplace=True)
    return df_ranges

def detectar_rupturas_volumen(df, ranges, temporalidad=15, multiplicador_volumen=1.5):
    """Detecta rupturas confirmadas por volumen superior al promedio."""
    señales = []
    for fecha, rango in ranges[ranges['temporalidad'] == temporalidad].iterrows():
        fin_rango = df.index[df.index.date == fecha][0] + pd.Timedelta(minutes=temporalidad)
        resto_sesion = df[(df.index.date == fecha) & (df.index > fin_rango)]
        if len(resto_sesion) == 0:
            continue
        volumen_promedio = rango['volumen'] / temporalidad
        ruptura_detectada = False
        for timestamp, vela in resto_sesion.iterrows():
            if not ruptura_detectada:
                if vela['High'] > rango['high'] and vela['Volume'] > volumen_promedio * multiplicador_volumen:
                    señales.append({'fecha': fecha, 'timestamp': timestamp, 'tipo': 'alcista', 'precio_entrada': rango['high']})
                    ruptura_detectada = True
                elif vela['Low'] < rango['low'] and vela['Volume'] > volumen_promedio * multiplicador_volumen:
                    señales.append({'fecha': fecha, 'timestamp': timestamp, 'tipo': 'bajista', 'precio_entrada': rango['low']})
                    ruptura_detectada = True
    return pd.DataFrame(señales)

def filtrar_rupturas_distancia(señales, ranges, porcentaje_minimo=0.1):
    """Filtra rupturas que no superan el rango por un margen mínimo."""
    if len(señales) == 0:
        return señales
    señales_filtradas = []
    for _, señal in señales.iterrows():
        rango = ranges[(ranges.index == señal['fecha']) & (ranges['temporalidad'] == 15)]
        if len(rango) == 0:
            continue
        rango = rango.iloc[0]
        tamaño_rango = rango['rango']
        margen_minimo = tamaño_rango * (porcentaje_minimo / 100)
        if señal['tipo'] == 'alcista' and señal['precio_entrada'] > rango['high'] + margen_minimo:
            señales_filtradas.append(señal)
        elif señal['tipo'] == 'bajista' and señal['precio_entrada'] < rango['low'] - margen_minimo:
            señales_filtradas.append(señal)
    return pd.DataFrame(señales_filtradas)

def filtrar_rupturas_tendencia(df, señales, periodos_ma=50):
    """Filtra rupturas según la tendencia previa (media móvil)."""
    if len(señales) == 0:
        return señales
    df['ma'] = df['Close'].rolling(periodos_ma).mean()
    señales_filtradas = []
    for
