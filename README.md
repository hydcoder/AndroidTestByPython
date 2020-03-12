# AndroidTestByPython
 Android APP使用Python进行性能测试

### APP启动时间

#### 冷启动

- 启动APP命令

```shell
adb shell am start -W -n package/activity
```

- 停止App命令

```shell
adb shell am force-stop package
```

- 获取某个APP的packageName和ActivityName的命令

  ```shell
  adb logcat | grep START
  ```

  然后打开你想获取packageName和ActivityName的应用即可。

#### 热启动

- 启动APP命令和冷启动一样

- 停止App命令

  ```shell
  // 模拟点击back键
  adb shell input keyevent 3
  ```

  

#### 自动化脚本的实现

两种方案：

- 获取命令执行时间，作为启动时间参考值

  ```python
  class App(object):
      def __init__(self):
          self.content = ""
          self.startTime = 0
  
      # 启动APP
      def launch_app(self):
          cmd = 'adb shell am start -W -n org.chromium.webview_shell/.WebViewBrowserActivity'  # type: str
          self.content = os.popen(cmd)
  
      # 停止app
      @staticmethod
      def stop_app():
          # 冷启动停止的命令
          # cmd = 'adb shell am force-stop org.chromium.webview_shell'
          # 热启动停止的命令
          cmd = 'adb shell input keyevent 3'
          os.popen(cmd)
  
      # 获取启动时间
      def get_launched_time(self):
          for line in self.content.readlines():
              if "ThisTime" in line:
                  self.startTime = line.split(":")[1]
                  break
          return self.startTime
      
  # 单次测试过程
      def test_process(self):   
          self.app.launch_app()
          time.sleep(5)
          elapsed_time = self.app.get_launched_time()
          self.app.stop_app()
          time.sleep(3)
          current_time = self.get_current_time()
          self.all_data.append((current_time, elapsed_time))
  
      # 多次执行测试过程
      def run(self):
          while self.counter > 0:
              self.test_process()
              self.counter = self.counter - 1
  ```

  

- 在命令前后加上时间戳，以差值作为参考值

  ```python
   # 单次测试过程
      def test_process(self):
          time_before_launch = int(time.time())
          self.app.launch_app()
          time_after_launch = int(time.time())
          time.sleep(5)
          # elapsed_time = self.app.get_launched_time()
          elapsed_time = time_after_launch - time_before_launch
          self.app.stop_app()
          time.sleep(3)
          current_time = self.get_current_time()
          self.all_data.append((current_time, str(elapsed_time)))
  
      # 多次执行测试过程
      def run(self):
          while self.counter > 0:
              self.test_process()
              self.counter = self.counter - 1
  ```

> 可以多次计算启动时间值，并保存到本地csv文件，进行统计分析，求平均值等，第一次获得的值最好弃用。

### APP的CPU占用情况

#### 获取数据

##### 命令

```shell
# windows系统的cmd中，用findstr来过滤字符，不能用grep。
adb shell dumpsys cpuinfo | grep packagename
```

##### 脚本的代码实现

```python
# 单次测试过程
    def test_process(self):
        # window 下用findstr，Mac下用grep
        cmd = "adb shell dumpsys cpuinfo | findstr org.chromium.webview_shell"
        self.result = os.popen(cmd)
        cpu_value = 0
        for line in self.result.readlines():
            cpu_value = line.split("%")[0]

        current_time = self.get_current_time()
        self.all_data.append((current_time, cpu_value))
```





