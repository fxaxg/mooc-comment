# 英华课堂刷课程评论
## 介绍
英华课堂刷课程评论，使用Python3编写。
如果需要已打包的安装包：[下载exe](https://github.com/fxaxg/mooc-comment/releases/tag/exe)
## 安装
### 1.下载源码
```bash
git clone git@github.com:fxaxg/mooc-comment.git
cd mooc-comment
```
### 2.安装依赖库
```bash
pip install Pillow requests beautifulsoup4
```
### 3.修改英华学堂网站地址
打开目录下<kbd>config.json</kbd>文件改成自己学校的即可
```json
{
    "host": "你学校的英华慕课网址，最后记得加斜杠/"
}
```
## 运行
从main.py运行即可