# encoding:utf-8
import csv
import os
import time

# APP类
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


# 控制类
class Controller(object):
    def __init__(self, count):
        self.app = App()
        self.counter = count
        self.all_data = [("timestamp", "elapsedTime")]

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

    # 获取当前的时间戳
    @staticmethod
    def get_current_time():
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return current_time

    # 数据的存储
    def save_data_to_csv(self):
        # 冷启动生成的文件
        # csv_file = file('startTime.csv', 'wb')
        # 热启动生成的文件
        csv_file = file('startTime2.csv', 'wb')
        writer = csv.writer(csv_file)
        writer.writerows(self.all_data)
        csv_file.close()


if __name__ == '__main__':
    controller = Controller(10)
    controller.run()
    controller.save_data_to_csv()
