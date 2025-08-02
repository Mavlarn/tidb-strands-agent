import asyncio, os, logging, json

from strands import tool
from pytidb import TiDBClient

from setup.setup_embed import ProductReview, CSRecords

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("tidb_strands_agent")

db = TiDBClient.connect(
    host=os.getenv("TIDB_HOST"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    username=os.getenv("TIDB_USERNAME"),
    password=os.getenv("TIDB_PASSWORD"),
    database=os.getenv("TIDB_DATABASE"),
    enable_ssl=True,
)

@tool
def universal_search(table_name, query, filter_object, limit) -> list[dict]:
    """
    Execute universal search on TiDB database, including semantic search with vector search,
    and filtering some columns.

    Args:
    - table_name: the name of the table to query, should be one of the defined tables like product_reviews or customer_service_records
    - query: query sentance for semantic search
    - filter_object: for filtering one or serval columns, this param is an object with syntax:
    ```{
        "$and|$or": [
            {
                "field_name": {
                    <operator>: <value>
                }
            },
            {
                "field_name": {
                    <operator>: <value>
                }
            }
            ...
        ]
    }```
    or just simple filter like:
    ```{
        "field_name": {
            <operator>: <value>
        }
    }```
    operators are:
        $eq 	Equal to value
        $ne 	Not equal to value
        $gt 	Greater than value
        $gte 	Greater than or equal to value
        $lt 	Less than value
        $lte 	Less than or equal to value
        $in 	In a list of values
    this is an example:
    ```
        {
            "$and": [
                {
                    "created_at": {
                        "$gt": "2024-01-01"
                    }
                },
                {
                    "meta.category": {
                        "$in": ["tech", "science"]
                    }
                }
            ]
        }
    ```
    - limit: for limiting the number of results
    """
    try:
        if table_name == "product_reviews":
            vec_table = db.create_table(schema=ProductReview, mode="exist_ok")
        elif table_name == "customer_service_records":
            vec_table = db.create_table(schema=CSRecords, mode="exist_ok")
        else:
            log.error(f"Invalid table name: {table_name}")
            raise ValueError(f"Invalid table name: {table_name}")

        if type(filter_object) is str:
            filter_object = json.loads(filter_object)
        data_list = vec_table.search(query).filter(filter_object).limit(limit).to_list()
        return data_list
    except Exception as e:
        log.error(f"Failed to execute query: {query}, on table: {table_name}, to filter: {filter_object}, limit: {limit}, error: {e}")
        raise e
