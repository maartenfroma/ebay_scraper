import pandas as pd
from PySide6.QtWidgets import QDialog, QVBoxLayout
import seaborn as sns
from mpl_canvas import Mpl_Canvas

class BoxplotPrice(QDialog):
    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Price range brand top 5")
        self.resize(900,500)

        layout=QVBoxLayout(self)
        self.canvas=Mpl_Canvas(width=8, height=4)
        layout.addWidget(self.canvas)

        self.plot(df)

    def plot(self, df):

        #Top 5 brands frequency
        brand_top5=df['brand'].value_counts().head(5).index

        #Dataframe of only top 5 brands
        df_top5=df[df['brand'].isin(brand_top5)].copy()

        order=list(brand_top5)

        ax=self.canvas.ax
        ax.clear()

        sns.boxplot(data=df_top5,
                    x="brand",
                    y="price",
                    order=order,
                        ax=ax)

        ax.set_title("Price distribution per brand")
        ax.set_xlabel("Brand")
        ax.set_ylabel("Price")
        ax.tick_params(axis='x', rotation=30)

        self.canvas.draw()
