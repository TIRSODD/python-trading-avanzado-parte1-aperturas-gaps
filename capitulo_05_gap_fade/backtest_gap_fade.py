"""
Capítulo 5: Estrategias Gap Fade
Script: Backtesting completo de la estrategia Gap Fade
"""
import pandas as pd
import numpy as np
import yfinance as yf
from analisis_gaps import calcular_gaps_apertura, analizar_estadisticas_gaps, filtrar_gaps_para_fade
from gap_fade_strategy import generar_señales_gap_fade, calcular_niveles_salida, calcular_tamaño_posicion_fade

class BacktestGapFade:
    """Backtesting completo de estrategia Gap Fade."""
    def __init__(self, df, capital_inicial=10000, riesgo_porcentaje=1.0):
        self.df = df.copy()
        self.capital_inicial = capital_inicial
        self.riesgo_porcentaje = riesgo_porcentaje
        self.operaciones = []
        self.equity_curve = []

    def ejecutar(self, umbral_minimo_pips=2.0, max_gap_pips=15,
                 max_ratio_volumen=2.5, multiplicador_stop=1.5,
                 max_horas=8, periodos_ma=100):
        print("=== INICIANDO BACKTEST GAP FADE ===\n")
        
        print("1. Calculando gaps de apertura...")
        df_gaps = calcular_gaps_apertura(self.df)
        df_gaps_sig = analizar_estadisticas_gaps(df_gaps, umbral_minimo_pips)
        
        print("\n2. Filtrando gaps candidatos para fade...")
        df_candidates = filtrar_gaps_para_fade(
            self.df, df_gaps, df_gaps_sig,
            max_gap_pips, max_ratio_volumen, periodos_ma
        )
        
        if len(df_candidates) == 0:
            print("No hay gaps candidatos para fade")
            return None
            
        print("\n3. Generando señales y calculando gestión de riesgo...")
        df_señales = generar_señales_gap_fade(self.df, df_candidates)
        df_señales = calcular_niveles_salida(df_señales, multiplicador_stop, max_horas)
        df_señales = calcular_tamaño_posicion_fade(df_señales, self.capital_inicial, self.riesgo_porcentaje)
        
        print("\n4. Simulando operaciones...")
        capital = self.capital_inicial
        for _, señal in df_señales.iterrows():
            resultado = self._simular_operacion(señal)
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
                'fecha': señal['fecha'], 'direccion': señal['direccion'],
                'pnl_usd': pnl_usd, 'capital': capital
            })
            self.equity_curve.append({'equity': capital})
            
        self._calcular_estadisticas()
        return pd.DataFrame(self.operaciones)

    def _simular_operacion(self, señal):
        inicio = señal['timestamp_entrada']
        fin = inicio + pd.Timedelta(hours=señal['tiempo_maximo_horas'])
        datos = self.df[(self.df.index >= inicio) & (self.df.index <= fin)]
        
        if len(datos) == 0:
            return None
            
        for timestamp, vela in datos.iterrows():
            if timestamp == inicio:
                continue
                
            if señal['direccion'] == 'long' and vela['High'] >= señal['nivel_objetivo']:
                return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp, 'precio_salida': señal['nivel_objetivo']}
            elif señal['direccion'] == 'short' and vela['Low'] <= señal['nivel_objetivo']:
                return {'tipo_salida': 'take_profit', 'timestamp_salida': timestamp, 'precio_salida': señal['nivel_objetivo']}
                
            if señal['direccion'] == 'long' and vela['Low'] <= señal['stop_loss']:
                return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp, 'precio_salida': señal['stop_loss']}
            elif señal['direccion'] == 'short' and vela['High'] >= señal['stop_loss']:
                return {'tipo_salida': 'stop_loss', 'timestamp_salida': timestamp, 'precio_salida': señal['stop_loss']}
                
        ultimo_precio = datos['Close'].iloc[-1]
        return {'tipo_salida': 'time_stop', 'timestamp_salida': datos.index[-1], 'precio_salida': ultimo_precio}

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
    
    backtest = BacktestGapFade(df, capital_inicial=10000, riesgo_porcentaje=1.0)
    resultados = backtest.ejecutar()
