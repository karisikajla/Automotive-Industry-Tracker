import pymysql
import pandas as pd
import logging

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "automotive_tracker",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logging.info("MySQL connection established.")
        return conn
    except Exception as e:
        logging.error(f"MySQL connection failed: {e}")
        raise


def populate_financials(df: pd.DataFrame):
    conn = get_connection()
    inserted = 0
    skipped = 0
    try:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                try:
                    make = str(row.get("data.make", "Unknown"))
                    model = str(row.get("data.model", "Unknown"))
                    year = int(row["data.year"]) if pd.notna(row.get("data.year")) else None
                    recalls_raw = row.get("data.recalls", "")
                    recall_count = len(str(recalls_raw).split(",")) if recalls_raw and str(recalls_raw) not in ["", "[]", "nan"] else 0
                    source = str(row.get("source", "unknown"))
                    version = float(row["version"]) if pd.notna(row.get("version")) else None
                    collection_name = str(row.get("_collection", "unknown"))
                    release_year = int(row["release_year"]) if pd.notna(row.get("release_year")) else None
                    fetched_at = str(row.get("fetched_at", ""))

                    cursor.execute(
                        """
                        INSERT INTO vehicle_financials
                        (make, model, year, recall_count, source, version, collection_name, release_year, fetched_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (make, model, year, recall_count, source, version, collection_name, release_year, fetched_at),
                    )
                    inserted += 1
                except Exception as row_err:
                    logging.warning(f"Skipped row: {row_err}")
                    skipped += 1
        conn.commit()
        logging.info(f"Inserted {inserted} rows, skipped {skipped} rows.")
    finally:
        conn.close()


def query_financials() -> pd.DataFrame:
    import sqlalchemy
    engine = sqlalchemy.create_engine("mysql+pymysql://root@localhost/automotive_tracker")
    df = pd.read_sql("SELECT * FROM vehicle_financials WHERE year IS NOT NULL", engine)
    logging.info(f"Queried {len(df)} rows from vehicle_financials.")
    return df