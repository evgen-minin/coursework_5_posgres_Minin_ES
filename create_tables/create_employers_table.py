import csv
import psycopg2


def create_table_from_csv(config, table_name, csv_file):
    dbname = config['DB_NAME']
    user = config['USER']
    password = config['PASSWORD']
    host = config.get('HOST')

    with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=dbname,
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')")
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            create_table = input(
                f"Таблицы {table_name} не существует. Хотите создать таблицу и загрузить данные? (да/нет): ")

            if create_table.lower() != 'да':
                return

            with open(csv_file, 'r') as file:
                csv_data = csv.reader(file)
                header = next(csv_data)

                columns = []
                for column in header:
                    if column in ['vacancy name', 'vacancy id', 'vacancy location']:
                        columns.append(f'"{column}" TEXT')
                    else:
                        columns.append(f'"{column}" VARCHAR(255)')

                columns_str = ', '.join(columns)
                create_table_query = f'CREATE TABLE "{table_name}" ({columns_str})'
                cursor.execute(create_table_query)

                unique_ids = set()
                insert_query = f"INSERT INTO \"{table_name}\" VALUES ({', '.join(['%s'] * len(header))})"
                for row in csv_data:
                    if row[1] not in unique_ids:
                        unique_ids.add(row[1])
                        cursor.execute(insert_query, tuple(row))

            connection.commit()

            print(f"Таблица {table_name} успешно создана и загружены данные из файла {csv_file}.")
        else:
            load_data = input(f"Таблица {table_name} уже существует. Хотите загрузить новые данные? (да/нет): ")

            if load_data.lower() != 'да':
                return

            with open(csv_file, 'r') as file:
                csv_data = csv.reader(file)
                header = next(csv_data)

                unique_ids = set()
                insert_query = f"INSERT INTO \"{table_name}\" VALUES ({', '.join(['%s'] * len(header))})"
                for row in csv_data:
                    if row[1] not in unique_ids:
                        unique_ids.add(row[1])
                        cursor.execute(insert_query, tuple(row))
            connection.commit()

            print(f"Новые данные успешно загружены в таблицу {table_name}.")
