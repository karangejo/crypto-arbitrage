#!/usr/bin/env python3

import psycopg2

database_name = "crypto_arb"
table_name = "cg_arb"


def connect_db(database_name=None):
    if database_name == None:
        return psycopg2.connect(
            host="localhost",
            user='postgres',
            password='postgres')
    else:
        return psycopg2.connect(
            host="localhost",
            database=database_name,
            user='postgres',
            password='postgres')


def execute_db_command(command, database_name=None, insert_row=None):
    if database_name == None:
        conn = connect_db()
        conn.autocommit = True
    else:
        conn = connect_db(database_name)

    cursor = conn.cursor()
    try:
        if insert_row == None:
            cursor.execute(command)
        else:
            cursor.execute(command, insert_row)
        cursor.close()
        conn.commit()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_database():
    global database_name
    create_db_command = (
        f"""
            CREATE DATABASE {database_name} 
        """
    )
    execute_db_command(create_db_command)


def create_table(table_name):
    global database_name
    create_table_command = (
        f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name VARCHAR(10) NOT NULL,
                spread FLOAT NOT NULL,
                max_market VARCHAR(50) NOT NULL,
                min_market VARCHAR(50) NOT NULL,
                min_price float NOT NULL,
                max_price float NOT NULL
            )
        """
    )
    execute_db_command(create_table_command, database_name=database_name)


def insert_rows(table_name, rows):
    global database_name
    print("#######################################")
    print("#######################################")
    print("Database Insert:")
    for row in rows:
        execute_db_command(insert_command(table_name),
                           database_name=database_name, insert_row=row)


def insert_command(table_name):
    return (
        f"""
            INSERT INTO {table_name}(name, spread, max_market, min_market, max_price, min_price) VALUES (%(name)s, %(spread)s, %(max_market)s, %(min_market)s, %(max_price)s, %(min_price)s)
        """
    )


def delete_all_rows(table_name):
    global database_name
    command = (
        f"""
            DELETE FROM {table_name}
        """
    )
    execute_db_command(command, database_name=database_name)
