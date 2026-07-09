"""
Capítulo 2: Infraestructura de Datos
Script: Descargador masivo con manejo de errores y reintentos
"""
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

class DescargadorMasivo:
    def __init__(self, max_reintentos=3, pausa_segundos=2):
        self.max_reintentos = max_reintentos
        self.pausa_segundos = pausa_segundos
    
    def descargar_activo(self, ticker, periodo="60d", intervalo="5m"):
        """Descarga datos de un activo con reintentos automáticos."""
        for intento in range(self.max_reintentos):
            try:
                print(f"Descargando {ticker} (intento {intento + 1})...")
                data = yf.Ticker(ticker).history(
                    period=periodo, 
                    interval=intervalo
                )
                if len(data) > 0:
                    print(f"  ✓ {len(data)} filas descargadas")
                    return data
                else:
                    print(f"  ⚠️  Sin datos para {ticker}")
                    return None
            except Exception as e:
                print(f"  ✗ Error: {e}")
                if intento < self.max_reintentos - 1:
                    print(f"  Reintentando en {self.pausa_segundos}s...")
                    time.sleep(self.pausa_segundos)
        return None
    
    def descargar_cartera(self, tickers, periodo="60d", intervalo="5m"):
        """Descarga múltiples activos respetando los rate limits."""
        resultados = {}
        for ticker in tickers:
            data = self.descargar_activo(ticker, periodo, intervalo)
            if data is not None:
                resultados[ticker] = data
            time.sleep(self.pausa_segundos)  # Pausa entre activos
        return resultados

# Uso
if __name__ == "__main__":
    descargador = DescargadorMasivo()
    cartera = ['EURGBP=X', 'EURUSD=X', 'XAUUSD=X']
    datos = descargador.descargar_cartera(cartera)
    print(f"\nTotal activos descargados: {len(datos)}")
