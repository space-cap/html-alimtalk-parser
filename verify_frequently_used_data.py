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
cur.execute('SELECT COUNT(*) FROM frequently_used_template')
total_count = cur.fetchone()[0]
print(f'총 레코드 수: {total_count}')

# 모든 데이터 확인 (적은 수이므로)
cur.execute('SELECT template_code, LEFT(text_content, 80), category_1, public_private FROM frequently_used_template')
print('\n모든 템플릿 데이터:')
for i, row in enumerate(cur.fetchall(), 1):
    print(f'{i}. {row[0]}: {row[1]}... (분류: {row[2]}, 공용/전용: {row[3]})')

# 카테고리별 통계
cur.execute('SELECT category_1, COUNT(*) FROM frequently_used_template WHERE category_1 != "" GROUP BY category_1')
print('\n카테고리별 분포:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 공용/전용 분포
cur.execute('SELECT public_private, COUNT(*) FROM frequently_used_template WHERE public_private != "" GROUP BY public_private')
print('\n공용/전용 분포:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 템플릿 코드 중복 확인
cur.execute('SELECT COUNT(DISTINCT template_code) as unique_codes, COUNT(*) as total_records FROM frequently_used_template')
row = cur.fetchone()
print(f'\n유니크한 템플릿 코드: {row[0]}개 / 전체 레코드: {row[1]}개')

conn.close()