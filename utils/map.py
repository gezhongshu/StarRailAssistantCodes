import time

from .calculated import *
from .config import get_file, read_json_file, modify_json_file, read_maps, insert_key, CONFIG_FILE_NAME, _
from .log import log, fight_log
from .requests import webhook_and_log

class Map:
    def __init__(self,title = _("崩坏：星穹铁道")):
        """
        参数: 
            :param platform: 运行设备
        """
        if read_json_file(CONFIG_FILE_NAME).get("language") != "EN":
            self.calculated = calculated(title)
        else:
            self.calculated = calculated(title, det_model_name="en_PP-OCRv3_det", rec_model_name="en_number_mobile_v2.0")
        self.mouse = self.calculated.mouse
        self.keyboard = self.calculated.keyboard
        self.data = read_json_file(CONFIG_FILE_NAME)
        self.open_map = self.data.get("open_map", "m")
        self.DEBUG = self.data.get("debug", False)
        self.map_list, self.map_list_map = read_maps()
        self.start = True

        if not os.path.exists("logs/image/"):
            os.makedirs("logs/image/")

    def map_init(self):
        # 进行地图初始化，把地图缩小,需要缩小5次
        target = cv.imread(f'./temp/pc/contraction.jpg')
        while True:
            result = self.calculated.scan_screenshot(target)
            if result['max_val'] > 0.98:
                target = cv.imread(f'./temp/pc/map_shrink.png')
                shrink_result = self.calculated.scan_screenshot(target,(20,89,40,93))
                if shrink_result['max_val'] < 0.98:
                    #points = self.calculated.calculated(result, target.shape)
                    points = result["max_loc"]
                    log.debug(points)
                    for i in range(6):
                        self.calculated.Click(points)
                break
            time.sleep(0.1)

    def start_map(self, map, map_name):
        map_data = read_json_file(f"map\\{map}.json")
        map_filename = map
        # 开始寻路
        log.info(_("开始寻路"))
        for map_index, map in enumerate(map_data["map"]):
            self.calculated.monthly_pass()
            log.info(_("执行{map_filename}文件:{map_index}/{map_data2} {map}").format(map_filename=map_filename,map_index=map_index+1,map_data2=len(map_data['map']),map=map))
            key = list(map.keys())[0]
            value = map[key]
            if key in ["w", "s", "a", "d"]:
                pos = self.calculated.move(key, value, map_name)
                if self.DEBUG:
                    map_data["map"][map_index]["pos"] = pos
                    log.debug(map_data["map"])
            elif key == "f":
                self.calculated.teleport(key, value)
            elif key == "mouse_move":
                self.calculated.Mouse_move(value)
            elif key == "fighting":
                if value == 1:  # 进战斗
                    ret = self.calculated.fighting()
                    if ret == False and map:
                        fight_log.info(f"执行{map_filename}文件时，识别敌人超时")
                        fight_data = read_json_file(CONFIG_FILE_NAME).get("fight_data", {})
                        date_time = datetime.now().strftime("%m%d%H%M")
                        cv.imwrite(f"logs/image/{map_filename}-{date_time}.jpg",self.calculated.take_screenshot()[0]) #识别超时,截图
                        if map_filename not in fight_data.get("data", {}):
                            day_time = datetime.now().strftime('%Y-%m-%d')
                            if fight_data.get("day_time", 0) != day_time or self.start:
                                fight_data={
                                    "data": [],
                                    "day_time": day_time
                                }
                                fight_data["data"].append(map_filename)
                                self.start = False
                            else:
                                fight_data["data"].append(map_filename)
                                fight_data["day_time"] = day_time
                            modify_json_file(CONFIG_FILE_NAME, "fight_data", fight_data)
                elif value == 2:  # 障碍物
                    self.calculated.Click()
                    time.sleep(1)
                else:
                    raise Exception(_("map数据错误, fighting参数异常:{map_filename}").format(map_filename=map_filename), map)
            elif key == "scroll":
                self.calculated.scroll(value)
            '''
            else:
                raise Exception(_("map数据错误,未匹配对应操作:{map_filename}").format(map_filename=map_filename), map)
            '''

    def auto_map(self, start):
        __, __, __, __, __, width, length = self.calculated.take_screenshot()
        log.info((width,length))
        if not (1915<=width<=1925 and 1075<=length<=1085):
            raise Exception(_("错误的PC分辨率，请调整为1920X1080，请不要在群里问怎么调整分辨率，小心被踢！"))
        def start_map(self:Map, start, check:bool=False):
            wrong_map = True
            if f'map_{start}.json' in self.map_list:
                if not check:
                    map_list = self.map_list[self.map_list.index(f'map_{start}.json'):len(self.map_list)] 
                else:
                    log.info("开始捡漏")
                    map_list = read_json_file(CONFIG_FILE_NAME).get("fight_data", {}).get("data", [])
                for map in map_list:
                    # 选择地图
                    map = map.split('.')[0]
                    map_data = read_json_file(f"map/{map}.json")
                    name:str = map_data['name']
                    author = map_data['author']
                    start_dict = map_data['start']
                    webhook_and_log(_("开始\033[0;34;43m{name}\033[0m锄地").format(name=name))
                    log.info(_("该路线导航作者：\033[0;31;46m{author}\033[0m").format(author=author))
                    log.info(_("感谢每一位无私奉献的作者"))
                    for start in start_dict:
                        self.calculated.monthly_pass()
                        key:str = list(start.keys())[0]
                        log.debug(key)
                        value = start[key]
                        log.debug(f'key: {key}, map: {map}')
                        if key == 'map':
                            time.sleep(1) # 防止卡顿
                            self.calculated.open_map(self.open_map)
                            self.map_init()
                        else:
                            time.sleep(value)
                            if check and "point" in key and map.split("_")[-1] != "1":
                                self.calculated.click_target("temp\\orientation_1.jpg", 0.98)
                                self.calculated.click_target("temp\\orientation_{num}.png".format(num=str(int(key.split("map_")[-1][0])+1)), 0.98)
                                self.calculated.click_target(key.split("_point")[0], 0.98)
                                self.calculated.click_target(key, 0.98)
                            elif not check and wrong_map and "point" in key and map.split("_")[-1] != "1":
                                self.calculated.click_target("temp\\orientation_1.jpg", 0.98)
                                self.calculated.click_target("temp\\orientation_{num}.png".format(num=str(int(key.split("map_")[-1][0])+1)), 0.98)
                                self.calculated.click_target(key.split("_point")[0], 0.98)
                                self.calculated.click_target(key, 0.98)
                                wrong_map = False
                            else:
                                self.calculated.click_target(key, 0.98)
                    #time.sleep(3)
                    count = self.calculated.wait_join()
                    log.info(_('地图加载完毕，加载时间为 {count} 秒').format(count=count))
                    time.sleep(2) # 加2s防止人物未加载
                    map_name = name.split("-")[0]
                    self.start_map(map, map_name)
            else:
                log.info(_('地图编号 {start} 不存在，请尝试检查更新').format(start=start))
        start_map(self, start)
        # 检漏
        if self.data.get("deficiency", True):
            start_map(self, start, True)
