import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class UnivariateVisualizer:
    """
    Clase dedicada exclusivamente a la visualización de distribuciones univariadas
    usando la API orientada a objetos de Matplotlib (fig, ax).
    """

    def __init__(self, data: pd.Series, title: str = "Distribución de la variable"):
        self.data = data.dropna()
        self.title = title
        sns.set_theme(style="whitegrid", palette="muted")

    def plot_histogram(self, figsize=(10, 6)):
        """Genera un histograma y devuelve la figura y el eje."""
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.histplot(self.data, kde=True, bins=30, color='royalblue', ax=ax)
        ax.axvline(self.data.mean(), color='red', linestyle='--', label='Media')
        ax.axvline(self.data.median(), color='green', linestyle='-', label='Mediana')
        ax.legend()
        
        ax.set_title(f"Histograma y KDE - {self.title}")
        ax.set_xlabel("Valor")
        ax.set_ylabel("Frecuencia")
        
        return fig, ax

    def plot_boxplot(self, figsize=(10, 4)):
        """Genera un diagrama de caja y devuelve la figura y el eje."""
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.boxplot(x=self.data, color='lightgreen', flierprops={"marker": "x", "color": "red"}, ax=ax)
        
        ax.set_title(f"Diagrama de Caja (Boxplot) - {self.title}")
        ax.set_xlabel("Valor")
        
        return fig, ax

    def plot_combined_distribution(self, figsize=(10, 8)):
        """Genera boxplot e histograma apilados devolviendo la figura y sus ejes."""
        fig, (ax_box, ax_hist) = plt.subplots(
            nrows=2, 
            sharex=True, 
            figsize=figsize, 
            gridspec_kw={"height_ratios": (.15, .85)}
        )
        
        sns.boxplot(x=self.data, ax=ax_box, color='lightgreen', flierprops={"marker": "x", "color": "red"})
        ax_box.set_xlabel('') 
        ax_box.set_title(f"Análisis Completo de Distribución - {self.title}")
        
        sns.histplot(self.data,kde=True, ax=ax_hist, color='royalblue', bins=30)
        ax_hist.set_xlabel("Valor")
        ax_hist.set_ylabel("Frecuencia")
        
        fig.tight_layout()
        
        return fig, (ax_box, ax_hist)