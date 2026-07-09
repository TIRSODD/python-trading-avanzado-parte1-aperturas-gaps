"""
Capítulo 2: Infraestructura de Datos
Script: Pipeline de datos robusto y modular
"""
import pandas as pd
import numpy as np
import yfinance as yf
import os
from datetime import datetime

class PipelineDatos:
    def __init__(self, ruta_base='./data_trading'):
        self.ruta_base = ruta_base
        # Crear estructura de directorios
        for carpeta in ['01_crudo', '02_limpio', '03_procesado']:
            os.makedirs(os.path.join(ruta_base, carpeta), exist_ok=True)
        print(f"Pipeline inicializado en: {ruta_base}")
    
    def descargar(self, ticker, periodo="60d", intervalo="5m"):
        """Paso 1: Descargar datos crudos."""
        print(f"Descargando {ticker}...")
        df = yf.Ticker(ticker).history(period=periodo, interval=intervalo)
        # Guardar crudo
        ruta = os.path.join(self.ruta_base, '01_crudo', f'{ticker}_crudo.parquet')
        df.to_parquet(ruta)
        print(f"  ✓ Datos crudos guardados: {ruta}")
        return df
    
    def validar(self, df):
        """Paso 2: Validar integridad."""
        print("Validando datos...")
        # Verificar columnas obligatorias
        columnas_req = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in columnas_req:
            if col not in df.columns:
                raise ValueError(f"Falta columna obligatoria: {col}")
        
        # Verificar que High >= Low
        invalidos = df[df['High'] < df['Low']]
        if len(invalidos) > 0:
            print(f"  ⚠️  {len(invalidos)} filas con High < Low")
            df.loc[df['High'] < df['Low'], ['High', 'Low']] = df.loc[df['High'] < df['Low'], ['Low', 'High']].values
        
        # Verificar nulos
        nulos = df.isnull().sum()
        if nulos.any():
            print(f"  ️  Valores nulos detectados: {nulos[nulos > 0].to_dict()}")
        
        print("  ✓ Validación completada")
        return df
    
    def limpiar(self, df):
        """Paso 3: Limpiar datos (outliers y huecos)."""
        print("Limpiando datos...")
        # Rellenar precios con forward fill
        df['Close'] = df['Close'].ffill()
        df['Open'] = df['Open'].ffill()
        df['High'] = df['High'].ffill()
        df['Low'] = df['Low'].ffill()
        
        # Volumen: dejar como 0
        df['Volume'] = df['Volume'].fillna(0)
        
        # Filtrar filas sin volumen
        df = df[df['Volume'] > 0]
        print(f"  ✓ Datos limpiados. Filas finales: {len(df)}")
        return df
    
    def transformar(self, df):
        """Paso 4: Calcular retornos y optimizar memoria."""
        print("Transformando datos...")
        # Calcular log-retornos
        df['log_retorno'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Optimizar memoria
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype('float32')
        
        print("  ✓ Transformación completada")
        return df
    
    def almacenar(self, df, ticker):
        """Paso 5: Guardar en formato Parquet."""
        ruta_limpio = os.path.join(self.ruta_base, '02_limpio', f'{ticker}_limpio.parquet')
        ruta_proc = os.path.join(self.ruta_base, '03_procesado', f'{ticker}_procesado.parquet')
        
        df.to_parquet(ruta_limpio)
        print(f"  ✓ Datos limpios guardados: {ruta_limpio}")
        
        # Guardar también la versión procesada
        df.to_parquet(ruta_proc)
        print(f"  ✓ Datos procesados guardados: {ruta_proc}")
    
    def procesar_completo(self, ticker, periodo="60d", intervalo="5m"):
        """Ejecuta el pipeline completo para un activo."""
        print(f"\n{'='*50}")
        print(f"PROCESANDO: {ticker}")
        print(f"{'='*50}")
        
        df = self.descargar(ticker, periodo, intervalo)
        df = self.validar(df)
        df = self.limpiar(df)
        df = self.transformar(df)
        self.almacenar(df, ticker)
        
        print(f"✓ Pipeline completado para {ticker}\n")
        return df

# Uso
if __name__ == "__main__":
    pipeline = PipelineDatos('./data_trading')
    df_eurgbp = pipeline.procesar_completo('EURGBP=X', periodo="7d", intervalo="5m")
