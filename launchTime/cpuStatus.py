# encoding:utf-8
import csv
import os
import time


# 控制类
class Controller(object):
    def __init__(self, count):
        self.result = ""
        self.counter = count
        self.all_data = [("timestamp", "cpuStatus")]

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

    # 多次执行测试过程
    def run(self):
        while self.counter > 0:
            self.test_process()
            self.counter = self.counter - 1
            time.sleep(3)

    # 获取当前的时间戳
    def get_current_time(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return current_time

    # 数据的存储
    def save_data_to_csv(self):
        csv_file = file('cpustatus.csv', 'wb')
        writer = csv.writer(csv_file)
        writer.writerows(self.all_data)
        csv_file.close()


if __name__ == '__main__':
    controller = Controller(10)
    controller.run()
    controller.save_data_to_csv()
