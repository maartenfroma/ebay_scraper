import pandas as pd
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QDialog,QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtGui import QFont

class AnalyzeDialog(QDialog):
    def __init__(self, product_name: str, text: str, top_brands: str, describe_df: pd.DataFrame, parent=None, title:str="Analyze Descriptives"):
        super().__init__(parent)

        self.product_name=product_name

        self.setWindowTitle("Analyze Descriptives " + self.product_name.upper())
        self.resize(650,650)

        layout=QVBoxLayout(self)

        lable_info=QLabel("Info")
        lable_desc=QLabel("DESCRIPTIVE STATISTICS")
        lable_top=QLabel("Top brands")

        info_edit=QTextEdit()
        info_edit.setReadOnly(True)
        info_edit.setPlainText("")
        info_edit.setPlainText(text)
        info_edit.setFont(QFont("Consolas"))
        info_edit.setMaximumHeight(200)


        top_edit=QTextEdit()
        top_edit.setReadOnly(True)
        top_edit.setPlainText("")
        top_edit.setPlainText(top_brands)
        top_edit.setFont(QFont("Consolas"))
        top_edit.setMaximumHeight(200)

        table_widget=QTableWidget()
        self.fill_table(table_widget, describe_df)

        layout.addWidget(lable_info)
        layout.addWidget(info_edit)
        layout.addWidget(lable_desc)
        layout.addWidget(table_widget)
        layout.addWidget(lable_top)
        layout.addWidget(top_edit)


    def fill_table(self, table: QTableWidget, df: pd.DataFrame):

        #Set row and column count COMPULSORY
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])

        #Set header labels
        table.setHorizontalHeaderLabels(df.columns.astype(str))
        table.setVerticalHeaderLabels(df.index.astype(str))

        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                val=df.iat[r,c]
                item=QTableWidgetItem("" if pd.isna(val) else str(val))
                table.setItem(r,c,item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
