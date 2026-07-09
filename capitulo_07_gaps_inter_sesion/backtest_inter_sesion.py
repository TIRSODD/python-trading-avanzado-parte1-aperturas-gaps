"""
Capítulo 7: Gaps Inter-Sesión y Estrategias
Script: Backtesting completo de estrategias inter-sesión
"""
import pandas as pd
import numpy as np
import yfinance as yf
from gaps_inter_sesion import calcular_gaps_overnight, analizar_gaps_overnight
from estrategias_inter_sesion import estrategia_gap_fade_overnight

class BacktestInterSesion:
    """Backtesting de estrategias basadas en gaps y transiciones entre sesiones."""
    def __init__(self, df, capital_inicial=10000, riesgo_porcentaje=1.0):
        self.df = df.copy()
        self.capital_inicial = capital_inicial
        self.riesgo_porcentaje = riesgo_porcentaje
        self.operaciones = []
        self.equity_curve = []

    def ejecutar_gap_fade_overnight(self, max_gap_pips=8, min_gap_pips=2.0):
        """Ejecuta backtest de estrategia Gap Fade Overnight."""
        print("=== BACKTEST: GAP FADE OVERNIGHT ===\n")
        
        print("1. Calculando gaps overnight...")
        df_gaps = calcular_gaps_overnight(self.df)
        df_gaps_sig = analizar_gaps_overnight(df_gaps, min_gap_pips)
        
        print("\n2. Generando señales...")
        df_señales = estrategia_gap_fade_overnight(
            self.df, df_gaps_sig, 
            self.capital_inicial, self.riesgo_porcentaje
        )
        
        if len(df_señales) == 0:
            print("No hay señales para backtesting")
            return None
            
        print("\n3. Simulando operaciones...")
        capital = self.capital_inicial
        for _, señal in df_señales.iterrows():
            resultado = self._simular_operacion_gap_fade(señal)
            if resultado is None:
                continue
                
            if resultado['tipo_salida'] == 'take_profit':
                if señal['direccion'] == 'long':
                    pnl_pips = (señal['nivel_objetivo'] - señal['precio_entrada']) * 10000
                else:
                    pnl_pips = (señal['precio_entrada'] - señal['nivel_objetivo']) * 10000
            else:
                if señal['direccion'] == 'long':
                    pnl_pips = (resultado['precio_salida'] - señal['precio_entrada']) * 10000
                else:
                    pnl_pips = (señal['precio_entrada'] - resultado['precio_salida']) * 10000
                    
            pnl_usd = pnl_pips * señal['tamaño_lotes'] * 10 / 10000
            capital += pnl_usd
            
            self.operaciones.append({
                'fecha': señal['fecha'],
                'direccion': señal['direccion'],
                'pnl_usd': pnl_usd,
                'capital': capital
            })
            self.equity_curve.append({'equity': capital})
            
        self._calcular_estadisticas()
        return pd.DataFrame(self.operaciones)

    def _simular_operacion_gap_fade(self, señal, max_horas=4):
        """Simula una operación de gap fade."""
        inicio = señal['timestamp_entrada']
        fin = inicio + pd.Timedelta(hours=max_horas)
        datos = self.df[(self.df.index >= inicio) & (self.df.index <= fin)]
        
        if len(datos) == 0:
            return None
            
        for timestamp, vela in datos.iterrows():
            if timestamp == inicio:
                continue
                
            if señal['direccion'] == 'long' and vela['high'] >= señal['nivel_objetivo']:
                return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp, 'precio_salida': señal['nivel_objetivo']}
            elif señal['direccion'] == 'short' and vela['low'] <= señal['nivel_objetivo']:
                return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp, 'precio_salida': señal['nivel_objetivo']}
                
            if señal['direccion'] == 'long' and vela['low'] <= señal['stop_loss']:
                return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp, 'precio_salida': señal['stop_loss']}
            elif señal['direccion'] == 'short' and vela['high'] >= señal['stop_loss']:
                return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp, 'precio_salida': señal['stop_loss']}
                
        ultimo_precio = datos['close'].iloc[-1]
        return {'tipo_salida': 'time_stop', 'timestamp_salida': datos.index[-1], 'precio_salida': ultimo_precio}

    def _calcular_estadisticas(self):
        """Calcula estadísticas del backtesting."""
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
    
    backtest = BacktestInterSesion(df, capital_inicial=10000, riesgo_porcentaje=1.0)
    resultados = backtest.ejecutar_gap_fade_overnight()
