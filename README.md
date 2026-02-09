# NovelDigest

每日自动抓取 [jjwxc.net](https://www.jjwxc.net)（晋江文学城）和 [gongzicp.com](https://www.gongzicp.com)（长佩文学）的最新更新/热门排序小说，通过大模型（Gemini）筛选出符合你个人偏好的作品，并将结果发送到你的邮箱。项目通过 GitHub Actions 实现全自动化。


## 配置

### config.env

复制 `config.example.env` 为 `config.env`（本地运行时使用）：

```env
GEMINI_API_KEY="你的 Gemini API Key"
QQ_EMAIL="你的 QQ 邮箱地址"
QQ_PASS="QQ 邮箱授权码（非登录密码）"
```

- `GEMINI_API_KEY` — Gemini API 密钥，用于大模型筛选（有免费额度）
- `QQ_EMAIL` — 接收邮件的 QQ 邮箱
- `QQ_PASS` — QQ 邮箱 SMTP 授权码，需在邮箱设置中开启 SMTP 后获取

> GitHub Actions 运行时，在 **Settings → Secrets → Actions** 中配置以上三项。

### novel.json

复制 `novel.example.json` 为 `novel.json`（本地运行时使用）。每个 key 为一个分类：

```json
{
    "gb": {
        "jj": "https://www.jjwxc.net/bookbase.php?yc1=1&xx=1&sortType=1",
        "jj_page": 3,
        "cp": "https://www.gongzicp.com/home/indexType?a=74&f=4&o=0",
        "cp_page": 10,
        "prompt": "筛选出所有gb小说，将标题、作者、简介提取出来，每行为一条记录，格式为{title:'', author:'', intro:''}，不要包含其他内容。"
    }
}
```

- **url** — 在网站调整排序/标签后复制网址即可
- **page** — 免费用户 token 有限，不建议过多
- **prompt** — 可自由修改筛选条件，但输出格式必须为每行一条：`{title:'', author:'', intro:''}`，不符合格式的行会被丢弃

> 不想暴露此文件可将内容作为 `NOVEL_JSON` secret 配置。

## 单独运行

| 文件 | 说明 |
|------|------|
| `jjwxc_scraper.py` | 抓取晋江小说列表（≥ 2 万字），保存到 `{分类}/novels_jj.json` |
| `cp_scraper.py` | 抓取长佩小说列表，保存到 `{分类}/novels_cp.json` |
| `ask_model.py` | 通过 Gemini 按 prompt 筛选，输出 `{分类}/selected_*.json` |
| `send_email.py` | 汇总筛选结果发送邮件，支持 `--dry-run` 仅打印 |

## 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium  # cp_scraper 需要
```

## 致谢

- [jjwxc-scraper](https://github.com/dev-chenxing/jjwxc-scraper) by [dev-chenxing](https://github.com/dev-chenxing) — 晋江爬虫原始实现，许可证见 [third_party_license/LICENSE](third_party_license/LICENSE)