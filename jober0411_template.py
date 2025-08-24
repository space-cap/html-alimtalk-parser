# pip install pandas openpyxl pymysql
import pandas as pd
import pymysql
from pymysql.constants.CLIENT import MULTI_STATEMENTS

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

excel_path = "JJ템플릿.xlsx"  # 파일 경로로 변경
sheet_name = "Jober0411"

# 1) 엑셀 로드
df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")

# 2) 컬럼 매핑 (엑셀 헤더 → DB 컬럼)
df = df.rename(
    columns={
        "템플릿 코드": "template_code",
        "템플릿 이름": "template_name",
        "템플릿 내용": "template_body",
        "카테고리": "category",
        "서브카테고리": "subcategory",
        "제안 버튼명": "suggested_button",
    }
)

# 3) 값 정제(앞뒤 공백 제거)
for col in [
    "template_code",
    "template_name",
    "template_body",
    "category",
    "subcategory",
    "suggested_button",
]:
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
CREATE TABLE IF NOT EXISTS jober_jober0411_template (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  template_code VARCHAR(120) NOT NULL,
  template_name VARCHAR(200) NOT NULL,
  template_body TEXT NOT NULL,
  category VARCHAR(100) NULL,
  subcategory VARCHAR(120) NULL,
  suggested_button VARCHAR(120) NULL,
  src_sheet VARCHAR(100) NOT NULL DEFAULT 'Jober0411 템플릿',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_template_code (template_code),
  INDEX ix_category (category),
  INDEX ix_subcategory (subcategory)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
"""

insert_sql = """
INSERT INTO jober_jober0411_template
(template_code, template_name, template_body, category, subcategory, suggested_button, src_sheet)
VALUES (%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
template_name=VALUES(template_name),
template_body=VALUES(template_body),
category=VALUES(category),
subcategory=VALUES(subcategory),
suggested_button=VALUES(suggested_button),
src_sheet=VALUES(src_sheet);
"""

with conn:
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        data = [
            (
                row.get("template_code", ""),
                row.get("template_name", ""),
                row.get("template_body", ""),
                row.get("category", ""),
                row.get("subcategory", ""),
                row.get("suggested_button", ""),
                sheet_name,
            )
            for _, row in df.iterrows()
        ]
        cur.executemany(insert_sql, data)
    conn.commit()

print(f"Upserted {len(df)} rows into jober0411_templates")
