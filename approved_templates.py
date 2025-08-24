# pip install pandas openpyxl pymysql
import pandas as pd
import pymysql
from pymysql.constants.CLIENT import MULTI_STATEMENTS
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

excel_path = "JJ템플릿.xlsx"  # 파일 경로로 변경
sheet_name = "승인받은템플릿"

# 1) 엑셀 로드
df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")

# 2) 컬럼 매핑 (엑셀 헤더 → DB 컬럼)
df = df.rename(
    columns={
        "텍스트": "text_content",
        "분류 1차": "category_1",
        "분류 2차": "category_2",
        "자동 생성 제목": "auto_title",
        "템플릿 코드": "template_code",
        "버튼": "button_label",
        "공용/전용": "public_private",
        "업종분류": "industry",
        "목적분류": "purpose",
    }
)

# 3) 공용/전용 표준화(공백 제거)
df["public_private"] = df["public_private"].str.strip()

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
CREATE TABLE IF NOT EXISTS approved_templates (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  text_content TEXT NOT NULL,
  category_1 VARCHAR(100) NULL,
  category_2 VARCHAR(100) NULL,
  auto_title VARCHAR(255) NULL,
  template_code VARCHAR(120) NOT NULL,
  button_label VARCHAR(100) NULL,
  public_private VARCHAR(50) NULL,
  industry VARCHAR(100) NULL,
  purpose VARCHAR(100) NULL,
  src_sheet VARCHAR(100) NOT NULL DEFAULT '승인받은템플릿',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_template_code (template_code)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
"""

insert_sql = """
INSERT INTO approved_templates
(text_content, category_1, category_2, auto_title, template_code, button_label, public_private, industry, purpose, src_sheet)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
text_content=VALUES(text_content),
category_1=VALUES(category_1),
category_2=VALUES(category_2),
auto_title=VALUES(auto_title),
button_label=VALUES(button_label),
public_private=VALUES(public_private),
industry=VALUES(industry),
purpose=VALUES(purpose),
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
                row.get("auto_title", ""),
                row.get("template_code", ""),
                row.get("button_label", ""),
                row.get("public_private", ""),
                row.get("industry", ""),
                row.get("purpose", ""),
                sheet_name,
            )
            for _, row in df.iterrows()
        ]
        cur.executemany(insert_sql, data)
    conn.commit()

print(f"Upserted {len(df)} rows into approved_templates")
