# 项目交接给后续 Agent

## 首先阅读

1. `README.md`
2. `docs/EMS_READONLY_DATA_ACCESS.md`
3. `ems_readonly_probe.py`
4. `ems_replay_readonly.py`

## 已验证事实

- Ems 认证服务和业务服务均位于 `giada-erp.redstone.com.cn`；认证端口 `9999`，业务端口 `9100`。
- 登录方法名为 `userLogin`；密码字段为 `MD5(password UTF-8).hexdigest().upper()`。
- TCP 应用帧的前 4 字节是 big-endian 帧体长度。必须完整读完 `4 + length`，不能假定一次 `recv()` 返回完整响应。
- 直接调用 `querySaleDetailList` 会超时；先按抓包的只读初始化请求顺序调用才成功。
- 已在授权网络内验证 `querySaleDetailList` 返回 50,541 字节，约 92 行销售详单。
- 返回是自定义 TLV/RDS 结构；还未完成通用、可靠的二进制字段解码器。

## 当前任务建议

将 `ems_replay_readonly.py` 从依赖 PCAP 的验证脚本升级为代码构造的生产只读客户端：

1. 参数化日期、机构、分页和筛选条件。
2. 将初始化帧固定为明确的 builder 函数，而非从 PCAP 读取。
3. 完成 `querySaleDetailList` 返回数据的 TLV/RDS 解码。
4. 与 Ems 导出的 Excel 逐字段、逐销售单号比对。
5. 成功后再接入每 20 分钟的聚合和企业微信 webhook 逻辑。

## 禁止项

- 不要向 Git 写入真实 `ems_config.json`、密码、MD5 摘要、Token、PCAP、二进制响应或销售数据。
- 不要构造或发送新增、修改、删除类 Ems 请求。
- 不要假定端口/IP 在所有环境固定；优先使用配置中的域名和端口。
