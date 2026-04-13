import pandas as pd
from io import StringIO
from ScraperEbay_v1 import Scraper_EBAY

class Analyse:
    def __init__(self, product_name: str, output_file):

        self.product_name=product_name
        self.df = pd.read_csv(output_file)
        #Remove brands if all digits
        self.df=self.df[~self.df['brand'].astype(str).str.isdigit()]
        #Brands to upper
        self.df['brand']=self.df['brand'].astype(str).str.upper()
        #Remove outliers in price if std >3
        price_mean=self.df['price'].mean()
        price_std=self.df['price'].std()
        self.df=self.df[(self.df['price'] - price_mean).abs() <= (3 * price_std)]
        print(self.df.head(50))



    #-------------------------------------------------------------------------------------------------------------------
    #Preprocess data
    #------------------------------------------------------------------------------------------------------------------


    #Basic info dataframe
    def basic_info(self) -> str:
        s = StringIO()
        self.df.info(buf=s)
        return s.getvalue()

    def describe_df(self) -> pd.DataFrame:
        return self.df[['price']].describe().round(2)

    def brand_summary(self, top_n=10) -> str:
        if "brand" not in self.df.columns:
            return "No 'brand' column found."
        vc = (self.df["brand"].dropna().value_counts(normalize=True).head(top_n)*100).round(2)
        return "=== TOP BRANDS share in % ===\n" + vc.to_string()




