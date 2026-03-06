#!/usr/bin/env python3
"""
通过 ActivityWatch 本地 API (默认 5600) 删除本机所有 bucket，便于清空后重新导入。
"""
import sys
from typing import Set

# 使用项目内的 aw-client（若在 venv 中已安装则直接 import）
try:
    from aw_client import ActivityWatchClient
except ImportError:
    import os
    _root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(_root, "aw-client"))
    from aw_client import ActivityWatchClient


def delete_all_buckets(host: str = "127.0.0.1", port: int = 5600) -> Set[str]:
    """
    连接指定地址的 aw-server，列出并删除所有 bucket。
    :return: 已删除的 bucket id 集合
    """
    client = ActivityWatchClient(
        client_name="delete-all-buckets-script",
        host=host,
        port=port,
    )
    buckets = client.get_buckets()
    if not buckets:
        print("当前没有任何 bucket，无需删除。")
        return set()

    deleted: Set[str] = set()
    for bucket_id in list(buckets.keys()):
        try:
            # 非测试模式下删除需传 force=True（即请求带 ?force=1）
            client.delete_bucket(bucket_id, force=True)
            deleted.add(bucket_id)
            print(f"已删除: {bucket_id}")
        except Exception as e:
            print(f"删除 {bucket_id} 失败: {e}", file=sys.stderr)

    print(f"共删除 {len(deleted)} 个 bucket。")
    return deleted


if __name__ == "__main__":
    port = 5600
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("用法: python delete_all_buckets.py [端口，默认 5600]", file=sys.stderr)
            sys.exit(1)

    delete_all_buckets(port=port)
