# 背景
- 在手机中下载了300g音声，音声的字幕文件是srt格式，但手机里的播放器只支持lrc格式，找了许久都没有一个满意的播放器，无奈只能转换格式，手机app的转换软件只能一个一个转，并且限制额度，音声数量太多也不好转移到电脑中处理，于是只能通过ai自己写一个工具来解决问题。 
# 痛点
1. 大量srt文件在手机不同的文件夹下
2. srt文件在手机中，不方便移动到电脑中处理
# 需求
1. 将各自文件夹下的srt转换为lrc，并且lrc文件要在srt文件同一目录中
2. 大批量转换
# 环境
1. python
	- 编辑器：Vscode，Pycharm...
2. adb --**Android Debug Bridge**，即 **Android 调试桥**
	- 下载链接：[SDK Platform Tools release notes  |  Android Studio  |  Android Developers](https://developer.android.google.cn/tools/releases/platform-tools) 
	- 加入到系统变量path中
3. 手机连接电脑，通过开发者选项，打开USB调试
