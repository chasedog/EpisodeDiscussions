import sqlite3
db_file = "C:\Dropbox\ForChase\EpisodeDiscussions\episodediscussions.sqlite"
training_data_table_name = "training_data"
tables = [{"name": training_data_table_name,
           "columns": [{"db": ("is_valid", "bool"), "ignore": True},
                       {"db": ("id", "varchar(30)", "PRIMARY KEY")},
                       {"db": ("title", "varchar(255)", "not null")},
                       {"db": ("created_utc", "datetime", "not null")},
                       {"db": ("subreddit", "varchar(72)", "not null"), "mapper": "display_name"},
                       {"db": ("is_self", "boolean", "not null")},
                       {"db": ("selftext", "text")},
                       {"db": ("author_flair_text", "varchar(200)")},
                       {"db": ("author", "varchar(200)"), "mapper": "name"},
                       {"db": ("archived", "boolean")},
                       {"db": ("downs", "int")},
                       {"db": ("ups", "int")},
                       {"db": ("score", "int")},
                       {"db": ("link_flair_text", "varchar(300)")},
                       {"db": ("url", "varchar(500)")},
                      ]}
         ]
class DB:
    def __init__(self):
        self.conn = sqlite3.connect(db_file)

    def getTrainingData(self, table=training_data_table_name):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.conn.row_factory = dict_factory
        cursor = self.cursor()
        cursor.execute("select * from {table}".format(table=table))
        return cursor.fetchall()

    def destroy(self):
        for table in tables:
            self.drop_table(table["name"])

    def drop_table(self, table_name):
        drop_table = "DROP TABLE IF EXISTS `{table_name}`".format(table_name=table_name)
        self.conn.execute(drop_table)
        self.conn.commit()

    def create(self):
        cursor = self.cursor()
        for table in tables:
            create_table = "CREATE TABLE {table_name} (".format(table_name=table["name"])

            columns = ",".join([" {definition}".format(definition=' '.join(column["db"])) for column in table["columns"]])

            end_create_table = ")"

            query = "{create_table} {columns} {end_create_table}".format(create_table=create_table, columns=columns, end_create_table=end_create_table)
            print(query)
            cursor.execute(query)
        self.conn.commit()

    def insertManyTrainingData(self, data):
        cursor = self.cursor()
        columnLenth = len(data[0]) if len(data) > 0 else 0
        placeholders = ",".join('?' * columnLenth)
        cursor.executemany(self._insert_into(training_data_table_name) + "VALUES ({})".format(placeholders), data)
        self.commit()
    def insertTrainingData(self, title, created_utc, raw_data, is_valid=None):
        cursor = self.cursor()
        data = (title, created_utc, raw_data, is_valid)
        cursor.execute(self._insert_into(training_data_table_name) + "VALUES (?,?,?,?)", data)
        self.commit()

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()

    def _insert_into(self, table_name):
        return 'INSERT INTO {table_name} '.format(table_name=table_name)

    def commit(self):
        self.conn.commit()