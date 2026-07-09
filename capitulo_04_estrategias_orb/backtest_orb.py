"""
Capítulo 4: Estrategias ORB
Script: Backtesting completo de la estrategia ORB
"""
import pandas as pd
import numpy as np
import yfinance as yf
from filtros_rupturas import pipeline_completo_orb
from orb_strategy import calcular_stops, calcular_take_profits, calcular_tamaño_posicion

class BacktestORB:
    """Backtesting completo de estrategia ORB con filtros."""
    def __init__(self, df, capital_inicial=10000, riesgo_porcentaje=1.0):
        self.df = df.copy()
        self.capital_inicial = capital_inicial
        self.riesgo_porcentaje = riesgo_porcentaje
        self.operaciones = []
        self.equity_curve = []

    def ejecutar(self, temporalidad=15, multiplicador_volumen=1.5, porcentaje_distancia=0.1, periodos_ma=50, multiplicador_stop=1.0, ratio_rb=2.0):
        print("=== Iniciando Backtest ORB ===\n")
        señales, ranges = pipeline_completo_orb(self.df, temporalidad, multiplicador_volumen, porcentaje_distancia, periodos_ma)
        if señales is None or len(señales) == 0:
            print("No hay señales para backtesting")
            return None
            
        señales = calcular_stops(señales, ranges, temporalidad, multiplicador_stop)
        señales = calcular_take_profits(señales, ratio_rb)
        señales = calcular_tamaño_posicion(señales, self.capital_inicial, self.riesgo_porcentaje)
        
        capital = self.capital_inicial
        for _, señal in señales.iterrows():
            resultado = self._simular_operacion(señal)
            if resultado is None:
                continue
            if resultado['tipo_salida'] == 'take_profit':
                pnl_pips = abs(señal['take_profit'] - señal['precio_entrada']) * 10000
            else:
                pnl_pips = -abs(señal['stop_loss'] - señal['precio_entrada']) * 10000
                
            pnl_usd = pnl_pips * señal['tamaño_lotes'] * 10 / 10000
            capital += pnl_usd
            
            self.operaciones.append({
                'fecha': señal['fecha'], 'tipo': señal['tipo'], 'pnl_usd': pnl_usd, 'capital': capital
            })
            self.equity_curve.append({'equity': capital})
            
        self._calcular_estadisticas()
        return pd.DataFrame(self.operaciones)

    def _simular_operacion(self, señal):
        inicio = señal['timestamp']
        fin = inicio + pd.Timedelta(hours=4)
        datos = self.df[(self.df.index >= inicio) & (self.df.index <= fin)]
        if len(datos) == 0:
            return None
        for timestamp, vela in datos.iterrows():
            if timestamp == inicio:
                continue
            if señal['tipo'] == 'alcista':
                if vela['Low'] <= señal['stop_loss']:
                    return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp}
                if vela['High'] >= señal['take_profit']:
                    return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp}
            else:
                if vela['High'] >= señal['stop_loss']:
                    return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp}
                if vela['Low'] <= señal['take_profit']:
                    return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp}
        return {'tipo_salida': 'timeout', 'timestamp_salida': datos.index[-1]}

    def _calcular_estadisticas(self):
        if len(self.operaciones) == 0:
            print("No hay operaciones para analizar")
            return
        df_ops = pd.DataFrame(self.operaciones)
        total_ops = len(df_ops)
        ops_ganadoras = len(df_ops[df_ops['pnl_usd'] > 0])
        tasa_acierto = ops_ganadoras / total_ops * 100
        pnl_total = df_ops['pnl_usd'].sum()
        retorno_total = (df_ops['capital'].iloc[-1] - self.capital_inicial) / self.capital_inicial * 100
        
        print("\n=== ESTADÍSTICAS DEL BACKTEST ===\n")
        print(f"Total operaciones: {total_ops}")
        print(f"Operaciones ganadoras: {ops_ganadoras} ({tasa_acierto:.1f}%)")
        print(f"PnL total: ${pnl_total:.2f}")
        print(f"Retorno total: {retorno_total:.2f}%")

# Uso
if __name__ == "__main__":
    print("Descargando datos de EUR/GBP...")
    ticker = yf.Ticker("EURGBP=X")
    df = ticker.history(period="60d", interval="5m")
    
    backtest = BacktestORB(df, capital_inicial=10000, riesgo_porcentaje=1.0)
    resultados = backtest.ejecutar(temporalidad=15)
