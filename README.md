# AniNet 数据自动化

经 bangumi [技术宅](https://bgm.tv/group/topic/358702)
小组网友建议，手动添加人物实在太过痛苦。
为加快创建更多作品网络的制作进程，需要搞一点自动化。

## bgm.tv 数据提取

提取 bgm.tv 动画页面上的数据生成带有节点信息的 json 文件。

### 安装依赖

```bash
$ pip install fire requests lxml
...
```

### 运行

不是很会写异步代码，所以目前还是同步版本的脚本。使用多线程加速，速度有点慢。

第一个参数是需要抓取的页面id（按照评价排名的编号，比如第二页就是 `https://bgm.tv/anime/browser?sort=rank&page=2`）列表，比如我要用 10 个线程抓取前 100 页：

```bash
$ python bgm.py $(seq 1 100 | tr '\n' ',') --workers 10
...
```

### 数据

前 200 页作品的 json 文件位于 [`./data/bgm/json`](./data/bgm/json) 目录下，
作品名与 id 对应关系见[此文件](./data/bgm/index.json)。
