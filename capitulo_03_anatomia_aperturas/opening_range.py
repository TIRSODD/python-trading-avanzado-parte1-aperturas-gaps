"""
Capítulo 3: Anatomía de las Aperturas de Mercado
Script: Cálculo del Opening Range y análisis de temporalidades
"""
import pandas as pd
import numpy as np
import yfinance as yf

def calcular_opening_range(df, minutos=15):
    """
    Calcula el Opening Range de los primeros N minutos.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
        
    opening_ranges = []
    for fecha, grupo in df.groupby(df.index.date):
        primer_minuto = grupo.index.min()
        ventana = grupo[grupo.index <= primer_minuto + pd.Timedelta(minutes=minutos)]
        
        if len(ventana) > 0:
            opening_range = {
                'fecha': fecha,
                'high': ventana['High'].max(),
                'low': ventana['Low'].min(),
                'rango': ventana['High'].max() - ventana['Low'].min()
            }
            opening_ranges.append(opening_range)
            
    df_ranges = pd.DataFrame(opening_ranges)
    if len(df_ranges) > 0:
        df_ranges.set_index('fecha', inplace=True)
        print(f"Opening Range calculado para {len(df_ranges)} sesiones")
        print(f"Rango promedio: {df_ranges['rango'].mean():.5f}")
    return df_ranges

def analizar_eficacia_temporalidades(df, minutos_ranges=[5, 15, 30, 60]):
    """
    Analiza qué temporalidad de Opening Range tiene mejor ratio de rupturas exitosas.
    """
    print("\n=== Análisis de Eficacia por Temporalidad ===\n")
    print(f"{'Minutos':<10} {'Tamaño Promedio':<15}")
    print("-" * 30)
    
    for minutos in minutos_ranges:
        ranges = calcular_opening_range(df, minutos)
        if len(ranges) > 0:
            print(f"{minutos:<10} {ranges['rango'].mean():<15.5f}")

# Uso
if __name__ == "__main__":
    print("Descargando datos de EUR/GBP...")
    ticker = yf.Ticker("EURGBP=X")
    df = ticker.history(period="60d", interval="5m")
    
    # Calcular rango de 15 minutos
    ranges_15 = calcular_opening_range(df, minutos=15)
    
    # Analizar diferentes temporalidades
    analizar_eficacia_temporalidades(df)
