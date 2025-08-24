# pip install pandas openpyxl pymysql python-dotenv
import pandas as pd
import pymysql
from pymysql.constants.CLIENT import MULTI_STATEMENTS
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1) 엑셀 로드
excel_path = "반려받은템플릿.xlsx"  # 엑셀 파일 경로로 변경
sheet_name = "Sheet1"

df = pd.read_excel(excel_path, sheet_name=sheet_name, dtype=str).fillna("")

# 2) 컬럼 매핑 (엑셀 헤더가 정확히 아래와 동일하다고 가정)
df = df.rename(
    columns={
        "텍스트": "text_content",
        "분류 1차": "category_1",
        "분류 2차": "category_2",
        "자동 생성 제목": "auto_title",
        "반려 사유": "reject_reason",
        "반려 사유(요약)": "reject_reason_summary",
        "이미지 여부": "has_image",
        "템플릿 코드": "template_code",
    }
)


# 3) 값 정제: 이미지 여부(X -> 0, 그 외(공백 제외) -> 1)
def to_bool(x: str) -> int:
    x = (x or "").strip()
    if x == "" or x.upper() == "X":
        return 0
    return 1


df["has_image"] = df["has_image"].map(to_bool)

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

# 5) 테이블이 없으면 생성 (DDL 실행)
create_table_sql = """
CREATE TABLE IF NOT EXISTS rejected_templates (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  text_content TEXT NOT NULL,
  category_1 VARCHAR(100) NULL,
  category_2 VARCHAR(100) NULL,
  auto_title VARCHAR(255) NULL,
  reject_reason TEXT NULL,
  reject_reason_summary TEXT NULL,
  has_image TINYINT(1) NOT NULL DEFAULT 0,
  template_code VARCHAR(100) NOT NULL,
  src_sheet VARCHAR(100) NOT NULL DEFAULT '반려 받은 템플릿',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
"""

insert_sql = """
INSERT INTO rejected_templates
(text_content, category_1, category_2, auto_title, reject_reason, reject_reason_summary, has_image, template_code, src_sheet)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
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
                row.get("reject_reason", ""),
                row.get("reject_reason_summary", ""),
                int(row.get("has_image", 0)),
                row.get("template_code", ""),
                sheet_name,
            )
            for _, row in df.iterrows()
        ]
        cur.executemany(insert_sql, data)
    conn.commit()

print(f"Inserted {len(df)} rows into rejected_templates")
