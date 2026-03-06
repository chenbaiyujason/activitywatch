import json
from typing import Dict, Any

def extract_missing_buckets(input_path: str, output_path: str):
    """
    提取 DESKTOP-3G8QA55 缺失的桶并合并同步数据。
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    buckets: Dict[str, Any] = data.get('buckets', {})
    
    # 我们要提取的缺失桶 ID
    target_ids = [
        "aw-watcher-afk_DESKTOP-3G8QA55",
        "aw-watcher-vscode_DESKTOP-3G8QA55",
        "aw-watcher-vscode-agent_DESKTOP-3G8QA55"
    ]
    
    result_buckets = {}
    
    for target_id in target_ids:
        # 1. 寻找基础桶
        base_bucket = buckets.get(target_id)
        
        # 2. 寻找同步桶 (如果有)
        synced_id = f"{target_id}-synced-from-DESKTOP-3G8QA55"
        synced_bucket = buckets.get(synced_id)
        
        if not base_bucket and not synced_bucket:
            print(f"警告: 找不到桶 {target_id}")
            continue
            
        # 以基础桶或同步桶为模板
        merged = (base_bucket or synced_bucket).copy()
        merged['id'] = target_id
        events = list(merged.get('events', []))
        
        # 如果两者都存在，合并事件
        if base_bucket and synced_bucket:
            events.extend(synced_bucket.get('events', []))
            print(f"合并了 {target_id} 的原始数据和同步数据")
        
        # 去重和排序
        seen = set()
        unique_events = []
        events.sort(key=lambda x: x['timestamp'])
        for e in events:
            key = (e['timestamp'], e['duration'], json.dumps(e['data'], sort_keys=True))
            if key not in seen:
                seen.add(key)
                unique_events.append(e)
        
        merged['events'] = unique_events
        if unique_events:
            merged['metadata']['start'] = unique_events[0]['timestamp']
            merged['metadata']['end'] = unique_events[-1]['timestamp']
            
        result_buckets[target_id] = merged
        print(f"提取完成: {target_id} ({len(unique_events)} 条事件)")

    # 生成单独的 JSON
    output_data = {"buckets": result_buckets}
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"文件已保存至: {output_path}")

if __name__ == "__main__":
    extract_missing_buckets("/Users/shichen/Downloads/aw-buckets-export (3).json", "/Users/shichen/Downloads/missing-desktop-buckets.json")
