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
cur.execute('SELECT COUNT(*) FROM other_service_approved_templates')
total_count = cur.fetchone()[0]
print(f'총 레코드 수: {total_count}')

# 샘플 데이터 확인
cur.execute('SELECT template_code, LEFT(text_content, 50), keywords FROM other_service_approved_templates LIMIT 5')
print('\n샘플 데이터:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}... (keywords: {row[2]})')

# 카테고리별 통계
cur.execute('SELECT category_1, COUNT(*) FROM other_service_approved_templates WHERE category_1 != "" GROUP BY category_1 ORDER BY COUNT(*) DESC LIMIT 5')
print('\n상위 5개 카테고리:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 키워드가 있는 데이터 확인
cur.execute('SELECT COUNT(*) FROM other_service_approved_templates WHERE keywords != ""')
keyword_count = cur.fetchone()[0]
print(f'\n키워드가 있는 템플릿: {keyword_count}개')

# 템플릿 코드 중복 확인
cur.execute('SELECT COUNT(DISTINCT template_code) as unique_codes, COUNT(*) as total_records FROM other_service_approved_templates')
row = cur.fetchone()
print(f'\n유니크한 템플릿 코드: {row[0]}개 / 전체 레코드: {row[1]}개')

conn.close()