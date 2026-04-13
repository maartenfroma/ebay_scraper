from PySide6.QtCore import QObject, Signal, Slot
import time

#----------------------------------------------------------------------------------------------------------------------
#Create Scraper thread by passing the scraper object
#-----------------------------------------------------------------------------------------------------------------------

class ScrapeWorker(QObject):

    #Create Signal object for different states
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper

    @Slot()
    def run(self):
        try:
            token, _ = self.scraper.get_app_token()
            all_rows = []
            offset = 0
            page_size = 50

            #Loop through the pages
            for p in range(self.scraper.pages):
                self.status.emit(f"Loading page {p+1}/{self.scraper.pages}...")
                self.progress.emit(int((p / self.scraper.pages) * 100))

                #Get the rows from the json file
                data = self.scraper.search_items(token, limit=page_size, offset=offset)
                rows = self.scraper.extract_rows(data)

                if not rows:
                    self.status.emit(f"No results on page {p+1}")
                    break

                #Add the rows to the all_rows list
                all_rows.extend(rows)
                #Add new pages
                offset += page_size
                #Pause
                time.sleep(1)

            # Save CSV
            #self.scraper.save_csv(all_rows)

            self.progress.emit(100)
            self.status.emit("Scraping completed")
            self.finished.emit(all_rows)

        except Exception as e:
            self.error.emit(str(e))
