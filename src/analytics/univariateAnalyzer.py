import numpy as np
import pandas as pd
import sys
import math
import scipy.stats as stats
import seaborn as sns

class UnivariateAnalyzer:
    """
    Una clase para realizar un análisis estadístico exhaustivo de la distribución de una sola variable,
    centrándose en comprender su forma, las tendencias centrales y la dispersión.
    """

    def __init__(self, data: pd.Series):
        self.total_original = len(data)
        self.valores_nulos = data.isna().sum()
        self.data = data.dropna()
        self.porcentaje_nulos = (self.valores_nulos / self.total_original) * 100 if self.total_original > 0 else 0

    def get_central_tendency(self) -> dict:
        mode_list = self.data.mode()
        mode = mode_list[0] if not mode_list.empty else np.nan
        
        return {
            "mean": self.data.mean(),  
            "median": self.data.median(),
            "mode": mode,
        }

    def get_dispersion_metrics(self) -> dict:
        q1 = self.data.quantile(q=0.25, interpolation='linear')
        q3 = self.data.quantile(q=0.75, interpolation='linear')
        limit_range = self.data.max() - self.data.min()

        return {
            "std": self.data.std(),
            "var": self.data.var(),
            "range": limit_range,
            "IQR": q3 - q1,
        }

    def get_percentiles(self) -> dict:
        points = [0.25, 0.50, 0.75, 0.90, 0.99]
        values = {}

        for p in points: 

            values[f'{p*100}'] = self.data.quantile(q=p, interpolation='linear')

        return values

    def get_shape_metrics(self) -> dict:
        ca_f = stats.skew(self.data)
        k = stats.kurtosis(self.data)

        return {
            "asimetria": (self._clasificar_asimetria(ca_f), ca_f),
            "curtosis": (self._clasificar_curtosis(k), k)
        }

    def identify_outliers(self) -> dict:

        q1 = self.data.quantile(0.25, interpolation='linear')
        q3 = self.data.quantile(0.75, interpolation='linear')
        iqr = q3 - q1
        
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        outliers = self.data[(self.data < limite_inferior) | (self.data > limite_superior)]
        
        return {
            "limite_inferior": max(0,limite_inferior),
            "limite_superior": limite_superior,
            "cantidad_outliers": len(outliers),
            "porcentaje_outliers": (len(outliers) / len(self.data)) * 100
        }

    def test_normality(self):
        stat, p_value = stats.normaltest(self.data)
        es_normal = p_value > 0.05 
        
        return {
            "estadistico": stat,
            "p_value": p_value,
            "es_normal": es_normal
        }
    
    def generate_summary_report(self) -> dict:
        """
        Devuelve un resumen consolidado con todos los hallazgos estadísticos y estado de limpieza.
        """
        reporte_crudo = {
            "tendencia_central": self.get_central_tendency(),
            "dispersion": self.get_dispersion_metrics(),
            "percentiles": self.get_percentiles(),
            "forma": self.get_shape_metrics(),
            "outliers": self.identify_outliers(),
            "normalidad": self.test_normality()
        }

        return self._formatear_a_dataframe(reporte_crudo)


    @staticmethod
    def _formatear_a_dataframe(reporte_crudo: dict) -> pd.DataFrame:

        def format_val(v):
            if isinstance(v, tuple): return f"{v[0]} ({v[1]:.3f})"
            if isinstance(v, float): return round(v, 4)
            return v

        filas = [
            (categoria.replace("_", " ").upper(), metrica.replace("_", " ").capitalize(), format_val(valor))
            for categoria, metricas in reporte_crudo.items()
            for metrica, valor in metricas.items()
        ]
                
        return pd.DataFrame(filas, columns=["Categoría", "Métrica", "Valor"]).set_index(["Categoría", "Métrica"])
        
    @staticmethod
    def _clasificar_asimetria(valor):
        if math.isclose(valor, 0.0, abs_tol=sys.float_info.epsilon): return "Simetrica"
        return "Asimetria positiva" if valor > 0 else "Asimetria negativa"

    @staticmethod
    def _clasificar_curtosis(valor):
        if math.isclose(valor, 0.0, abs_tol=sys.float_info.epsilon): return "Mesocurtica"
        return "Leptocurtica" if valor > 0 else "Platicurtica"