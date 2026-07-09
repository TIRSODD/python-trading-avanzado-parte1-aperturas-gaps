"""
Capítulo 4: Estrategias ORB
Script: Gestión de riesgo, stops y dimensionamiento de posición
"""
import pandas as pd
import numpy as np

def calcular_stops(señales, ranges, temporalidad=15, multiplicador_stop=1.0):
    """Calcula stop-loss basado en el tamaño del rango."""
    if len(señales) == 0:
        return señales
    señales_con_stops = []
    for _, señal in señales.iterrows():
        rango = ranges[(ranges.index == señal['fecha']) & (ranges['temporalidad'] == temporalidad)]
        if len(rango) == 0:
            continue
        rango = rango.iloc[0]
        tamaño_rango = rango['rango']
        if señal['tipo'] == 'alcista':
            stop_loss = rango['high'] - (tamaño_rango * multiplicador_stop)
            stop_loss = min(stop_loss, rango['low'])
        else:
            stop_loss = rango['low'] + (tamaño_rango * multiplicador_stop)
            stop_loss = max(stop_loss, rango['high'])
        señal_con_stop = señal.copy()
        señal_con_stop['stop_loss'] = stop_loss
        señal_con_stop['tamaño_rango'] = tamaño_rango
        señales_con_stops.append(señal_con_stop)
    return pd.DataFrame(señales_con_stops)

def calcular_take_profits(señales_con_stops, ratio_rb=2.0):
    """Calcula take-profit basado en ratio riesgo/beneficio."""
    if len(señales_con_stops) == 0:
        return señales_con_stops
    señales_completas = []
    for _, señal in señales_con_stops.iterrows():
        riesgo = abs(señal['precio_entrada'] - señal['stop_loss'])
        beneficio = riesgo * ratio_rb
        if señal['tipo'] == 'alcista':
            take_profit = señal['precio_entrada'] + beneficio
        else:
            take_profit = señal['precio_entrada'] - beneficio
        señal_completa = señal.copy()
        señal_completa['take_profit'] = take_profit
        señal_completa['ratio_rb'] = ratio_rb
        señal_completa['riesgo_pips'] = riesgo * 10000
        señales_completas.append(señal_completa)
    return pd.DataFrame(señales_completas)

def calcular_tamaño_posicion(señales_completas, capital, riesgo_porcentaje=1.0):
    """Calcula el tamaño de posición para arriesgar un porcentaje fijo del capital."""
    if len(señales_completas) == 0:
        return señales_completas
    señales_con_posicion = []
    riesgo_monetario = capital * (riesgo_porcentaje / 100)
    for _, señal in señales_completas.iterrows():
        riesgo_pips = señal['riesgo_pips']
        if riesgo_pips == 0:
            continue
        tamaño_lotes = riesgo_monetario / (riesgo_pips * 10)
        señal_con_posicion = señal.copy()
        señal_con_posicion['tamaño_lotes'] = round(tamaño_lotes, 2)
        señal_con_posicion['riesgo_usd'] = riesgo_monetario
        señales_con_posicion.append(señal_con_posicion)
    return pd.DataFrame(señales_con_posicion)
