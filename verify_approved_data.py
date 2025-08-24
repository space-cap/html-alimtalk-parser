import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset=os.getenv("DB_CHARSET", "utf8mb4"),
)

cur = conn.cursor()

# 총 레코드 수 확인
cur.execute('SELECT COUNT(*) FROM approved_templates')
total_count = cur.fetchone()[0]
print(f'총 레코드 수: {total_count}')

# 샘플 데이터 확인
cur.execute('SELECT template_code, LEFT(text_content, 50), public_private FROM approved_templates LIMIT 5')
print('\n샘플 데이터:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}... ({row[2]})')

# 공용/전용 분포
cur.execute('SELECT public_private, COUNT(*) FROM approved_templates GROUP BY public_private')
print('\n공용/전용 분포:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 카테고리별 통계
cur.execute('SELECT category_1, COUNT(*) FROM approved_templates GROUP BY category_1 ORDER BY COUNT(*) DESC LIMIT 5')
print('\n상위 5개 카테고리:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

conn.close()