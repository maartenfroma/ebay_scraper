Pandas, Pyside6.

Get your id and secret at:
https://developer.ebay.com/api-docs/static/oauth-credentials.html

Set the "EBAY_CLIENT_ID" in environment variables
Set the "EBAY_CLIENT_SECRET" in environment variables

Run main and the MainWindow appears where you can set market place, query(product), pages n and output file name.

It loads the pages from the api json file and saves the results in an csv file. Data is also shown in the QTableWidget.

After that a short analysis is run to get the dataframe statistics and boxplot of price range.
