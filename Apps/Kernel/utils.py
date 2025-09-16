
import os
from json import JSONDecodeError
from typing import Any, Dict, List, Union
from pathlib import Path
import json
from datetime import datetime, timezone

class Utils:
    def __init__(self):
        pass

    

    def _extract_one_user(self,d: Dict[str, Any]) -> Dict[str, Any]:

        if "data" in d and isinstance(d["data"], dict):
            d = d["data"]

        return {
            "id": d.get("user_id"),
            "username": d.get("username"),
            "email": d.get("email"),
            "mobile": d.get("mobile"),
            "verified": d.get("verified"),
            "followers": d.get("followers"),
            "followings": d.get("followings"),
            "rank": d.get("rank"),
            "timezone": d.get("tz"),
            "type": d.get("type"),
            "score": d.get("total_score"),
            "feedback": {
                "count": d.get("feedback_count"),
                "rate": d.get("feedback_rate"),
            },
            "plan": {
                "type": d.get("plan", {}).get("type") if isinstance(d.get("plan"), dict) else None,
                "title": d.get("plan", {}).get("title") if isinstance(d.get("plan"), dict) else None,
                "credit": d.get("plan", {}).get("credit_coin_count") if isinstance(d.get("plan"), dict) else None,
                "debit": d.get("plan", {}).get("debit_coin_count") if isinstance(d.get("plan"), dict) else None,
            },
            "is_pro": d.get("ponisha_pro", {}).get("is_pro") if isinstance(d.get("ponisha_pro"), dict) else None,
            "is_online": d.get("is_online"),
            "avatar": d.get("avatar"),
        }

    def extract_users_from_file(self,file_path: Union[str, Path]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        file_path = Path("sessions/"+file_path)
        if not file_path.exists():
            print(f"[ERR] File not found: {file_path.resolve()}")
            return {}

        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            print("[ERR] File is empty.")
            return {}

        try:
            obj = json.loads(text)
            print("[OK] Parsed as standard JSON.")
        except JSONDecodeError:
            print("[WARN] Not standard JSON, trying NDJSON (one JSON per line)...")
            lines = [ln for ln in text.splitlines() if ln.strip()]
            objs = []
            for i, ln in enumerate(lines, 1):
                try:
                    objs.append(json.loads(ln))
                except JSONDecodeError as e:
                    print(f"[ERR] Line {i} is not valid JSON: {e}")
            if not objs:
                print("[ERR] Could not parse file as NDJSON either.")
                return {}
            obj = objs

        if isinstance(obj, dict):
            out = self._extract_one_user(obj)
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return out
        elif isinstance(obj, list):
            out_list = []
            for item in obj:
                if not isinstance(item, dict):
                    print("[WARN] Skipping non-dict item in array.")
                    continue
                out_list.append(self._extract_one_user(item))
            print(json.dumps(out_list, ensure_ascii=False, indent=2))
            return out_list
        else:
            print("[ERR] Parsed JSON is neither dict nor list.")
            return {}
        
    def _ts_to_iso_utc(self,ts: Union[int, float, None]) -> Union[str, None]:
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
        except Exception:
            return None

    def extract_ponisha_profile(self,obj: Dict[str, Any]) -> Dict[str, Any]:
        root = obj.get("data", obj)

        user = root.get("user", {}) or {}
        profile = root.get("profile", {}) or {}
        stats = root.get("statistics", {}) or {}
        progress = root.get("progress_step", {}) or {}
        cover = root.get("cover", {}) or {}
        avatar_block = root.get("avatar", {}) or {}

        avatar_url = None
        if isinstance(avatar_block, dict):
            avatar_url = avatar_block.get("url")
        if not avatar_url:
            av = user.get("avatar")
            avatar_url = av.get("url") if isinstance(av, dict) else (av if isinstance(av, str) else None)

        skills = root.get("skills", []) or []
        skills_slim = [{"id": s.get("id"), "title": s.get("title")} for s in skills if isinstance(s, dict)]

        return {
            "id": user.get("user_id"),
            "username": user.get("username"),
            "verified": user.get("verified"),
            "rank": user.get("rank"),
            "timezone": user.get("timezone"),
            "type": user.get("type"),
            "plan": user.get("plan"),
            "is_pro": user.get("is_pro"),
            "is_online": user.get("is_online"),
            "followers": user.get("followers"),
            "registered_at": {
                "unix": user.get("registered_at"),
                "iso_utc": self._ts_to_iso_utc(user.get("registered_at")),
            },
            "profile": {
                "name_verified": profile.get("name_verified"),
                "gender": profile.get("gender"),
                "languages": profile.get("languages"),
                "city": {
                    "id": (profile.get("city") or {}).get("id") if isinstance(profile.get("city"), dict) else None,
                    "name": (profile.get("city") or {}).get("name") if isinstance(profile.get("city"), dict) else None,
                },
                "job_title": profile.get("job_title"),
                "job_description": profile.get("job_description"),
            },
            "media": {
                "avatar_url": avatar_url,
                "cover_url": cover.get("url"),
            },
            "skills": skills_slim,
            "stats": {
                "completed_projects": stats.get("completed_projects_count"),
                "active_projects": stats.get("active_projects_count"),
                "created_projects": stats.get("created_projects_count"),
                "feedback_count": stats.get("feedback_count"),
                "feedback_rate": stats.get("feedback_rate"),
                "portfolio_count": stats.get("portfolios_count"),
                "portfolio_views": stats.get("portfolio_views"),
                "profile_views": stats.get("profile_views"),
                "total_score": stats.get("total_score"),
                "portfolio_likes": stats.get("portfolio_like_count"),
            },
            "progress": {
                "percent": progress.get("percent"),
                "next_step_number": progress.get("next_step_number"),
            },
            "flags": {
                "has_portfolio": bool(stats.get("portfolios_count", 0)),
                "is_followed": root.get("is_follow"),
            },
        }

    def extract_from_profile_file(self,path: Union[str, Path]) -> Dict[str, Any]:
        p = Path(f"./sessions/{path}")
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p.resolve()}")
        text = p.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError("File is empty.")
        try:
            obj = json.loads(text)
        except JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e
        return self.extract_ponisha_profile(obj)
