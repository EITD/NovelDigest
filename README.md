# NovelDigest

每日自动抓取 [jjwxc.net](https://www.jjwxc.net)（晋江文学城）和 [gongzicp.com](https://www.gongzicp.com)（长佩文学）的最新更新小说，通过大模型（Gemini）筛选出符合你个人偏好的作品，并将结果发送到你的邮箱。项目通过 GitHub Actions 实现全自动化.


## 配置

### config.env

复制 `config.example.env` 为 `config.env`（本地运行时使用）：

```env
GEMINI_API_KEY="你的 Gemini API Key"
QQ_EMAIL="你的 QQ 邮箱地址"
QQ_PASS="QQ 邮箱授权码（非登录密码）"
```

- `GEMINI_API_KEY`：Google Gemini API 密钥，用于调用大模型进行小说筛选（目前为数不多具有免费用户额度的模型）
- `QQ_EMAIL`：接收推送邮件的 QQ 邮箱
- `QQ_PASS`：QQ 邮箱的 SMTP 授权码，需要在 QQ 邮箱设置中开启 SMTP 服务后获取

> 如果使用 GitHub Actions 运行，建议在仓库的 **Settings → Secrets and variables → Actions** 中配置 `GEMINI_API_KEY`、`QQ_EMAIL`、`QQ_PASS` 。

### novel.json

复制 `novel.example.json` 为 `novel.json`（本地运行时使用）。每个顶层 key 代表一个**分类**（如 `"gb"`），value 包含该分类的抓取和筛选配置：

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

| 字段 | 说明 |
|------|------|
| `jj` | 晋江文学城的搜索列表页 URL |
| `jj_page` | 晋江抓取的页数 |
| `cp` | 长佩文学的分类列表页 URL |
| `cp_page` | 长佩抓取的页数 |
| `prompt` | 发送给大模型的筛选指令 |

**关于 page**：如果是大模型免费用户，由于token有限，不建议抓取过多页。

**关于 prompt**：prompt 中需要明确指定输出格式。程序会按行解析模型返回的内容，每行必须严格匹配以下格式：

```
{title:'小说标题', author:'作者名', intro:'简介内容'}
```

不符合格式的行会被丢弃并报错。你可以自由修改 prompt 中的筛选条件（如类型、cp属性要求等），但务必保留上述输出格式要求。

> 如果不想暴露本文件，可将 `novel.json` 的完整内容作为 `NOVEL_JSON` secret 配置。

## 单独运行

如果只想使用部分功能，可以单独运行各个脚本：

| 文件 | 功能 | 说明 |
|------|------|------|
| `jjwxc_scraper.py` | 晋江小说抓取 | 爬取晋江文学城小说列表，筛选字数 ≥ 2 万的作品，保存元数据到 `{分类}/novels_jj.json` |
| `cp_scraper.py` | 长佩小说抓取 | 爬取长佩文学小说列表，保存到 `{分类}/novels_cp.json` |
| `ask_model.py` | 大模型筛选 | 读取抓取结果，通过 Gemini 按 prompt 筛选，输出 `{分类}/selected_novels_{网站}.json` |
| `send_email.py` | 邮件发送 | 汇总所有 `selected_novels_{网站}.json`，通过 QQ 邮箱 SMTP 发送。支持 `--dry-run` 参数仅打印不发送 |


## 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium  # cp_scraper 需要
```

## 致谢

- [jjwxc-scraper](https://github.com/dev-chenxing/jjwxc-scraper) by [dev-chenxing](https://github.com/dev-chenxing) — 晋江爬虫的原始实现，本项目在此基础上进行了修改。许可证见 [third_party_license/LICENSE](third_party_license/LICENSE)。
