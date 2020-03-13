# encoding:utf-8
import csv

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
