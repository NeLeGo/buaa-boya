# buaa-boya: BUAA 博雅选课自动化脚本

## INSTRUCTIONS 使用说明

### 1. 安装依赖

```shell
pip install selenium
```

### 2. 下载浏览器驱动

根据浏览器版本下载驱动，注意驱动版本号需与浏览器版本号相匹配。支持的浏览器及驱动下载地址如下

- Chrome: https://chromedriver.chromium.org/downloads
- Firefox: https://github.com/mozilla/geckodriver/releases
- Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

### 3. 配置参数

使用记事本修改 `config.json` 文件中的参数，具体参数说明如下

- "driver": 浏览器驱动相关配置
  - "type": 浏览器类型，支持 Chrome、Firefox、Edge
  - "path": 浏览器驱动路径，支持绝对路径和相对路径
- "wait-time": 每次刷新课程的等待时间，单位秒
- "login": 登录相关配置
  - "id": 学工号
  - "password": 统一认证密码
- "courses": 待选课程名称

以下是一个示例配置

```js
{
  "driver": {
    "type": "edge",
    "path": "./msedgedriver.exe"
  },
  "wait-time": 10,
  "account": {
    "id": "23011001",
    "password": "123456"
  },
  "courses": ["课程一", "课程二"]
}
```

### 4. 运行脚本

```shell
python boya.py
```

注：配合 Windows 计划任务等方式可以实现定时运行脚本，参考[这篇 CSDN 文章](https://blog.csdn.net/deefin/article/details/100893169)。
