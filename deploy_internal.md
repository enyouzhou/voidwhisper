# VoidWhisper 内网部署指南

## 快速部署步骤

### 1. 克隆项目到内网服务器
```bash
git clone https://github.com/enyouzhou/voidwhisper.git
cd voidwhisper
```

### 2. 设置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，填入你的 API keys
nano .env
```

### 3. 创建虚拟环境并安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 给启动脚本添加执行权限
chmod +x scripts/start_backend.sh
```

### 4. 启动服务
```bash
# 使用启动脚本（推荐）- 会自动处理端口占用问题
./scripts/start_backend.sh

# 或者手动启动
# python -m backend.app
```

服务将在 `http://0.0.0.0:5001` 启动，内网其他机器可通过 `http://<服务器IP>:5001` 访问。

**注意**：`start_backend.sh` 脚本会自动 kill 占用 5001 端口的进程，无需手动管理。

## 生产环境部署（可选）

### 使用 systemd 服务
创建服务文件：
```bash
sudo nano /etc/systemd/system/voidwhisper.service
```

内容：
```ini
[Unit]
Description=VoidWhisper Flask App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/voidwhisper
Environment=PYTHONUNBUFFERED=1
ExecStart=/path/to/voidwhisper/scripts/start_backend.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable voidwhisper
sudo systemctl start voidwhisper
sudo systemctl status voidwhisper
```

### 防火墙配置
如果服务器有防火墙，需要开放端口：
```bash
# Ubuntu/Debian
sudo ufw allow 5001

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

## 访问应用

部署完成后，内网用户可以通过以下地址访问：
- `http://<服务器IP>:5001/`

例如：`http://192.168.1.100:5001/` 