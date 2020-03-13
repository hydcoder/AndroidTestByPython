# encoding:utf-8
import csv
import os
import time

# 控制类
class Controller(object):
    def __init__(self, count):
        # 定义测试的次数
        self.counter = count
        # 定义收集数据的数组
        self.all_data = [("timestamp", "power")]

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

    # 获取当前的时间戳
    @staticmethod
    def get_current_time():
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return current_time

    # 数据的存储
    def save_data_to_csv(self):
        csv_file = file('power.csv', 'wb')
        writer = csv.writer(csv_file)
        writer.writerows(self.all_data)
        csv_file.close()


if __name__ == '__main__':
    controller = Controller(5)
    controller.run()
    controller.save_data_to_csv()
