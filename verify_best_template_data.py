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
cur.execute('SELECT COUNT(*) FROM best_template')
total_count = cur.fetchone()[0]
print(f'총 레코드 수: {total_count}')

# 샘플 데이터 확인
cur.execute('SELECT template_code, template_subject, LEFT(template_body, 50) FROM best_template LIMIT 3')
print('\n샘플 데이터:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]} - {row[2]}...')

# 업종별 통계
cur.execute('SELECT industry, COUNT(*) FROM best_template WHERE industry != "" GROUP BY industry ORDER BY COUNT(*) DESC')
print('\n업종별 분포:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 활용 분야별 통계
cur.execute('SELECT use_domain, COUNT(*) FROM best_template WHERE use_domain != "" GROUP BY use_domain ORDER BY COUNT(*) DESC LIMIT 5')
print('\n상위 5개 활용 분야:')
for row in cur.fetchall():
    print(f'- {row[0]}: {row[1]}개')

# 템플릿 코드 중복 확인
cur.execute('SELECT COUNT(DISTINCT template_code) as unique_codes, COUNT(*) as total_records FROM best_template')
row = cur.fetchone()
print(f'\n유니크한 템플릿 코드: {row[0]}개 / 전체 레코드: {row[1]}개')

conn.close()