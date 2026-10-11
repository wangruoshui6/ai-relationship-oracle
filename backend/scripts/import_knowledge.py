"""通用知识库种子数据导入脚本。

从任意 JSON 文件（条目数组，字段与 KnowledgeDocument 一致）导入 knowledge_documents 表。
塔罗种子沿用 scripts/import_tarot_knowledge.py；本脚本用于八字、心理学等后续领域。

用法：
  # 1) 生成种子 JSON 供审查（默认只输出，不写库）
  python scripts/import_knowledge.py --file data/knowledge/bazi_knowledge.json

  # 2) 直接写入数据库（幂等，按 domain+doc_key upsert）
  python scripts/import_knowledge.py --file data/knowledge/bazi_knowledge.json --import
  python scripts/import_knowledge.py --file data/knowledge/psychology_knowledge.json --import

  # 3) 批量导入多个文件
  python scripts/import_knowledge.py --file data/knowledge/bazi_knowledge.json data/knowledge/psychology_knowledge.json --import
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

DEFAULT_FILES = [
    BACKEND_DIR / "data" / "knowledge" / "bazi_knowledge.json",
    BACKEND_DIR / "data" / "knowledge" / "psychology_knowledge.json",
]


def load_records(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("records", [])
    return data


def import_to_db(records: list[dict]) -> tuple[int, int]:
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.db.session import SessionLocal
    from app.models.knowledge_document import KnowledgeDocument

    session: Session = SessionLocal()
    inserted, updated = 0, 0
    try:
        for rec in records:
            existing = session.scalar(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.domain == rec["domain"],
                    KnowledgeDocument.doc_key == rec["doc_key"],
                )
            )
            if existing is None:
                session.add(KnowledgeDocument(**rec))
                inserted += 1
            else:
                for field, value in rec.items():
                    setattr(existing, field, value)
                updated += 1
        session.commit()
    finally:
        session.close()
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description="导入通用知识库种子数据")
    parser.add_argument(
        "--file", nargs="+", type=Path,
        help="JSON 数据文件路径（可多个）；缺省用默认八字/心理学文件",
    )
    parser.add_argument("--import", dest="do_import", action="store_true", help="直接写入数据库")
    args = parser.parse_args()

    files = args.file or DEFAULT_FILES
    total_inserted = total_updated = total_records = 0
    for path in files:
        if not path.exists():
            print(f"[跳过] 文件不存在：{path}")
            continue
        records = load_records(path)
        total_records += len(records)
        domains = sorted({r.get("domain") for r in records})
        print(f"[解析] {path.name}: {len(records)} 条, domain={domains}")
        if args.do_import:
            inserted, updated = import_to_db(records)
            total_inserted += inserted
            total_updated += updated

    if args.do_import:
        print(f"入库完成：新增 {total_inserted} 条，更新 {total_updated} 条，共 {total_records} 条")
    else:
        print(f"共解析 {total_records} 条（未写库，加 --import 入库）")


if __name__ == "__main__":
    main()
