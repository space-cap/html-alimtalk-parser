# pip install pandas openpyxl pymysql
import pandas as pd
import pymysql
from pymysql.constants.CLIENT import MULTI_STATEMENTS

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

excel_path = "JJ템플릿.xlsx"  # 엑셀 파일 경로로 변경
sheet_name = "Best템플릿"

# 1) 엑셀 로드
df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")

# 2) 컬럼 매핑 (엑셀 헤더 → DB 컬럼)
# 실제 컬럼명 확인 후 매핑
print("원본 컬럼:", list(df.columns))
df = df.rename(
    columns={
        "템플릿 주제": "template_subject",
        "활용 가능한 분야": "use_domain", 
        "업종": "industry",
        "템플릿 코드": "template_code",
        "버튼명": "button_label", 
        "템플릿 내용": "template_body",
        "비고": "note",
    }
)
print("매핑 후 컬럼:", list(df.columns))

# 3) 값 정제(앞뒤 공백 제거) - 실제 존재하는 컬럼만 처리
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

# 4) MySQL 연결 정보 (.env에서 로드)
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset=os.getenv("DB_CHARSET", "utf8mb4"),
    client_flag=MULTI_STATEMENTS,
)

create_table_sql = """
CREATE TABLE IF NOT EXISTS best_template (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  template_subject VARCHAR(200) NOT NULL,
  use_domain VARCHAR(200) NULL,
  industry VARCHAR(120) NULL,
  template_code VARCHAR(150) NOT NULL,
  button_label VARCHAR(120) NULL,
  template_body TEXT NOT NULL,
  note VARCHAR(500) NULL,
  src_sheet VARCHAR(100) NOT NULL DEFAULT 'best 템플릿',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_template_code (template_code),
  INDEX ix_subject (template_subject),
  INDEX ix_domain (use_domain),
  INDEX ix_industry (industry)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
"""

insert_sql = """
INSERT INTO best_template
(template_subject, use_domain, industry, template_code, button_label, template_body, note, src_sheet)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
template_subject=VALUES(template_subject),
use_domain=VALUES(use_domain),
industry=VALUES(industry),
button_label=VALUES(button_label),
template_body=VALUES(template_body),
note=VALUES(note),
src_sheet=VALUES(src_sheet);
"""

with conn:
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        data = [
            (
                row.get("template_subject", ""),
                row.get("활용 가능한 분야", ""),  # 매핑되지 않은 원본 컬럼명 사용
                row.get("industry", ""),
                row.get("template_code", ""),
                row.get("button_label", ""),
                row.get("template_body", ""),
                row.get("note", ""),
                sheet_name,
            )
            for _, row in df.iterrows()
        ]
        cur.executemany(insert_sql, data)
    conn.commit()

print(f"Upserted {len(df)} rows into best_templates")
