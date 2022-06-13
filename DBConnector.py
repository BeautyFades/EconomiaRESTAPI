import logging
import sqlalchemy as sq

class DBConnector():

    def __init__(self, db_type: str, db_user: str, db_pw: str, db_host: str, 
                db: str
                ):

        self.db_type = db_type
        self.db_user = db_user
        self.db = db
        self.engine = sq.create_engine(f'{db_type}://{db_user}:{db_pw}@{db_host}/{db}')
        logging.info(f'Connected to {self.db_type}/{self.db} as {self.db_user}')


    def execute_query(self, query: str, verbose: bool = False):
        with self.engine.connect() as con:
            logging.info(f'Executing query: {query}')
            query_res = con.execute(query)

            if verbose:
                res = []
                for row in query_res:
                    res.append(row)
                return query_res, res
        
        return query_res