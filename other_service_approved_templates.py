# pip install pandas openpyxl pymysql
import pandas as pd
import pymysql
from pymysql.constants.CLIENT import MULTI_STATEMENTS

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

excel_path = "JJ템플릿.xlsx"  # 엑셀 파일 경로로 변경
sheet_name = "타서비스승인받은템플릿"

# 1) 엑셀 로드
df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")

# 2) 컬럼 매핑 (엑셀 헤더 → DB 컬럼)
df = df.rename(
    columns={
        "텍스트": "text_content",
        "분류 1차": "category_1",
        "분류 2차": "category_2",
        "keyword": "keywords",
        "code": "template_code",
        "자동 생성 제목": "auto_title",
    }
)

# 3) 값 정제(공백 정리)
for col in ["category_1", "category_2", "keywords", "template_code", "auto_title"]:
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
CREATE TABLE IF NOT EXISTS other_service_approved_templates (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  text_content TEXT NOT NULL,
  category_1 VARCHAR(100) NULL,
  category_2 VARCHAR(100) NULL,
  keywords VARCHAR(1000) NULL,
  template_code VARCHAR(120) NOT NULL,
  auto_title VARCHAR(255) NULL,
  src_sheet VARCHAR(100) NOT NULL DEFAULT '타 서비스 승인 받은 템플릿',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_template_code (template_code),
  INDEX ix_cat1 (category_1),
  INDEX ix_cat2 (category_2)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
"""

insert_sql = """
INSERT INTO other_service_approved_templates
(text_content, category_1, category_2, keywords, template_code, auto_title, src_sheet)
VALUES (%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
text_content=VALUES(text_content),
category_1=VALUES(category_1),
category_2=VALUES(category_2),
keywords=VALUES(keywords),
auto_title=VALUES(auto_title),
src_sheet=VALUES(src_sheet);
"""

with conn:
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        data = [
            (
                row.get("text_content", ""),
                row.get("category_1", ""),
                row.get("category_2", ""),
                row.get("keywords", ""),
                row.get("template_code", ""),
                row.get("auto_title", ""),
                sheet_name,
            )
            for _, row in df.iterrows()
        ]
        cur.executemany(insert_sql, data)
    conn.commit()

print(f"Upserted {len(df)} rows into other_service_approved_templates")
