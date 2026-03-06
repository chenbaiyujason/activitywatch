#!/usr/bin/env python3
"""
从 merged JSON 中把事件同步到本机已存在的 bucket 里（不创建新 bucket，避免 BucketAlreadyExists）。
只对「服务器上已存在的 bucket」追加文件中多出来的事件，并按 (timestamp, duration, data) 去重。
"""
import argparse
import json
import os
import sys
from datetime import timedelta
from typing import Any, Dict, List, Set, Tuple

try:
    from aw_client import ActivityWatchClient
    from aw_core.models import Event
except ImportError:
    _root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(_root, "aw-client"))
    sys.path.insert(0, os.path.join(_root, "aw-core"))
    from aw_client import ActivityWatchClient
    from aw_core.models import Event


# 每批插入的事件数，避免单次请求过大
INSERT_BATCH_SIZE = 500


def event_key(e: Dict[str, Any]) -> Tuple[str, float, str]:
    """用于去重的键：(timestamp, duration, data 的规范 JSON)。"""
    ts = e.get("timestamp", "")
    dur = e.get("duration", 0.0)
    if isinstance(dur, (int, float)):
        pass
    else:
        dur = float(getattr(dur, "total_seconds", lambda: 0)())
    data = e.get("data") or {}
    return (ts, float(dur), json.dumps(data, sort_keys=True))


def load_merged_buckets(path: str) -> Dict[str, Any]:
    """加载 merged JSON 中的 buckets。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("buckets", {})


def existing_event_keys(
    client: ActivityWatchClient,
    bucket_id: str,
) -> Set[Tuple[str, float, str]]:
    """获取该 bucket 在服务器上已有事件的去重键集合。"""
    try:
        events = client.get_events(bucket_id, limit=-1)
    except Exception:
        return set()
    out: Set[Tuple[str, float, str]] = set()
    for e in events:
        d = e.to_json_dict() if hasattr(e, "to_json_dict") else dict(e)
        out.add(event_key(d))
    return out


def dict_to_event(e: Dict[str, Any]) -> Event:
    """将 merged 文件中的事件 dict 转为 Event，不传 id 让服务端分配。"""
    dur = e.get("duration", 0.0)
    if isinstance(dur, (int, float)):
        dur = timedelta(seconds=float(dur))
    return Event(
        timestamp=e["timestamp"],
        duration=dur,
        data=e.get("data") or {},
    )


def sync_events_from_merged(
    merged_path: str,
    host: str = "127.0.0.1",
    port: int = 5600,
) -> None:
    """
    从 merged 文件读取每个 bucket 的事件，仅对服务器上已存在的 bucket 追加缺失事件。
    """
    print(f"正在读取: {merged_path}")
    buckets = load_merged_buckets(merged_path)
    if not buckets:
        print("文件中没有 buckets，退出。")
        return

    client = ActivityWatchClient(
        client_name="sync-events-from-merged",
        host=host,
        port=port,
    )
    server_buckets = client.get_buckets()
    server_ids = set(server_buckets.keys())

    for bucket_id in sorted(buckets.keys()):
        if bucket_id not in server_ids:
            print(f"  跳过（服务器上无此 bucket）: {bucket_id}")
            continue

        file_events: List[Dict[str, Any]] = buckets[bucket_id].get("events") or []
        if not file_events:
            continue

        existing = existing_event_keys(client, bucket_id)
        to_insert: List[Dict[str, Any]] = [
            e for e in file_events
            if event_key(e) not in existing
        ]
        if not to_insert:
            print(f"  {bucket_id}: 无新增事件")
            continue

        events_as_objects: List[Event] = [dict_to_event(e) for e in to_insert]
        total = 0
        for i in range(0, len(events_as_objects), INSERT_BATCH_SIZE):
            batch = events_as_objects[i : i + INSERT_BATCH_SIZE]
            client.insert_events(bucket_id, batch)
            total += len(batch)
        print(f"  {bucket_id}: 已同步 {total} 条新事件")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 merged JSON 中的事件同步到本机已存在的 bucket（不创建新 bucket）。",
    )
    parser.add_argument(
        "merged_path",
        nargs="?",
        default="/Users/shichen/Downloads/aw-buckets-export-merged.json",
        help="merged 导出文件路径",
    )
    parser.add_argument("--port", type=int, default=5600, help="aw-server 端口")
    parser.add_argument("--host", default="127.0.0.1", help="aw-server 主机")
    args = parser.parse_args()

    if not os.path.isfile(args.merged_path):
        print(f"错误: 文件不存在: {args.merged_path}", file=sys.stderr)
        sys.exit(1)

    sync_events_from_merged(
        merged_path=args.merged_path,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
