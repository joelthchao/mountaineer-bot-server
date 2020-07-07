# mountaineer-bot-server
Mountaineer Bot is a Linebot to help you acquire and subscribe latest mountain weather during climbing.

This repository dedicates to establish a service to provide above requests for linebot.

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

# TODO
- [ ] Documentation
- [ ] System robustness
- [ ] Error feedback for user
- [ ] Less network consumption
