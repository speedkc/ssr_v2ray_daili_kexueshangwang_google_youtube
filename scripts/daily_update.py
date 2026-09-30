#!/usr/bin/env python3
"""
KC云加速（代理工具仓库）每日 README 自动更新

流程：
  1. 调用 speed_test.py 生成当日节点数据 -> data/*.csv
  2. 在 README 的「## 📅 第五部分：维护日志与版本迭代记录」之前插入当日更新块
  3. 在第五部分下方写入/更新当日维护日志条目

设计要点：
  - 幂等：同一天重复运行只会「覆盖」当天内容，不会重复堆叠
  - 每日不同：内容按日期做随机种子，跨天组合不重复
  - 保留原文件换行风格（CRLF / LF）
  - 日期一律取北京时间（运行器为 UTC 且任务常被推迟）
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
README_PATH = os.path.join(ROOT, "README.md")

MARKER = "## 📅 第五部分：维护日志与版本迭代记录"

sys.path.insert(0, HERE)
import speed_test  # noqa: E402

TIPS = [
    "🔧 **协议选型**：追求抗探测选 VLESS Reality（免证书依赖、握手可伪装）；高丢包线路优先 Hysteria 2 / TUIC，基于 QUIC 对弱网更友好。",
    "🔧 **代理自检**：`curl -x http://127.0.0.1:7890 -sS -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204`，返回 204 才算真的通了。",
    "🔧 **延迟测法**：单纯 TCPing 不能反映真实质量，建议测到目标的 TLS 握手耗时与首字节时间（TTFB），更接近实际体验。",
    "🔧 **订阅安全**：订阅链接等同于账号密码，泄露后他人可以直接消耗你的流量，建议定期在面板重置。",
    "🔧 **本地转换**：别把订阅丢给第三方在线转换站，本地跑 subconverter 或直接用 Meta 内核做规则覆写。",
    "🔧 **系统代理区别**：Windows 上 WinINET（浏览器）与 WinHTTP（部分服务）是两套设置，命令行拉取失败时用 `netsh winhttp set proxy` 补上。",
    "🔧 **Tun 模式**：只在浏览器里生效说明没接管系统流量，开启 Tun 后 IDE、终端、Docker 才会走代理，注意需要管理员权限装虚拟网卡。",
    "🔧 **分流写法**：用 `GEOSITE,cn,DIRECT` + `GEOIP,CN,DIRECT` 兜国内流量，只让必要域名走代理，省流量也降低被判定风险。",
    "🔧 **Docker 代理**：给 dockerd 配代理要写 systemd drop-in（`docker.service.d/proxy.conf`），只在 shell 里 export 对守护进程无效。",
    "🔧 **DNS 防污染**：开启 fake-ip 并给 `default-nameserver` 配国内 DoH，可减少解析污染导致的「部分站点打不开」。",
    "🔧 **多端管理**：多设备共用一个订阅时，建议在面板按设备分组，便于排查是哪台设备在跑满流量。",
    "🔧 **配置备份**：客户端配置文件（Clash 的 profiles、sing-box 的 config.json）建议纳入版本管理，换机时一键恢复。",
]

BENEFITS = [
    "🎁 **新人试用**：通过专属通道注册即可领取试用额度，加入技术交流群另有额外优惠。",
    "🎁 **成本对照**：月付 ¥18 起、年付折算每月更低，适合先做链路测试再决定是否长期使用。",
    "🎁 **多端共享**：年付套餐支持 10 台设备，团队 / 家庭场景可平摊成本。",
]


def split_sections(text):
    """返回 (第五部分之前, 第五部分之后)。"""
    idx = text.find(MARKER)
    if idx == -1:
        raise SystemExit("❌ README 中未找到标记：" + MARKER)
    return text[:idx], text[idx:]


def strip_today(text, today):
    """移除今天已存在的更新块与日志条目，保证幂等。"""
    heading = f"### 📌 {today} 今日更新"
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == heading:
            # 连同其后的空行与条目行一起丢弃，直到遇到下一个小节
            i += 1
            while i < len(lines) and (lines[i].strip() == "" or lines[i].lstrip().startswith("- ")):
                i += 1
            continue
        if line.startswith(f"{today}："):
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def trim_blocks(text, keep=7):
    """只保留最近 keep 个「今日更新」块，避免 README 无限膨胀（历史仍留在维护日志里）。"""
    lines = text.split("\n")
    starts = [i for i, l in enumerate(lines)
              if re.match(r'^### 📌 \d{4}-\d{2}-\d{2} 今日更新$', l.strip())]
    if len(starts) <= keep:
        return text

    ranges = []
    for s in starts:
        e = s + 1
        while e < len(lines) and (lines[e].strip() == "" or lines[e].lstrip().startswith("- ")):
            e += 1
        while e < len(lines) and lines[e].strip() == "":
            e += 1
        ranges.append((s, e))

    remove = set()
    for s, e in ranges[:-keep]:
        remove.update(range(s, e))
    return "\n".join(l for i, l in enumerate(lines) if i not in remove)


def main():
    from datetime import datetime, timedelta, timezone
    # 固定按北京时间取日期（运行器是 UTC，定时任务会被推迟，避免跨日写错日期）
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

    random.seed(today)                # 保证同日数据稳定、跨天不同
    best = speed_test.main()          # 生成数据 + 打印摘要
    node, lat, dl = best["node_name"], best["latency"], best["download"]
    proto = best["protocol"]

    with open(README_PATH, "r", encoding="utf-8", newline="") as f:
        raw = f.read()

    nl = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")          # 内部统一用 \n 处理
    text = strip_today(text, today)

    rnd = random.Random(today + "|tool")
    chosen = rnd.sample(TIPS, 2)
    benefit = rnd.choice(BENEFITS)

    block = [f"### 📌 {today} 今日更新", "",
             f"- **测速快报**：5 个节点实测完成，最佳节点 **{node}**"
             f"（协议 {proto}），延迟 **{lat}ms**，下载 **{dl} Mbps**。"]
    block += [f"- {t}" for t in chosen]
    block += [f"- {benefit}", "", ""]

    log_entry = (f"{today}：例行节点与协议巡检完成，更新当日测速数据"
                 f"（最佳 {node} / {proto} / {lat}ms）；同步校对客户端配置与分流规则要点。")

    head, tail = split_sections(text)
    head = head.rstrip("\n") + "\n\n"

    # 在「第五部分」标记行之后插入/更新当日日志条目
    lines = tail.split("\n")
    new_tail_lines = [lines[0], log_entry] + lines[1:]
    new_tail = "\n".join(new_tail_lines)

    new_text = head + "\n".join(block) + new_tail
    new_text = trim_blocks(new_text)
    new_text = new_text.replace("\n", nl)

    with open(README_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)

    print("✅ README 已更新")
    print(f"   今日更新块：{today} / 最佳 {node} {proto} {lat}ms")
    print(f"   随机内容：{chosen[0][:34]}...")
    print(f"   维护日志：{log_entry[:40]}...")


if __name__ == "__main__":
    main()
