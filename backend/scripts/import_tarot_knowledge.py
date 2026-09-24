"""塔罗知识库种子数据导入脚本。

数据来源：Love Oracle Open Dataset（CC BY 4.0）
  https://www.loveoracle.app/dataset/love-tarot.json

用法：
  # 1) 生成种子 JSON（供审查，不写库）
  python scripts/import_tarot_knowledge.py

  # 2) 直接写入数据库（幂等，按 domain+doc_key upsert）
  python scripts/import_tarot_knowledge.py --import

输出：
  data/tarot/seed_knowledge_documents.json  —— 种子数据（78 牌 × 正逆位 = 156 条）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

SEED_FILE = BACKEND_DIR / "data" / "tarot" / "love-tarot.json"
OUTPUT_FILE = BACKEND_DIR / "data" / "tarot" / "seed_knowledge_documents.json"
DOMAIN = "tarot"
SOURCE = "Love Oracle Open Dataset"
LICENSE = "CC BY 4.0"
LANGUAGE = "zh"

ORIENTATION_ZH = {"upright": "正位", "reversed": "逆位"}


def build_records(data: dict) -> list[dict]:
    cards = data.get("cards", data)
    records: list[dict] = []
    for card in cards:
        slug = card["slug"]
        name_en = card["name"]
        zh = card.get("love", {}).get("zh", {})
        zh_name = zh.get("name") or name_en
        for orientation in ("upright", "reversed"):
            meaning_zh = zh.get(orientation, "")
            meaning_en = card.get("love", {}).get("en", {}).get(orientation, "")
            yes_no = card.get("yes_no", {}).get(orientation)
            doc_key = f"{slug}__{orientation}"
            title_zh = f"{zh_name} · {ORIENTATION_ZH[orientation]}"
            title_en = f"{name_en} · {orientation.capitalize()}"
            content = (
                f"【{title_zh}】{meaning_zh}。"
                f"（{title_en}: {meaning_en}）"
                + (f" Yes/No 极性：{yes_no}。" if yes_no else "")
            )
            meta = {
                "arcana": card.get("arcana"),
                "number": card.get("number"),
                "suit": card.get("suit"),
                "element": card.get("element"),
                "decan": card.get("decan"),
                "yes_no": card.get("yes_no"),
            }
            records.append(
                {
                    "domain": DOMAIN,
                    "doc_key": doc_key,
                    "title_zh": title_zh,
                    "title_en": title_en,
                    "content": content,
                    "keywords": [],
                    "meta": meta,
                    "orientation": orientation,
                    "language": LANGUAGE,
                    "source": SOURCE,
                    "license": LICENSE,
                    "embedding_id": None,
                    "is_active": True,
                }
            )
    return records


def import_to_db(records: list[dict]) -> None:
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
    print(f"入库完成：新增 {inserted} 条，更新 {updated} 条，共 {inserted + updated} 条")


def main() -> None:
    parser = argparse.ArgumentParser(description="导入塔罗知识库种子数据")
    parser.add_argument("--import", dest="do_import", action="store_true", help="直接写入数据库")
    args = parser.parse_args()

    if not SEED_FILE.exists():
        print(f"未找到语料文件：{SEED_FILE}")
        print("请先下载：curl.exe -s -o backend/data/tarot/love-tarot.json https://www.loveoracle.app/dataset/love-tarot.json")
        sys.exit(1)

    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    records = build_records(data)
    print(f"解析完成：{data.get('card_count', len(data.get('cards', [])))} 张牌 → {len(records)} 条知识条目")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"种子数据已输出：{OUTPUT_FILE}")

    if args.do_import:
        import_to_db(records)


if __name__ == "__main__":
    main()
