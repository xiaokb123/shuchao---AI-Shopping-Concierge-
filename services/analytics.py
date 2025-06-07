import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
from ..models.database_models import ShoppingHistoryDB, UserBehavior

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_data(self):
        sales_data = self.db.query(ShoppingHistoryDB).all()
        df = pd.DataFrame([s.__dict__ for s in sales_data])
        return df

    def plot_sales_trends(self):
        df = self.get_sales_data()
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        sales_trends = df.groupby(df['purchase_date'].dt.to_period('M')).sum()
        sales_trends.plot(y='price', kind='line')
        plt.title('Sales Trends')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        plt.show() 