Pandas, Pyside6.

Get your id and secret at:
https://developer.ebay.com/api-docs/static/oauth-credentials.html.

Set the "EBAY_CLIENT_ID" in environment variables.
Set the "EBAY_CLIENT_SECRET" in environment variables.

With QTDesigner I made the interface scraper_v1.ui.

If changes are made in the ui file, you have to make a new py file with:
pyside6-uic scraper_v1.ui -o scraper_v1.py in command prompt.

Run main and the MainWindow appears where you can set market place, query(product), pages n and output file name.

The problem was getting the brand column as most of the time it is not given and I had to extract it from the title column. I omitted brands that occur less than 10%. Also an exclusion list is used. An idea would be to concentrate on certain products and make a brand list that is allowed.

It loads the pages from the api json file and saves the results in a csv file. Data is also shown in the QTableWidget.

After the product data is retrieved, a short analysis is run to get the dataframe statistics and boxplot of price range.
