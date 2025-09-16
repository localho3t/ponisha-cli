import os, json, time, threading
from datetime import datetime

def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def ingest_loop(app, db, Project, inbox_dir: str, interval_sec: int, stop_event: threading.Event):
    """
    حلقه‌ی Worker: فایل‌های JSON داخل inbox_dir را می‌خواند و داخل DB ذخیره می‌کند.
    قالب هر فایل می‌تواند:
      1) یک آبجکت پروژه
      2) آرایه‌ای از پروژه‌ها
    مثال آبجکت پروژه:
    {
      "title": "کرالر محصولات",
      "price_min": 15, "price_max": 30, "price_unit": "میلیون",
      "desc": "خزش محصولات فروشگاه...",
      "status": "در حال انجام",
      "updated_at": "2025-09-10"   # اختیاری (ISO یا YYYY-MM-DD)
    }
    """
    os.makedirs(inbox_dir, exist_ok=True)
    processed_dir = os.path.join(inbox_dir, "_processed")
    failed_dir = os.path.join(inbox_dir, "_failed")
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    while not stop_event.is_set():
        try:
            for name in list(os.listdir(inbox_dir)):
                if name.startswith("_"):
                    continue
                path = os.path.join(inbox_dir, name)
                if not os.path.isfile(path) or not name.lower().endswith(".json"):
                    continue

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                    data = json.loads(text)

                    # نرمال‌سازی به لیست
                    items = data if isinstance(data, list) else [data]

                    with app.app_context():
                        for item in items:
                            title = (item or {}).get("title")
                            if not title:
                                continue

                            updated_at_raw = (item or {}).get("updated_at")
                            if updated_at_raw:
                                try:
                                    # تاریخ ISO یا YYYY-MM-DD
                                    if len(updated_at_raw) == 10:
                                        updated_at = datetime.fromisoformat(updated_at_raw)
                                    else:
                                        updated_at = datetime.fromisoformat(updated_at_raw.replace("Z", "+00:00"))
                                except Exception:
                                    updated_at = datetime.utcnow()
                            else:
                                updated_at = datetime.utcnow()

                            p = Project(
                                title=title,
                                price_min=_safe_float((item or {}).get("price_min")),
                                price_max=_safe_float((item or {}).get("price_max")),
                                price_unit=(item or {}).get("price_unit"),
                                desc=(item or {}).get("desc"),
                                status=(item or {}).get("status"),
                                updated_at=updated_at,
                            )
                            db.session.add(p)
                        db.session.commit()

                    os.replace(path, os.path.join(processed_dir, name))
                except Exception as e:
                    # انتقال فایل مشکل‌دار
                    try:
                        os.replace(path, os.path.join(failed_dir, name))
                    except Exception:
                        pass
                    print(f"[INGEST][ERROR] {name}: {e}")
        except Exception as e:
            print(f"[INGEST][LOOP ERROR] {e}")

        stop_event.wait(interval_sec)  # قابل قطع با stop_event
