import pymysql

conn = pymysql.connect(
    host='localhost',
    user='steve', 
    password='doolman',
    database='final-team-3'
)

cur = conn.cursor()

# 총 레코드 수 확인
cur.execute('SELECT COUNT(*) FROM rejected_templates')
total_count = cur.fetchone()[0]
print(f'총 레코드 수: {total_count}')

# 샘플 데이터 확인
cur.execute('SELECT template_code, LEFT(text_content, 50) FROM rejected_templates LIMIT 3')
print('\n샘플 데이터:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}...')

# 카테고리별 통계
cur.execute('SELECT category_1, COUNT(*) FROM rejected_templates GROUP BY category_1')
print('\n카테고리별 통계:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

conn.close()