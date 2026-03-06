import json
import os
from datetime import datetime
from typing import Dict, Any, List

def merge_buckets(input_path: str, output_path: str):
    """
    解析 ActivityWatch 导出的 JSON 文件，并将带有 '-synced-from-' 后缀的桶合并到原始桶中。
    """
    print(f"正在读取文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    buckets: Dict[str, Any] = data.get('buckets', {})
    merged_buckets: Dict[str, Any] = {}
    
    # 第一步：先收集所有不带同步后缀的桶
    for bid, bdata in buckets.items():
        if "-synced-from-" not in bid:
            merged_buckets[bid] = bdata
            if 'events' not in merged_buckets[bid]:
                merged_buckets[bid]['events'] = []
    
    # 第二步：处理所有带同步后缀的桶
    for bid, bdata in buckets.items():
        if "-synced-from-" in bid:
            base_id = bid.split("-synced-from-")[0]
            
            # 如果原始桶不存在，则创建一个新的
            if base_id not in merged_buckets:
                print(f"原始桶 {base_id} 不存在，将根据同步桶 {bid} 创建新桶。")
                merged_buckets[base_id] = bdata.copy()
                merged_buckets[base_id]['id'] = base_id
                # 初始 events 使用当前同步桶的事件
                merged_buckets[base_id]['events'] = list(bdata.get('events', []))
            else:
                # 合并事件
                source_events = bdata.get('events', [])
                if source_events:
                    merged_buckets[base_id]['events'].extend(source_events)
                    print(f"已将 {len(source_events)} 条事件从 {bid} 合并到 {base_id}")

    # 对每个桶的事件进行去重和排序
    for bid, bdata in merged_buckets.items():
        events = bdata.get('events', [])
        if not events:
            continue
            
        # 根据 timestamp 和 duration 去重
        # 使用 tuple 作为 key，因为 dict 不可哈希
        seen_events = set()
        unique_events = []
        
        # 排序以确保合并后的顺序正确
        events.sort(key=lambda x: x['timestamp'])
        
        for event in events:
            # 创建一个唯一的标识符，不包含 'id'，因为 ID 在不同桶中可能不同
            event_key = (event['timestamp'], event['duration'], json.dumps(event['data'], sort_keys=True))
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_events.append(event)
        
        bdata['events'] = unique_events
        
        # 更新元数据
        if unique_events:
            bdata['metadata']['start'] = unique_events[0]['timestamp']
            bdata['metadata']['end'] = unique_events[-1]['timestamp']

    # 写回文件
    data['buckets'] = merged_buckets
    print(f"正在保存合并后的文件到: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("合并完成！")

if __name__ == "__main__":
    input_file = "/Users/shichen/Downloads/aw-buckets-export (3).json"
    output_file = "/Users/shichen/Downloads/aw-buckets-export-merged.json"
    merge_buckets(input_file, output_file)
