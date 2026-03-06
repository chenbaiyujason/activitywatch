#!/usr/bin/env python3
"""
从 merge1 文件中找出当前服务器上缺失的 bucket，并通过 API 仅导入这些 bucket。
用法: python import_missing_from_merge1.py [merge1.json 路径] [--port 5600]
"""
import argparse
import json
import os
import sys
from typing import Dict, Any, Set

try:
    from aw_client import ActivityWatchClient
except ImportError:
    _root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(_root, "aw-client"))
    from aw_client import ActivityWatchClient


# 默认 merge1 文件路径（与 merge_buckets.py 输出一致）
DEFAULT_MERGE1_PATH = "/Users/shichen/Downloads/aw-buckets-export-merged1.json"


def load_merge1_buckets(path: str) -> Dict[str, Any]:
    """从 merge1 JSON 加载 buckets 字典。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("buckets", {})


def get_missing_bucket_ids(merge1_buckets: Dict[str, Any], server_bucket_ids: Set[str]) -> Set[str]:
    """返回在 merge1 中存在但在服务器上不存在的 bucket id 集合。"""
    merge1_ids = set(merge1_buckets.keys())
    return merge1_ids - server_bucket_ids


def import_missing_buckets(
    merge1_path: str,
    host: str = "127.0.0.1",
    port: int = 5600,
) -> int:
    """
    从 merge1 文件导入当前服务器缺失的 bucket。
    :return: 实际导入的 bucket 数量
    """
    print(f"正在读取 merge1 文件: {merge1_path}")
    merge1_buckets = load_merge1_buckets(merge1_path)
    if not merge1_buckets:
        print("merge1 中没有任何 bucket，退出。")
        return 0

    client = ActivityWatchClient(
        client_name="import-missing-from-merge1",
        host=host,
        port=port,
    )
    server_buckets = client.get_buckets()
    server_ids = set(server_buckets.keys())

    missing_ids = get_missing_bucket_ids(merge1_buckets, server_ids)
    if not missing_ids:
        print("当前服务器已包含 merge1 中的全部 bucket，无需导入。")
        return 0

    print(f"发现 {len(missing_ids)} 个缺失的 bucket，开始导入：")
    imported = 0
    for bid in sorted(missing_ids):
        bucket = merge1_buckets[bid]
        try:
            # 确保 bucket  dict 含有 id 字段（部分导出可能用 key 作为 id）
            if bucket.get("id") != bid:
                bucket = {**bucket, "id": bid}
            client.import_bucket(bucket)
            imported += 1
            print(f"  已导入: {bid}")
        except Exception as e:
            print(f"  导入失败 {bid}: {e}", file=sys.stderr)

    print(f"共导入 {imported} 个 bucket。")
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从 merge1 JSON 中仅导入当前服务器缺失的 bucket。"
    )
    parser.add_argument(
        "merge1_path",
        nargs="?",
        default=DEFAULT_MERGE1_PATH,
        help=f"merge1 文件路径（默认: {DEFAULT_MERGE1_PATH}）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5600,
        help="aw-server 端口（默认: 5600）",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="aw-server 主机（默认: 127.0.0.1）",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.merge1_path):
        print(f"错误: 文件不存在: {args.merge1_path}", file=sys.stderr)
        sys.exit(1)

    import_missing_buckets(
        merge1_path=args.merge1_path,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
