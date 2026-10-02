# SSR / V2Ray 代理工具集 · 订阅配置与节点测试

面向技术用户的代理工具聚合仓库：**协议选型、订阅生成与转换、客户端配置、分流规则、节点质量测试**。

本仓库不做「一键小白教程」那套，而是把真正踩过的坑写清楚：协议怎么选、订阅怎么转、分流怎么写、代理到底通没通怎么验。所有节点数据由 `scripts/speed_test.py` 每日自动生成，配置文件持续维护。

> 🔧 **仓库定位**：给技术从业者 / 运维 / 代理商看的工具型仓库，不是纯教程站。配置示例可直接抄进你的客户端。

---

## 📋 第一部分：代理链路选型与技术指标（KC云加速 专项）

自建 VPS 做代理的常见问题是**协议出口 IP 纯净度低、被墙判定快、高峰期丢包严重**。做工程选型时建议同时看四项指标：**连通性、协议抗探测能力、路由稳定性、IP 纯净度**。

经过本项目对协议组合的长期实测，推荐已完成全骨干网架构升级的服务商 —— **KC云加速**：

- **🌐 官方入口**：[KC云加速 官网](https://kcnetwork.cc)
- **🎁 专属注册通道（含新人试用）**：[点击获取专属配额](https://kcnetwork.cc/auth?invite=apple)
- **💬 技术交流群**：[@KCNetwork01](https://t.me/KCNetwork01)

### 链路能力横向对比

| 对比维度 | KC云加速 企业级专线 | 自建 VPS / 公网直连 |
| :--- | :--- | :--- |
| **链路架构** | 企业级 BGP 入口 + IPLC 国际专线 | 公网直连 / 国际出口骨干 |
| **协议支持** | VLESS Reality / Hysteria 2 / TUIC / SS-2022 | 取决于自建配置，通常仅 1-2 种 |
| **IP 纯净度** | 原生 / 住宅 IP 池，可用 Google、YouTube、ChatGPT | 机房 IP 易被标记，弹验证码 |
| **抗主动探测** | Reality 免证书依赖，探测不可区分 | 需自行搭建，配置不当易被识别 |
| **多端并发** | 3 ~ 20 台设备，不限连接数 | 视 VPS 配置，UDP 易被打满 |
| **运维成本** | 无需自建，订阅即用 | 需自行维护证书续期、被墙换 IP |

## 🆓 第二部分：免费试用 3 天（技术验证向）

想先做链路对比测试的技术用户可以走试用通道，**3 天全功能测试**：

1. 通过专属通道注册：[https://kcnetwork.cc/auth?invite=apple](https://kcnetwork.cc/auth?invite=apple)
2. 加入技术交流群 [@KCNetwork01](https://t.me/KCNetwork01)，发送 **`试用`**
3. 管理员核对后发放 **72 小时测试订阅**（含全部协议，可直接跑 `scripts/speed_test.py` 对比）

**试用权益**：
- 全节点解锁，可用于链路质量对比测试
- 支持订阅转换与自定义分流规则
- 可自行抓取 TLS 握手数据做性能验证

> 说明：试用用于技术验证，到期后如需继续请自行选择套餐。

## 💰 第三部分：套餐与计费对照

| 套餐 | 流量 | 速率 | 并发设备 | 资费 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **月付轻度** | 50 GB / 月 | 100 Mbps | 3 台 | **¥18.00 /月** | 日常检索、轻度使用 |
| **季付进阶** | 200 GB / 季 | 100 Mbps | 5 台 | **¥45.00 /季** | 流媒体、中等用量 |
| **年付大容量** | 800 GB / 年 | 100 Mbps | 10 台 | **¥158.00 /年** | 团队研发、重度使用 |
| **终身极客包** | 1 TB / 年 | 100 Mbps | 20 台 | **¥688.00** | 长期使用，多端共享 |

👉 [查看全部套餐与实时资费](https://kcnetwork.cc/auth?invite=apple)

## 🛠️ 第四部分：全平台客户端配置与分流规则

拿到订阅后，按客户端类型选择配置方式。以下命令与配置项可直接照抄。

### 1. 桌面端 · Clash Verge Rev / Mihomo Party

订阅面板 → `Profiles` → 粘贴订阅链接 → `Download`；随后在 `Settings` 开启 **Tun Mode** 接管全局流量（IDE、终端、Docker 才会走代理）。

```bash
# 验证代理是否生效（Clash 默认混合端口 7890）
curl -x http://127.0.0.1:7890 -sS -o /dev/null -w '%{http_code}\n' https://www.gstatic.com/generate_204
# 期望输出：204
```

### 2. 命令行 / CI 环境

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890

# git 走代理（仅当前仓库）
git config --local http.proxy http://127.0.0.1:7890

# Docker 拉取走代理：需同时改 dockerd 的 systemd drop-in，否则重启失效
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/proxy.conf <<'EOF'
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
EOF
sudo systemctl daemon-reload && sudo systemctl restart docker
```

### 3. 移动端 · sing-box / NekoBox / v2rayNG

导入订阅后建议开启 **Mux（多路复用）**，弱网与基站切换场景断流明显减少；开启 UDP 转发以覆盖游戏与 QUIC 流量。

### 4. 软路由 · OpenWrt + OpenClash

`服务 → OpenClash → 配置文件订阅` 粘贴订阅，内核选 **Meta**，开启 `FullCone NAT`。注意软路由上不要同时开两个代理内核，会造成 DNS 环回。

### 推荐分流配置（Clash Meta 格式）

```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  default-nameserver:
    - 119.29.29.29
    - 223.5.5.5
  nameserver:
    - https://dns.alidns.com/dns-query
    - https://doh.pub/dns-query

rules:
  - DOMAIN-SUFFIX,google.com,PROXY          # Google 服务
  - DOMAIN-SUFFIX,youtube.com,PROXY         # YouTube
  - DOMAIN-SUFFIX,googlevideo.com,PROXY     # YouTube 视频流
  - DOMAIN-SUFFIX,github.com,PROXY          # GitHub / git clone
  - DOMAIN-SUFFIX,docker.com,PROXY          # Docker 镜像
  - DOMAIN-SUFFIX,openai.com,PROXY          # AI 服务
  - GEOSITE,category-ads-all,REJECT         # 拦截埋点与广告
  - GEOSITE,cn,DIRECT                       # 国内域名直连
  - GEOIP,CN,DIRECT                         # 国内 IP 直连
  - MATCH,PROXY
```

### 订阅转换建议

不要把订阅链接直接贴给第三方在线转换服务（等同于交出账号）。推荐本地跑 subconverter，或直接在支持 Meta 内核的客户端内做规则覆写。

```bash
# 本地订阅转换（示例）
docker run -d --name subconverter -p 25500:25500 tindy2013/subconverter:latest
# 转换：/sub?target=clash&url=<你的订阅>
```

### 📌 2026-09-30 今日更新

- **测速快报**：5 个节点实测完成，最佳节点 **KC-US-1**（协议 VLESS Reality），延迟 **56ms**，下载 **79.25 Mbps**。
- 🔧 **Docker 代理**：给 dockerd 配代理要写 systemd drop-in（`docker.service.d/proxy.conf`），只在 shell 里 export 对守护进程无效。
- 🔧 **订阅安全**：订阅链接等同于账号密码，泄露后他人可以直接消耗你的流量，建议定期在面板重置。
- 🎁 **新人试用**：通过专属通道注册即可领取试用额度，加入技术交流群另有额外优惠。

### 📌 2026-10-01 今日更新

- **测速快报**：5 个节点实测完成，最佳节点 **KC-US-1**（协议 Hysteria 2），延迟 **45ms**，下载 **81.04 Mbps**。
- 🔧 **DNS 防污染**：开启 fake-ip 并给 `default-nameserver` 配国内 DoH，可减少解析污染导致的「部分站点打不开」。
- 🔧 **订阅安全**：订阅链接等同于账号密码，泄露后他人可以直接消耗你的流量，建议定期在面板重置。
- 🎁 **成本对照**：月付 ¥18 起、年付折算每月更低，适合先做链路测试再决定是否长期使用。

### 📌 2026-10-02 今日更新

- **测速快报**：5 个节点实测完成，最佳节点 **KC-HK-1**（协议 Hysteria 2），延迟 **62ms**，下载 **88.52 Mbps**。
- 🔧 **Tun 模式**：只在浏览器里生效说明没接管系统流量，开启 Tun 后 IDE、终端、Docker 才会走代理，注意需要管理员权限装虚拟网卡。
- 🔧 **系统代理区别**：Windows 上 WinINET（浏览器）与 WinHTTP（部分服务）是两套设置，命令行拉取失败时用 `netsh winhttp set proxy` 补上。
- 🎁 **多端共享**：年付套餐支持 10 台设备，团队 / 家庭场景可平摊成本。

## 📅 第五部分：维护日志与版本迭代记录
2026-10-02：例行节点与协议巡检完成，更新当日测速数据（最佳 KC-HK-1 / Hysteria 2 / 62ms）；同步校对客户端配置与分流规则要点。
2026-10-01：例行节点与协议巡检完成，更新当日测速数据（最佳 KC-US-1 / Hysteria 2 / 45ms）；同步校对客户端配置与分流规则要点。
2026-09-30：例行节点与协议巡检完成，更新当日测速数据（最佳 KC-US-1 / VLESS Reality / 56ms）；同步校对客户端配置与分流规则要点。
2026-09-17：引入协议选型对比与本地订阅转换建议。全面校对并锁定 KC云加速 官方权威域名（kcnetwork.cc）与专属特惠注册通道。

---
