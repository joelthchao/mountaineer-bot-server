# mountaineer-bot-server
Mountaineer Bot is a Linebot to help you acquire and subscribe latest mountain weather during climbing.

This repository dedicates to establish a service to provide above requests for linebot.

Currently only support 100 peaks of Taiwan.

# Installation

1. Prepare Python3 environment
2. Install Python libraries
```bash
pip install -r requirements.txt
```
3. Install chromedriver: [link](https://chromedriver.chromium.org/)
4. Install `imgkit` dependencies: [link](https://pypi.org/project/imgkit/)

# Usage

```bash
export LINE_CHANNEL_SECRET=XXXXX
export LINE_CHANNEL_ACCESS_TOKEN=XXXXX
export SSL_CRT=XXXXX
export SSL_PRIVATE_KEY=XXXXX
python3 -m mtn_bot_server.api
```

# Line Bot

Add offical accounts by id: `@801tuftx`

1. 查詢天氣預報："南湖大山的天氣"
2. 訂閱天氣預報並於指定時間回報，格式：訂閱 YYYYMMDDhhmm{山名}天氣，例如："訂閱202006241300玉山天氣"


# TODO
- [X] Documentation
- [X] System robustness
- [X] Error feedback for user
- [ ] Less network consumption
