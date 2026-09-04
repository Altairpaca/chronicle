# Chronicle

Chronicle 是一个个人时间账本：按柳比歇夫的方式记录实际时间，并用 B/S 模型标记该时段主要消耗的生物能量或社会能量。它是一套不依赖第三方云服务的响应式 PWA，手机和桌面浏览器访问同一地址。

## 本地运行

```bash
cd chronicle
python3 server.py
```

浏览器打开 `http://127.0.0.1:8787`。API 健康检查在 `GET /healthz`，数据位于 `data/chronicle.sqlite3`。

运行测试：

```bash
python -m unittest discover -s tests -v
python -m compileall -q chronicle_app.py ledger.py server.py tests
```

## Tailnet 常驻部署

该服务不会默认监听 `0.0.0.0`。`deploy/run-tailnet.sh` 在每次启动时读取本机 Tailscale IPv4，服务仅绑定该地址和端口 8787。

```bash
sudo useradd --system --home /opt/chronicle --shell /usr/sbin/nologin chronicle
sudo install -d -o chronicle -g chronicle /opt/chronicle/data
sudo rsync -a --delete --exclude data ./ /opt/chronicle/
sudo chown -R chronicle:chronicle /opt/chronicle
sudo install -m 0644 deploy/chronicle.service /etc/systemd/system/chronicle.service
sudo systemctl daemon-reload
sudo systemctl enable --now chronicle.service
```

确认 Tailnet 地址后，从 Tailnet 内设备访问 `http://<tailscale-ip>:8787`。若 Tailscale IPv4 变化，重启服务即可重新绑定：`sudo systemctl restart chronicle`。

### 安全边界

Chronicle 当前没有应用层账户或鉴权。Tailnet 部署必须把 Tailscale ACL/Grants 配置为仅允许你明确授权的设备或用户访问 8787 端口；不要把该端口映射到公网，也不要使用宽泛的 Tailnet 访问规则来代替应用鉴权。服务端对 JSON 请求体设有大小上限，并发送基础浏览器安全响应头，但这些措施不能替代身份认证。

## 备份

停止服务后复制 `data/chronicle.sqlite3`；这是唯一的业务数据文件。数据库包含完整个人时间记录，应按私密数据处理，不应提交到 Git 或上传到公共 artifact。
