"""
Capítulo 3: Anatomía de las Aperturas de Mercado
Script: Análisis del patrón de volumen y volatilidad en la apertura
"""
import pandas as pd
import numpy as np
import yfinance as yf

def analizar_patron_apertura(df, minutos_analisis=30):
    """
    Analiza el patrón de volumen y volatilidad en los primeros minutos.
    df: DataFrame con datos de 5 minutos
    """
    # Filtrar solo los primeros minutos de la sesión (asumiendo apertura a las 07:00 UTC para Londres)
    df_apertura = df.between_time('07:00', f'07:{minutos_analisis}')
    
    if len(df_apertura) == 0:
        print("No hay datos en el horario de apertura especificado.")
        return None, None

    # Calcular volumen promedio por minuto
    volumen_por_minuto = df_apertura.groupby(df_apertura.index.minute)['Volume'].mean()
    
    # Calcular volatilidad (rango high-low) por minuto
    df_apertura = df_apertura.copy()
    df_apertura['rango'] = df_apertura['High'] - df_apertura['Low']
    volatilidad_por_minuto = df_apertura.groupby(df_apertura.index.minute)['rango'].mean()
    
    print("=== Patrón de Apertura ===")
    print("\nVolumen promedio por minuto:")
    print(volumen_por_minuto.head(10))
    
    # Calcular ratio de decaimiento
    if len(volumen_por_minuto) >= 10:
        volumen_inicial = volumen_por_minuto.iloc[:5].mean()
        volumen_final = volumen_por_minuto.iloc[-5:].mean()
        ratio_decaimiento = volumen_inicial / volumen_final if volumen_final > 0 else 0
        
        print(f"\nRatio de decaimiento de volumen: {ratio_decaimiento:.2f}x")
        if ratio_decaimiento > 2:
            print("→ Alto volumen inicial, ideal para estrategias de ruptura")
        else:
            print("→ Volumen más uniforme, mejor para estrategias de reversión")
    
    return volumen_por_minuto, volatilidad_por_minuto

# Uso
if __name__ == "__main__":
    print("Descargando datos de EUR/GBP...")
    ticker = yf.Ticker("EURGBP=X")
    df = ticker.history(period="60d", interval="5m")
    
    volumen, volatilidad = analizar_patron_apertura(df, minutos_analisis=30)
