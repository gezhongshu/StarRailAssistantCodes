## 项目说明
本项目基于
[Starry-Wind/StarRailAssistant](https://github.com/Starry-Wind/StarRailAssistant)
修改而来，只包含其中的部分代码，根据本人使用体验，对部分代码进行了调整。

**项目使用方式：更新[StarRailAssistant](https://github.com/Starry-Wind/StarRailAssistant)工具至最新（或任意）版本；下载本项目代码覆盖代码部分；后续使用方法参考原项目。**

*注意事项：进行资源更新时，请勿更新脚本，只需更新后两项“图片”和“地图”。*

*由于原项目停止更新，在下一次地图更新时，本项目将适配其迁移后的项目[Night-stars-1
/ Auto_Star_Rail](https://github.com/Night-stars-1/Auto_Star_Rail)。*

本项目中代码调整主要包括以下几处：
- 在gui.py中删除了update()函数的代理选项（在本人使用过程中，代理参数会报错或者下载失败）；
- 在map.py中调整了高亮字符的显示颜色，是其在powershell终端更加清晰；
- 在utils/calculated.py中增加了fighting()函数鼠标点击后的等待时间，防止频繁点击，完成战斗后增加一次点击，可以击破部分战斗点位的可破坏物；
- 在utils/calculated.py中修改wait_join()函数的最长等待时间为2秒(835行)，utils/config.py中 join_time的默认值同样做了调整(272行)。如果你的等待时间仍然超过8秒，请修改config.json文件中的“join_time”键值。注意此值应当根据自己的设备性能合理设置；
- 在utils/calculated.py中修改click_target()函数部分代码，当目标点位位于屏幕外时，在更大的范围内拖动地图；
- 修正了部分调用的函数名错误（typos）。

## 致谢
感谢
[Starry-Wind/StarRailAssistant](https://github.com/Starry-Wind/StarRailAssistant)项目各位开发者提供的工具。