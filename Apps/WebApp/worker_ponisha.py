import json
import time
import threading
from datetime import datetime, timezone
import requests
from sqlalchemy import select
from Apps.WebApp.models import db, Project
from Apps.Notification.Notif import Notif
JSON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://ponisha.ir",
    "referer": "https://ponisha.ir/",
    "x-request-type": "csr",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-platform": '"Linux"',
}

def _ts_to_dt(ts):
    try:
        # ورودی‌های نمونه شما یونیکس ثانیه بودند
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except Exception:
        return None

def _safe_json(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return None

def fetch_page(session, api_url, bearer, payload, page):
    body = dict(payload)
    body["page"] = page
    headers = {**JSON_HEADERS, "authorization": f"Bearer {bearer}"}
    r = session.post(api_url, headers=headers, data=json.dumps(body), timeout=30)
    if r.status_code == 429:
        raise RuntimeError("Rate limited (429)")
    r.raise_for_status()
    return r.json()

def upsert_new_projects(app, page_json):
    """
    فقط رکوردهای جدید را درج می‌کند (بر اساس external_id یکتا).
    """
    data = (page_json or {}).get("data") or []
    if not isinstance(data, list):
        return 0

    inserted = 0
    with app.app_context():
        # مجموعه‌ای از external_id های موجود برای فیلتر سریع
        existing_ids = {
            eid for (eid,) in db.session.execute(
                select(Project.external_id).where(Project.external_id.in_([item.get("id") for item in data if item.get("id")]))
            ).all()
        }

        for item in data:
            ext_id = str(item.get("id")) if item.get("id") is not None else None
            if not ext_id or ext_id in existing_ids:
                continue  # موجود است → رد

            p = Project(
                external_id=ext_id,
                title=item.get("title") or "",
                slug=item.get("slug"),
                description=item.get("description"),
                priority=item.get("priority"),
                amount_min=item.get("amount_min"),
                amount_max=item.get("amount_max"),
                bidding_closed_at=_ts_to_dt(item.get("bidding_closed_at")),
                approved_at=_ts_to_dt(item.get("approved_at")),
                billboarded_at=_ts_to_dt(item.get("billboarded_at")),
                promotions_json=_safe_json(item.get("promotions")),
                skills_json=_safe_json(item.get("skills")),
                project_bids_count=item.get("project_bids_count"),
                bidders_json=_safe_json(item.get("bidders")),
            )
            db.session.add(p)
            Notif(f"[*] {item.get('title')} - {item.get('amount_min')} - {item.get('amount_max')}",1)
            inserted += 1

        if inserted:
            db.session.commit()

    return inserted

def ponisha_loop(app, cfg, stop_event: threading.Event):
    """
    هر INTERVAL_SEC کل صفحات را پیمایش می‌کند و فقط پروژه‌های جدید را وارد DB می‌کند.
    """
    per_page = int(cfg.get("PONISHA_PER_PAGE", 20))
    user_id = cfg.get("user_id")
    payload = {
        "query": "",
        "page": 1,
        "per_page": per_page,
        "filter_skills_by_user_id": str(user_id) if user_id else None,
        "sort": cfg.get("PONISHA_SORT", "billboarded_at"),
        "order": cfg.get("PONISHA_ORDER", "desc"),
        "filters": {
            "is_open_projects": True,
            "skills": [],
            "category": [],
            "promotions": [],
        },
    }
    payload = {k: v for k, v in payload.items() if v is not None} 

    session = requests.Session()

    while not stop_event.is_set():
        try:
            total_pages = 1
            page = 1
            total_inserted = 0

            while page <= total_pages and not stop_event.is_set():
                try:
                    j = fetch_page(session, cfg.get("PONISHA_API"), cfg.get("token"), payload, page)
                except Exception as e:
                    print(f"[WORKER] fetch page {page} error: {e}")
                    # اگر محدودیت نرخ یا خطا بود، کمی صبر کن
                    stop_event.wait(10)
                    break

                meta = (j or {}).get("meta") or {}
                pgn = meta.get("pagination") or {}
                total_pages = int(pgn.get("total_pages") or 1)
                inserted = upsert_new_projects(app, j)
                total_inserted += inserted
                print(f"[WORKER] page {page}/{total_pages} → inserted: {inserted}")
                page += 1

            print(f"[WORKER] cycle done. total inserted this cycle: {total_inserted}")
        except Exception as e:
            print(f"[WORKER] loop error: {e}")

        # منتظر دوره‌ی بعدی (قابل قطع)
        stop_event.wait(int(cfg.get("INTERVAL_SEC")))
