import numpy as np
import pandas as pd
import sys
import math
import scipy.stats as stats

class UnivariateAnalyzer:
    """
    Una clase para realizar un análisis estadístico exhaustivo de la distribución de una sola variable,
    centrándose en comprender su forma, las tendencias centrales y la dispersión.

    """

    def __init__(self, data: pd.Series):
        """
        Inicializa el analizador con una única serie de datos (una columna o array).
        """
        self.data = data

    def get_central_tendency(self) -> dict:
        """
        Calcula media, mediana y moda.
        """

        mode_list = self.data.mode()
        mode = mode_list[0] if not mode_list.empty else np.nan
        
        return {
            "mean:": [self.data.mean()],
            "median": [self.data.median()],
            "mode": [mode],
        }

    def get_dispersion_metrics(self) -> dict:
        """
        Calcula varianza, desviación estándar, rango y rango intercuartílico (IQR).
        """

        q1 = self.data.quantile(q=0.25, axis=0, numeric_only=False, interpolation='linear')
        q2 = self.data.quantile(q=0.75, axis=0, numeric_only=False, interpolation='linear')
        limit_range = self.data.max() - self.data.min()


        return {
            "std":[self.data.std()],
            "var": [self.data.var()],
            "range": [limit_range],
            "IQR": [q2-q1],
        }

        

    def get_percentiles(self) -> dict:
        """
        Calcula los percentiles clave (ej. 25%, 50%, 75%, 90%, 99%).
        """

        points = [0.25, 0.50, 0.75, 0.90, 0.99]

        values = {}

        for p in points: 
            values[f'{p}'] = self.data.quantile(q=p, axis=0, numeric_only=False, interpolation='linear')

        return values

    def get_shape_metrics(self):
        """
        Calcula la asimetría (skewness) y curtosis de la distribución general.
        """
        ca_f = stats.skew(self.datos)
        k = stats.kurtosis(self.datos)

        return {
            "asimetria": (self._clasificar_asimetria(ca_f), ca_f),
            "curtosis": (self._clasificar_curtosis(k), k)
        }

    def identify_outliers(self):
        """
        Identifica valores atípicos utilizando métodos como el IQR o Z-score.
        """
        pass

    def test_normality(self):
        """
        Aplica pruebas estadísticas (ej. Shapiro-Wilk) para ver si la distribución es normal.
        """
        pass

    def generate_summary_report(self):
        """
        Devuelve un diccionario o resumen consolidado con todos los hallazgos 
        estadísticos de la distribución.
        """
        pass


    @staticmethod
    def _clasificar_asimetria(valor):
        if math.isclose(valor, 0.0, abs_tol=sys.float_info.epsilon): return "Simetrica"
        return "Asimetria positiva" if valor > 0 else "Asimetria negativa"

    @staticmethod
    def _clasificar_curtosis(valor):
        if math.isclose(valor, 0.0, abs_tol=sys.float_info.epsilon): return "Mesocurtica"
        return "Leptocurtica" if valor > 0 else "Platicurtica"