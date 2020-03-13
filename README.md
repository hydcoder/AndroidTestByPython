# AndroidTestByPython

 Android APP使用Python进行性能测试以及测试框架

## APP性能测试

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
  # 模拟点击back键
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



### 流量

##### 命令

- 获取进程ID指令

  ```shell
  # windows下用findstr代替grep，否则拿不到结果
  adb shell ps | grep packagename
  ```

- 获取进程ID的流量指令

  ```shell
  # pid就是上面指令获取的进程ID
  adb shell cat /proc/pid/net/dev
  ```

##### 脚本实现

```python
# 单次测试过程
    def test_process(self):
        # 执行获取进程ID的指令 window 下用findstr，Mac下用grep
        cmd = "adb shell ps | findstr org.chromium.webview_shell"
        result = os.popen(cmd)
        # 获取进程ID
        pid = result.readlines()[0].split(" ")[5]

        # 获取进程ID使用的流量
        traffic = os.popen("adb shell cat /proc/" + pid + "/net/dev")
        for line in traffic:
            # 第一个网卡的数据
            if "eth0" in line:
                # 将所有空行换成#
                line = "#".join(line.split())
                # 然后按#号进行拆分，获取到收到和发出的流量值
                receive = line.split("#")[1]
                transmit = line.split("#")[9]
            # 第二个网卡的数据
            elif "eth1" in line:
                line2 = "#".join(line.split())
                # 然后按#号进行拆分，获取到收到和发出的流量值
                receive2 = line2.split("#")[1]
                transmit2 = line2.split("#")[9]

        # 计算所有流量之和
        all_traffic = string.atoi(receive) + string.atoi(transmit) + string.atoi(receive2) + string.atoi(transmit2)
        # 按KB计算流量值
        all_traffic = all_traffic / 1024
        # 获取当前时间
        current_time = self.get_current_time()
        # 将获取到的数据存到数组中
        self.all_data.append((current_time, all_traffic))
```

运行后的结果：

```
timestamp,traffic
2020-03-13 11:35:36,136535
2020-03-13 11:35:41,136791
2020-03-13 11:35:47,166458
2020-03-13 11:35:52,264812
2020-03-13 11:35:57,380940
```

##### 数据分析

用最后一条流量值减去第一条流量值，得到本次测试运行时消耗掉的流量，然后和以往版本以及竞品进行对比，然后发现流量消耗的问题。

### 电量

##### 获取电量

```shell
adb shell dumpsys battery
```

但是手机连接USB之后，会进入充电状态，测试电量需要在非充电的情况下，所以可以使用下面的命令切换充电状态

```shell
# 切换到非充电状态,status = 2 代表充电，非2就是非充电
adb shell dumpsys battery set status 1
```

##### 脚本实现

```python
# 单次测试过程
    def test_process(self):
        cmd = "adb shell dumpsys battery"
        result = os.popen(cmd)

        for line in result:
            if "level" in line:
                power = line.split(":")[1]

        # 获取当前时间
        current_time = self.get_current_time()
        # 将获取到的数据存到数组中
        self.all_data.append((current_time, power))

    # 多次执行测试过程
    def run(self):
        cmd = "adb shell dumpsys battery set status 1"
        os.popen(cmd)
        while self.counter > 0:
            self.test_process()
            self.counter = self.counter - 1
            # 每5秒采集一次数据, 真实测试场景建议在0.5-1小时
            time.sleep(5)
```

### 内存

##### 获取内存

```shell
adb shell top
# -d 刷新频率， 1 代表多久刷新一次，单位秒
adb shell top -d 1
# 输出到指定文件，测试完终止命令就可以分析指定文件
adb shell top -d 1 > meminfo
# 筛选指定包名,进行分析, windows上可以用type代替cat, findstr代替grep
cat meminfo | grep packagename
```

> VSS - Virtual Set Size 虚拟消耗内存
>
> RSS - Resident Set Size 实际使用物理内存

##### 脚本实现

脚本负责对命令行中测试后生成的meminfo文件进行分析，然后生成分析数据到csv文件，然后可以利用该csv文件进行图表绘制，内存数据获取时，建议测试时间长一点，方便分析使用过程中内存数据是否稳定，vss和rss分别分析。

```python
# 控制类
class Controller(object):
    def __init__(self):
        # 定义收集数据的数组
        self.all_data = [("id", "vss", "rss")]

    # 分析数据
    def analyze_data(self):
        content = self.read_file()
        i = 0
        for line in content:
            if "org.chromium.webview_shell" in line:
                print line
                line = "#".join(line.split())
                # 角标7和8不是固定的，要看你生成的meminfo文件里vss和rss出现的位置来确定
                vss = line.split("#")[7].strip("K")
                rss = line.split("#")[8].strip("K")

                # 将获取到的数据存到数组中
                self.all_data.append((i, vss, rss))
                i = i + 1

    # 读取数据文件
    @staticmethod
    def read_file():
        mem_info = file("meminfo", "r")
        content = mem_info.readlines()
        mem_info.close()
        return content

    # 数据的存储
    def save_data_to_csv(self):
        csv_file = file('meminfo.csv', 'wb')
        writer = csv.writer(csv_file)
        writer.writerows(self.all_data)
        csv_file.close()


if __name__ == '__main__':
    controller = Controller()
    controller.analyze_data()
    controller.save_data_to_csv()
```

### FPS&过度渲染

##### FPS

frames per second - 每秒的帧数

> Android中每一帧的绘制时间大于16秒，则可能会产生卡顿的现象，可以借助设置-开发者选项-GPU呈现模式分析，选择在屏幕上呈现为条形图，屏幕中横着的绿线就是16ms的基准线，高于绿线的条形图就是发生卡顿的帧

##### 过度渲染

描述的是屏幕上的某个像素在同一帧的时间内被绘制了多次

> 可以借助设置-开发者选项-调试GPU过度绘制-选择显示过度绘制区域，从最优到最差：蓝，绿，淡红，红。