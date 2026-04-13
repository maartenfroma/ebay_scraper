import pandas as pd
from PySide6.QtCore import QThread

from ScraperEbay_v1 import Scraper_EBAY
from scraper_v1 import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QFileDialog
import re
import os
from analyse import Analyse
from scraper_worker_progress import ScrapeWorker
from analayze_dialog import AnalyzeDialog
from boxplot_price import BoxplotPrice

#-----------------------------------------------------------------------------------------------------------------------
#Create MainWindow from QMainWindow object and load the gui from QTDesigner
#-----------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()

        #Load gui file that is converted to py
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)


        #Connect load button to on_load()
        self.ui.btn_load.clicked.connect(self.on_load)

        #Set the scraper, thread and worker to none to None
        self.scraper=None
        self.thread=None
        self.worker=None

        #Product name
        self.prod=""

        #Progress bar properties
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)
        self.ui.lbl_status.setText("")



    #-------------------------------------------------------------------------------------------------------------------
    #Create the slot for the load button
    #-------------------------------------------------------------------------------------------------------------------

    def on_load(self):

        #Get the output file text from the line edit
        output=self.ui.line_output.text().strip()
        output = os.path.basename(output)

        #Get the market place id from the list
        item = self.ui.list_market.currentItem()
        market = item.text() if item else "EBAY_US"

        #Get the query text input from the line edit
        query = self.ui.line_query.text().strip()
        if not query:
            QMessageBox.warning(self, "Error loading", "No query")
            return

        #Attach to instance variable
        self.prod=query

        #[self.ui.list_query.item(i).text() for i in range(self.ui.list_query.count())]

        #Read the number of pages from the line edit
        if self.ui.line_pages.text().isdigit():
            pages=int(self.ui.line_pages.text())

        else:
            QMessageBox.warning(self, "Error loading", "Pages must be integers")
            return

        #------------------------------------------------------------------------------------------------------------------
        #Laod the parameters in the scraper ebay class constructor
        self.scraper=Scraper_EBAY(market, query, pages, output)
        #------------------------------------------------------------------------------------------------------------------

        #Start the thread for progress
        self.thread = QThread()
        self.worker = ScrapeWorker(self.scraper)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.ui.progressBar.setValue)
        self.worker.status.connect(self.ui.lbl_status.setText)
        self.worker.finished.connect(self.on_scrape_finished)
        self.worker.error.connect(self.on_scrape_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)


        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)


        self.thread.start()

    #---------------------------------------------------------------------------------------------------------------------
    #Create function for analysing brand data
    #---------------------------------------------------------------------------------------------------------------------

    def on_analyze(self, file):


        # Run analysis
        try:
            #Create Analyse class object with product name and csv file
            analyser=Analyse(self.prod, file)
            #Returns the dataframe info()
            report=analyser.basic_info()
            #Returns a df with statistics
            descriptives=analyser.describe_df()
            #Returns a string with top 5 brand site shares
            top_brands=analyser.brand_summary(top_n=5)

            #Create instance of QDialog named AnalyzeDialog
            dlg=AnalyzeDialog(product_name=self.prod, text=report, top_brands=top_brands,
                              describe_df=descriptives, parent=self, title=f"Analyse – {file}")

            #Create box plot for price range
            box_plt=BoxplotPrice(df=analyser.df, parent=self)

            #Show the gui
            dlg.exec()
            box_plt.exec()

            QMessageBox.information(self, "Analyse", "Analysis completed successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Analyse Error", str(e))



    #Function for filling the table widget
    def fill_table(self, rows):

        # Fill the QTableWidget with data
        columns = ["title", "brand", "price", "currency", "itemWebUrl", "sellerUsername", "itemId"]
        table_results=self.ui.tableResults
        table_results.clearContents()

        table_results.setColumnCount(len(columns))
        table_results.setRowCount(len(rows))

        table_results.setHorizontalHeaderLabels(columns)
        table_results.horizontalHeader().setVisible(True)

        for r, row in enumerate(rows):
            raw_title=row.get('title') or ""
            clean_title=self.get_title(raw_title)
            row["title"] = clean_title

            #Brands that are excluded from the list
            brand_excl_list=["NEW"]

            brand=row.get('brand')
            # True if None, empty string, or NaN
            if brand is None or str(brand).strip() == "":
                brand = clean_title.split()[0] if clean_title.split()[0].upper() not in brand_excl_list else ""
                row["brand"]=brand

            for c, col in enumerate(columns):
                #Value for table cell
                val=row.get(col, "")
                #Create QTablewidgetItem
                item=QTableWidgetItem("" if val is None else str(val))
                #fill cells
                table_results.setItem(r,c,item)

        #Resize QTableWidget
        header = table_results.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # title kolom vult de ruimte
        header.setStretchLastSection(True)



    #Get string from raw string column title
    def get_title(self, title: str)-> str:
        if not title:
            return ""
        # remove everything except text, numbers and spaces
        title=re.sub(r"[^A-Za-z0-9 ]+", " ", title)
        return re.sub(r"\s+", " ", title).strip()

    # =====================================================================
    # SCRAPE FINISHED
    # =====================================================================
    def on_scrape_finished(self, rows):
        self.ui.lbl_status.setText("Scrape completed")

        #Load the rows into the tabelResults QTableWidget
        self.fill_table(rows)

        #Save to csv and to variable f
        f=self.scraper.save_csv(rows)

        #Load the Analyzer
        self.on_analyze(f)

    #-----------------------------------------------------------------------------------------------------------------
    #Normalize rows
    #--------------------------------------------------------------------------------------------------------------------
    def normalize_rows(self,rows):
        for row in rows:
            raw_title=row.get('title') or ""
            clean_title=self.get_title(raw_title)
            row['title']=clean_title

            brand=row.get('brand')

            if not brand:
                row["brand"]=clean_title.split()[0] if clean_title else ""

        return rows


    # =====================================================================
    # SCRAPE ERROR
    # =====================================================================
    def on_scrape_error(self, msg):
        QMessageBox.critical(self, "Scrape Error", msg)


if __name__=="__main__":
    app=QApplication([])
    win=MainWindow()
    win.show()
    #win.showMaximized()
    app.exec()