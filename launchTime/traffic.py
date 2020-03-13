# encoding:utf-8
import csv
import os
import time
import string


# 控制类
class Controller(object):
    def __init__(self, count):
        # 定义测试的次数
        self.counter = count
        # 定义收集数据的数组
        self.all_data = [("timestamp", "traffic")]

    # 单次测试过程
    def test_process(self):
        # 执行获取进程ID的指令 window 下用findstr，Mac下用grep
        # receive, transmit, receive2, transmit2 = "0"
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

    # 多次执行测试过程
    def run(self):
        while self.counter > 0:
            self.test_process()
            self.counter = self.counter - 1
            # 每5秒采集一次数据
            time.sleep(5)

    # 获取当前的时间戳
    @staticmethod
    def get_current_time():
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return current_time

    # 数据的存储
    def save_data_to_csv(self):
        csv_file = file('traffic.csv', 'wb')
        writer = csv.writer(csv_file)
        writer.writerows(self.all_data)
        csv_file.close()


if __name__ == '__main__':
    controller = Controller(5)
    controller.run()
    controller.save_data_to_csv()
