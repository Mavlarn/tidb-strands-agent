import os

from typing import Optional, Any
from pytidb import TiDBClient
from pytidb.schema import TableModel, Field, FullTextField
from pytidb.embeddings import EmbeddingFunction
from pytidb.datatype import Text

import litellm
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME"),
    password=os.getenv("TIDB_PASSWORD"),
    database=os.getenv("TIDB_DATABASE"),
    enable_ssl=True,
)

litellm._turn_on_debug()
os.environ["AWS_REGION_NAME"] = "us-east-1"

text_embed = EmbeddingFunction(
    "bedrock/amazon.titan-embed-text-v2:0",
    dimensions = 1024,
    timeout = 60
)

# Define the table
table_name = "product_reviews"
class ProductReview(TableModel, table=True):
    __tablename__ = table_name
    __table_args__ = {"extend_existing": True}

    review_id: str = Field(primary_key=True)
    order_id: str = Field()
    product_id: str = Field()
    customer_id: str = Field()
    rating: int = Field()
    product_name: str = Field()
    # product_name: str = FullTextField()
    review_content: str = Field(sa_type=Text)
    review_content_vec: list[float] = text_embed.VectorField(
        source_field="review_content"
    )
    review_date: str = Field()
    is_verified_purchase: bool = Field()
    

cs_table_name = "customer_service_records"
class CSRecords(TableModel, table=True):
    __tablename__ = cs_table_name
    __table_args__ = {"extend_existing": True}

    record_id: str = Field(primary_key=True)
    order_id: str = Field()
    customer_id: str = Field()
    service_type: str = Field()
    issue_category: str = Field()
    service_agent: str = Field()
    conversation_log: str = Field(sa_type=Text)
    conversation_log_vec: list[float] = text_embed.VectorField(
        source_field="conversation_log"
    )
    created_date: str = Field()
    resolved_date: str = Field()
    resolution_status: str = Field()
    product_name: str = Field()

pr_table = db.open_table(table_name)
cs_table = db.open_table(cs_table_name)

if pr_table is None:
    pr_table = db.create_table(schema=ProductReview, mode="exist_ok")
if cs_table is None:
    cs_table = db.create_table(schema=CSRecords, mode="exist_ok")

# Read data from CSV file
if pr_table.rows() == 0:
    print("Inserting product_reviews data into table...")

    df = pd.read_csv('setup/product_reviews.csv').fillna('')
    reviews_data = df.to_dict('records')

    # Insert records into table
    data_list = []
    for review in reviews_data:
        del review['review_content_vec'] # 需要删掉这个值，否则不会自动生成
        data_list.append(ProductReview(**review))
    pr_table.bulk_insert(data_list)
    print("Products reviews data inserted.")

if cs_table.rows() == 0:
    print("Inserting customer_service_records data into table...")

    df2 = pd.read_csv('setup/customer_service_records.csv').fillna('')
    cs_data = df2.to_dict('records')

    # Insert records into table
    cs_list = []
    for cs in cs_data:
        del cs['conversation_log_vec'] # 需要删掉这个值，否则不会自动生成
        cs_list.append(CSRecords(**cs))
    cs_table.bulk_insert(cs_list)
    print("customer service records data inserted.")

# data_list = [ProductReview(**review) for review in reviews_data]
# pr_table.bulk_insert(data_list)


list1 = pr_table.search("ZenPhone").limit(3).to_list()

list2 = cs_table.search("ZenPhone").limit(3).to_list()
# list1 = pr_table.search("ZenPhone", search_type="hybrid").text_column("product_name").limit(3).to_list()
print("list1:", list1)
print("list2:", list2)
