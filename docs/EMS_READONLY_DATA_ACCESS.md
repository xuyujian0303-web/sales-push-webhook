# Ems 只读数据访问交接

## 已验证的链路

在授权的公司内网环境中，以下链路已成功验证：

```text
userLogin (TCP 9999)
  -> 连接 TCP 9100
  -> 依次执行只读初始化请求
  -> querySaleDetailList
  -> 返回自定义 TLV/RDS 销售详单
```

认证服务为 `giada-erp.redstone.com.cn:9999`，业务服务为 `giada-erp.redstone.com.cn:9100`。内网 IP 曾解析到 `10.243.1.18`，但代码应使用配置中的域名，不能依赖该 IP 固定。

## 登录协议

- 方法：`userLogin`
- 密码摘要：`hashlib.md5(password.encode("utf-8")).hexdigest().upper()`
- 已验证完整登录响应为 2537 字节，并返回用户/公司可读文本。
- 不记录或上传用户账号、原密码、摘要、完整响应。

## 读取规则

协议为长度前缀二进制 TCP：前 4 个字节是 big-endian 帧体长度。每一帧必须读取到 `4 + length` 才能继续。实际网络中登录响应首段为 1200 字节，完整帧为 2537 字节，因此单次 `recv()` 不可靠。

`9100` 查询前按以下只读序列初始化，并逐个读取响应：

```text
getSaleDate
getServerTime
getAppSysDefin
getCommonOrgList
getCategoryList
getLineList
getMainCompList
getPayModeList
queryCompanyCardList
getSaleLblKindList
querySaleDetailList
getOrgAllCardTypeList
getServerTime
getSaleDate
```

直接向新业务连接发送 `querySaleDetailList` 会超时；完整初始化序列已验证返回成功。

## 销售详单

接口名：`querySaleDetailList`。一次已验证查询响应 50,541 字节，对应约 92 条明细。返回是自定义 TLV/RDS，尚未完成通用解析器；但可识别销售单号、日期、销售机构、产品编码、商品条码、价格、折扣、实际金额、销售件数与创建时间。

以 Ems 导出 Excel 为准的字段：

```text
销售单号、销售人员、销售日期、销售机构、业绩机构、销售类型、币种、顾客类型、顾客折扣类型、顾客折扣、卡类型、卡号、总金额、产品编码、款色码、ItemID、商品条码、类别、商品类型、特殊销售、商品状态、操作方式、价格、折扣、实际金额、实际折扣、销售件数、整单件数、创建时间、顾客来源、活动类型、助力素材
```

## 图片

已观察到图片 URL 格式：

```text
http://giada-erp.redstone.com.cn/giada/images/<产品编码>_01.jpg
```

需要内网/VPN访问。用“产品编码”与销售明细关联。

## 本机参考材料（禁止提交）

以下文件存在于先前工作机，只作为本地协议分析参考：

```text
D:\文档\桌面\ems_login_query.pcapng
D:\文档\桌面\images.pcapng
C:\Users\redstone\ems_sale_detail_response.bin
D:\文档\桌面\sales-0904.xlsx
```

它们可能包含客户、销售数据或会话信息；禁止上传到 GitHub。
