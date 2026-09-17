# sales-push-webhook

销售详单的只读取数基础模块与项目交接资料。已验证：在获得授权、处于公司内网或 VPN 的环境中，可以不启动 EmsClient，使用 Python 连接 Ems 服务并获取销售详单。

本仓库仅保存协议验证工具和实现说明；不包含任何密码、Token、PCAP 抓包、原始二进制响应、销售明细或图片文件。

## 快速开始

1. 创建私密配置：

   ```powershell
   Copy-Item ems_config.example.json ems_config.json
   notepad ems_config.json
   ```

2. 在公司内网/VPN下验证认证（只读）：

   ```powershell
   python ems_readonly_probe.py --send
   ```

3. 用本机已授权抓包验证完整业务初始化与销售详单查询：

   ```powershell
   python ems_replay_readonly.py "D:\文档\桌面\ems_login_query.pcapng" --send
   ```

详细协议、字段和下一步计划见 [docs/EMS_READONLY_DATA_ACCESS.md](docs/EMS_READONLY_DATA_ACCESS.md)。新的 Codex/AI 上下文应先读 [AGENTS.md](AGENTS.md) 和该文档。

## 安全边界

- 仅实现、测试和运行读取请求；禁止写请求。
- `ems_config.json` 包含明文凭据，绝不能提交、上传或发到聊天中。
- 不提交 `*.pcap`、`*.pcapng`、`*.bin`、销售 CSV/JSON/XLSX 或图片缓存。
- 仅访问公司授权的账号、机构与数据范围。
