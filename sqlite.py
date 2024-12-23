import sqlite3

# 创建数据库连接，若不存在则创建名为movies.db的数据库文件
conn = sqlite3.connect('movies.db')
# 创建游标对象
cursor = conn.cursor()

# 创建表的SQL语句
create_table_sql = '''
CREATE TABLE IF NOT EXISTS movies (
    movie_name TEXT NOT NULL PRIMARY KEY,
    movie_rating REAL DEFAULT 0.0,
    movie_date TEXT,
    movie_type TEXT,
    movie_actors TEXT
);
'''
# 执行创建表的SQL语句
cursor.execute(create_table_sql)

# 插入数据的SQL语句
insert_sql = '''
INSERT INTO movies (movie_name, movie_rating, movie_date, movie_type, movie_actors)
VALUES (?,?,?,?,?);
'''
# 要插入的数据，以元组形式提供
movie_data = ('《流浪地球2》', 8.3, '2023-01-22', '科幻', '吴京、李雪健、沙溢')
# 执行插入语句
cursor.execute(insert_sql, movie_data)
# 提交事务，使插入操作生效
conn.commit()

# 查询数据的SQL语句
select_sql = "SELECT * FROM movies;"
# 执行查询语句
cursor.execute(select_sql)
# 获取所有查询结果
results = cursor.fetchall()
# 遍历并打印查询结果
for row in results:
    print(f"影片名字: {row[0]}, 影片评价: {row[1]}, 影片日期: {row[2]}, 影片类型: {row[3]}, 影片演员: {row[4]}")

# 关闭游标
cursor.close()
# 关闭数据库连接
conn.close()