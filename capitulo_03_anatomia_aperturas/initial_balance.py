"""
Capítulo 3: Anatomía de las Aperturas de Mercado
Script: Análisis de la Initial Balance
"""
import pandas as pd
import numpy as np
import yfinance as yf

def analizar_initial_balance(df, minutos_ib=60):
    """
    Analiza si el precio rompe la initial balance y con qué frecuencia.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
        
    ib_data = []
    for fecha, grupo in df.groupby(df.index.date):
        primer_minuto = grupo.index.min()
        ib_ventana = grupo[grupo.index <= primer_minuto + pd.Timedelta(minutes=minutos_ib)]
        resto_sesion = grupo[grupo.index > primer_minuto + pd.Timedelta(minutes=minutos_ib)]
        
        if len(ib_ventana) > 0 and len(resto_sesion) > 0:
            ib_high = ib_ventana['High'].max()
            ib_low = ib_ventana['Low'].min()
            
            # ¿El resto de la sesión rompe la IB?
            max_resto = resto_sesion['High'].max()
            min_resto = resto_sesion['Low'].min()
            
            ruptura_alcista = max_resto > ib_high
            ruptura_bajista = min_resto < ib_low
            sin_ruptura = not ruptura_alcista and not ruptura_bajista
            
            ib_data.append({
                'fecha': fecha,
                'ib_high': ib_high,
                'ib_low': ib_low,
                'ruptura_alcista': ruptura_alcista,
                'ruptura_bajista': ruptura_bajista,
                'sin_ruptura': sin_ruptura
            })
            
    df_ib = pd.DataFrame(ib_data)
    
    if len(df_ib) > 0:
        total_dias = len(df_ib)
        dias_alcista = df_ib['ruptura_alcista'].sum()
        dias_bajista = df_ib['ruptura_bajista'].sum()
        dias_lateral = df_ib['sin_ruptura'].sum()
        
        print(f"=== Análisis Initial Balance ({minutos_ib} min) ===")
        print(f"Total días analizados: {total_dias}")
        print(f"Ruptura alcista: {dias_alcista} ({100*dias_alcista/total_dias:.1f}%)")
        print(f"Ruptura bajista: {dias_bajista} ({100*dias_bajista/total_dias:.1f}%)")
        print(f"Sin ruptura (lateral): {dias_lateral} ({100*dias_lateral/total_dias:.1f}%)")
        
    return df_ib

# Uso
if __name__ == "__main__":
    print("Descargando datos de EUR/GBP...")
    ticker = yf.Ticker("EURGBP=X")
    df = ticker.history(period="60d", interval="5m")
    
    ib_analysis = analizar_initial_balance(df, minutos_ib=60)
