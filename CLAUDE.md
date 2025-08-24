# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python utility that parses Korean AlimTalk template data from Excel files and imports it into a MySQL database. The project processes rejected template information including categories, rejection reasons, and template metadata.

## Required Dependencies

Install required packages:
```bash
pip install pandas openpyxl pymysql
```

## Database Configuration

The project connects to MySQL with these hardcoded credentials:
- Host: localhost:3306
- User: steve
- Password: doolman
- Database: final-team-3

## File Structure

- `rejected_templates.py`: Main script that loads Excel data and inserts into MySQL
- `반려받은템플릿.xlsx`: Source Excel file containing rejected template data
- `소스보기.html`: Large HTML file (298KB) containing AlimTalk template UI examples

## Data Processing

The script maps Korean Excel column headers to English database column names:
- "텍스트" → text_content
- "분류 1차" → category_1
- "분류 2차" → category_2
- "자동 생성 제목" → auto_title
- "반려 사유" → reject_reason
- "반려 사유(요약)" → reject_reason_summary
- "이미지 여부" → has_image (converted to boolean)
- "템플릿 코드" → template_code

## Running the Script

Execute the main script:
```bash
python rejected_templates.py
```

The script will:
1. Create the `rejected_templates` table if it doesn't exist
2. Load and process the Excel data
3. Insert all records into the database
4. Print confirmation of inserted row count