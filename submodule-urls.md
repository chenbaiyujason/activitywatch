# 子模块 URL 对照表

## 根仓库 `.gitmodules`（activitywatch 根目录）

| 子模块 | 你本地当前指向 | 官方 ActivityWatch/activitywatch master |
|--------|----------------|----------------------------------------|
| aw-core | `https://github.com/ActivityWatch/aw-core.git` | 一致 |
| aw-client | `https://github.com/ActivityWatch/aw-client.git` | 一致 |
| aw-server | `https://github.com/ActivityWatch/aw-server.git` | 一致 |
| aw-watcher-afk | `https://github.com/ActivityWatch/aw-watcher-afk.git` | 一致 |
| aw-qt | `https://github.com/ActivityWatch/aw-qt.git` | 一致 |
| aw-watcher-window | `https://github.com/ActivityWatch/aw-watcher-window.git` | 一致 |
| aw-server-rust | `https://github.com/ActivityWatch/aw-server-rust.git` | 一致 |
| aw-watcher-input | `https://github.com/ActivityWatch/aw-watcher-input.git` | 一致 |
| aw-tauri | `https://github.com/ActivityWatch/aw-tauri.git` | 官方是 `https://github.com/activitywatch/aw-tauri`（小写、无 .git） |
| awatcher | `https://github.com/2e3s/awatcher` | 一致 |
| aw-notify | `https://github.com/ActivityWatch/aw-notify-rs.git` | 一致 |

---

## 嵌套子模块（各仓库内的 `.gitmodules`）

### aw-server-rust

| 子模块 | 你本地 | 官方 aw-server-rust |
|--------|--------|---------------------|
| aw-webui | `https://github.com/ActivityWatch/aw-webui.git` | 一致 |

### aw-server-rust/aw-webui

| 子模块 | 你本地 | 官方 aw-webui |
|--------|--------|----------------|
| media | `https://github.com/ActivityWatch/media.git` | 一致 |

### aw-server

| 子模块 | 你本地 | 官方 aw-server |
|--------|--------|----------------|
| aw-webui | `https://github.com/ActivityWatch/aw-webui.git` | 一致 |

### aw-server/aw-webui

| 子模块 | 你本地 | 官方 aw-webui |
|--------|--------|----------------|
| media | `https://github.com/ActivityWatch/media.git` | 一致 |

### aw-qt

| 子模块 | 你本地 | 官方 aw-qt |
|--------|--------|-------------|
| media | `https://github.com/ActivityWatch/media.git` | 一致 |

### aw-tauri

| 子模块 | 你本地 | 官方 aw-tauri |
|--------|--------|----------------|
| aw-webui | `https://github.com/ActivityWatch/aw-webui.git` | 一致 |

### aw-tauri/aw-webui

| 子模块 | 你本地 | 官方 aw-webui |
|--------|--------|----------------|
| media | `https://github.com/ActivityWatch/media.git` | 一致 |

---

## 实际 git remote（各子模块里 `git remote -v` 的 origin）

**只列 origin（clone/update 用的），你本地有些还有 chenbaiyujason 是额外加的 fork，不影响「指向」是否和官方一致。**

| 路径 | origin 当前指向 |
|------|-----------------|
| aw-client | `https://github.com/ActivityWatch/aw-client.git` |
| aw-core | `https://github.com/ActivityWatch/aw-core.git` |
| aw-notify | `https://github.com/ActivityWatch/aw-notify-rs.git` |
| aw-qt | `https://github.com/ActivityWatch/aw-qt.git` |
| aw-qt/media | `https://github.com/ActivityWatch/media.git` |
| aw-server | `https://github.com/ActivityWatch/aw-server.git` |
| aw-server/aw-webui | `https://github.com/ActivityWatch/aw-webui.git` |
| aw-server/aw-webui/media | `https://github.com/ActivityWatch/media.git` |
| aw-server-rust | `https://github.com/ActivityWatch/aw-server-rust.git` |
| aw-server-rust/aw-webui | `https://github.com/ActivityWatch/aw-webui.git` |
| aw-server-rust/aw-webui/media | `https://github.com/ActivityWatch/media.git` |
| aw-tauri | `https://github.com/ActivityWatch/aw-tauri.git` |
| aw-tauri/aw-webui | `https://github.com/ActivityWatch/aw-webui.git` |
| aw-tauri/aw-webui/media | `https://github.com/ActivityWatch/media.git` |
| aw-watcher-afk | `https://github.com/ActivityWatch/aw-watcher-afk.git` |
| aw-watcher-input | `https://github.com/ActivityWatch/aw-watcher-input.git` |
| aw-watcher-window | `https://github.com/ActivityWatch/aw-watcher-window.git` |
| awatcher | `https://github.com/2e3s/awatcher` |

---

## 和「最新」的差异小结

1. **根仓库 aw-tauri**  
   你本地：`ActivityWatch/aw-tauri.git`  
   官方：`activitywatch/aw-tauri`（小写、无 `.git`）。  
   GitHub 上两个 URL 都会跳到同一仓库，功能上没区别，只是写法不同。

2. **其余所有子模块（含 aw-server-rust 里的 webui）**  
   `.gitmodules` 和实际 `origin` 都与官方一致，没有不同。

3. **你本地多出来的 remote**  
   aw-qt、aw-server、aw-server/aw-webui、aw-server-rust、aw-server-rust/aw-webui、aw-tauri 里还有 `chenbaiyujason` 的 remote，是本地额外加的，不影响当前「指向」是否和官方一致；要跟官方完全一致，只是把这些 fork 的 remote 删掉即可。

如果你有某个具体路径觉得和「你心目中的最新」还不一样，告诉我路径和期望的 URL，我可以按那个帮你改并给出命令。
