"""Python micro-concept graph used by the CT-GraphMAS demo."""

from __future__ import annotations

from typing import Any


MICRO_CONCEPT_TABLE = """
K001|Python执行原理|1|解释器基础工作流
K002|控制台基础|1|认识终端与输出窗口
K003|print()基础|1|基础打印字符串与数字
K004|print()多参|1|逗号分隔打印多个值
K005|print(end=)|2|控制打印结束符(取消换行)
K006|单行注释(#)|1|屏蔽单行代码
K007|多行注释|1|三引号屏蔽多行
K008|代码缩进感知|1|理解Python强制缩进的视觉意义
K009|中英文符号辨识|1|全角半角标点致命错误
K010|代码换行(\\)|2|过长代码的换行处理
K011|变量概念|1|标签与盒子隐喻
K012|命名规范|1|字母下划线开头及驼峰命名
K013|关键字避坑|1|不能用if, for等做变量名
K014|赋值(=)|1|右侧计算赋给左侧
K015|整型(int)|1|正负整数
K016|浮点型(float)|1|带小数点的数值
K017|布尔型(bool)|1|True与False
K018|字符串型(str)|1|文本类型
K019|type()检测|2|探测变量当前类型
K020|多重赋值|2|a, b = 1, 2 语法
K021|变量交换|2|a, b = b, a
K022|int()强转|2|字符串转整数
K023|str()强转|2|数值转字符串以便拼接
K024|float()强转|2|整数/字符转浮点数
K025|input()获取|2|获取键盘输入(默认字符串)
K026|加减法(+-)|1|基础数学运算
K027|乘除法(*/)|1|乘法与返回浮点数的除法
K028|整除(//)|3|向下取整除法
K029|取余(%)|3|获取余数(常用于判奇偶)
K030|幂运算(**)|3|次方计算
K031|复合赋值|2|+=, -= 等简写
K032|判等(==/!=)|1|判断是否相等/不等
K033|比较大小|1|>, <, >=, <=
K034|逻辑与(and)|3|全真为真
K035|逻辑或(or)|3|一真即真
K036|逻辑非(not)|3|真假翻转
K037|优先级(括号)|2|利用()强行改变运算顺序
K038|成员运算(in)|2|判断是否存在于序列中
K039|单双引号嵌套|2|解决I'm类冲突
K040|转义字符(\\n)|2|换行符与制表符
K041|字符串拼接(+)|1|文字头尾相连
K042|字符串倍增(*)|2|文字乘数字
K043|正向索引|2|s[0] 起始读取单个字符
K044|反向索引|3|s[-1] 读取末尾字符
K045|基础切片|3|s[start:end] 提取子串
K046|步长切片|3|s[::-1] 倒序等操作
K047|len()长度|2|获取总字符数
K048|.upper()/.lower()|2|大小写转换
K049|.replace()|3|子串替换
K050|.split()|3|按符号分割成列表
K051|f-string|3|高级变量插值 f'x={x}'
K052|单向分支(if)|2|触发器逻辑
K053|双向分支(if-else)|2|非此即彼逻辑
K054|多向(elif)|2|多状态分发
K055|条件块缩进|2|冒号后的层级对齐
K056|条件隐式布尔|3|空列表、0等价于False
K057|嵌套if|3|多维条件层层递进
K058|逻辑联结分支|3|if a > 0 and b < 0
K059|while基础|2|条件循环
K060|while更新迭代|3|避免死循环的 i+=1
K061|for遍历字符串|2|按字符逐个剥离
K062|for遍历列表|2|按元素逐个提取
K063|range(stop)|2|0 到 stop-1
K064|range(start,stop)|2|指定首尾序列
K065|range(step)|3|带步长的跳跃序列
K066|for+range结合|2|指定精确次数的循环
K067|break|3|暴力砸碎整个循环
K068|continue|3|跳过本轮进入下轮
K069|循环嵌套基础|4|外层行，内层列
K070|乘法表嵌套逻辑|4|内层范围依赖外层变量
K071|循环else|4|未被break打断才执行
K072|空列表([])|2|创建容器
K073|列表异构|2|数字字符串混装
K074|列表正向索引|2|list[0]
K075|列表反向索引|3|list[-1]
K076|列表切片|3|list[1:3] 截取子列表
K077|列表元素修改|2|list[0] = 新值
K078|.append()|2|尾部无脑追加
K079|.insert()|3|指定索引插队
K080|.pop()|3|弹出指定或末尾元素
K081|.remove()|3|按值寻找并销毁第一个
K082|.sort()|3|列表原地排序
K083|内置max/min|2|寻找极值
K084|内置sum()|2|列表快速求和
K085|列表拼接(+)|2|两个列表合并
K086|二维列表|4|矩阵的认知 list[i][j]
K087|列表推导式|4|[x for x in list] 极客写法
K088|元组定义(())|3|不可变列表概念
K089|元组拆包|4|a,b,c = (1,2,3)
K090|空字典({})|3|键值对容器
K091|键值对(K-V)|3|字与拼音的映射逻辑
K092|字典取值|3|dict[key] 获取对应Value
K093|新增/修改KV|3|赋新值或更新旧值
K094|字典键的唯一性|4|同名Key会覆盖旧值
K095|字典.get()|4|安全取值防止报错
K096|遍历字典.keys()|4|只遍历所有的键
K097|遍历字典.items()|4|同时遍历键和值
K098|import导包|2|引入外部轮子
K099|from...import|3|精准引入特定函数
K100|random.randint|2|生成整数随机数(猜数字)
K101|random.choice|3|从列表中随机抽签
K102|turtle画布|2|海龟窗口与初始化
K103|turtle前后运动|2|forward, backward
K104|turtle角度转向|3|right, left的几何认知
K105|turtle提笔落笔|3|penup, pendown
K106|math.sqrt|3|数学库开平方
K107|time.sleep|3|让程序暂停几秒
K108|def定义|4|制作自定义流水线
K109|无参函数调用|4|直接执行封装块
K110|形参(接收端)|4|流水线的进料口
K111|实参(调用端)|4|实际投入的原料
K112|return返回值|4|将加工结果吐出流水线
K113|多个返回值|4|return a, b 隐式元组
K114|局部变量隔离|4|函数内部变量出了门就死
K115|全局变量(global)|4|危险的全域共享变量
K116|默认参数|4|def func(a=1)
K117|累加器模式|3|total = 0 配合循环
K118|计数器模式|3|count = 0 配合判断
K119|旗标模式(Flag)|4|is_found = False 的状态标
K120|交换算法|3|利用第三个变量或多重赋值
K121|求极值算法|4|打擂台法找最大最小值
K122|读Traceback行号|2|顺藤摸瓜找报错位置
K123|读英文Error类|2|看懂最后一行的错误类型
K124|SyntaxError|1|语法错误(漏冒号/少括号)
K125|IndentationError|1|缩进不一致/乱敲空格
K126|NameError|2|变量未定义/拼写错
K127|TypeError|2|强行拼接字符串与数字
K128|ValueError|3|int('abc') 无效内容强转
K129|IndexError|3|列表索引越界
K130|KeyError|3|查询字典中不存在的键
K131|AttributeError|4|用错了对象的方法
K132|ZeroDivisionError|2|除数为零错误
K133|逻辑死循环|3|不报错但卡死的运行期故障
K134|try-except基础|4|主动捕获并处理异常
K135|文件读写(open)|4|打开与保存文本
K136|.read()|4|读取全部文件
K137|.write()|4|覆盖写入文件
K138|面向对象(Class)|4|类的初步认知
K139|实例化(Object)|4|从模具中创造对象
K140|self指针|4|理解对象自身引用
K141|对象属性|4|对象的特征
K142|对象方法|4|对象的行为
K143|模块自定义|4|将代码拆分到多文件
K144|__init__方法|4|类的初始化函数
K145|代码重构|4|去除重复、优化结构的工程思维
"""


MICRO_DEPENDENCIES = [
    ("K014", "K011"), ("K019", "K014"), ("K022", "K015"), ("K023", "K018"),
    ("K025", "K003"), ("K028", "K027"), ("K031", "K014"), ("K032", "K014"),
    ("K034", "K032"), ("K037", "K026"), ("K041", "K018"), ("K043", "K018"),
    ("K045", "K043"), ("K046", "K045"), ("K051", "K018"), ("K052", "K032"),
    ("K053", "K052"), ("K054", "K053"), ("K055", "K008"), ("K057", "K053"),
    ("K058", "K034"), ("K059", "K052"), ("K060", "K059"), ("K062", "K072"),
    ("K063", "K015"), ("K066", "K063"), ("K067", "K059"), ("K069", "K062"),
    ("K070", "K069"), ("K074", "K072"), ("K076", "K074"), ("K077", "K074"),
    ("K078", "K072"), ("K086", "K074"), ("K087", "K062"), ("K091", "K090"),
    ("K092", "K091"), ("K096", "K090"), ("K100", "K098"), ("K102", "K098"),
    ("K104", "K102"), ("K108", "K008"), ("K112", "K108"), ("K114", "K108"),
    ("K117", "K062"), ("K124", "K009"), ("K126", "K014"), ("K127", "K019"),
    ("K129", "K074"), ("K130", "K091"),
]


def micro_concepts() -> list[dict[str, Any]]:
    concepts: list[dict[str, Any]] = []
    for raw in MICRO_CONCEPT_TABLE.strip().splitlines():
        concept_id, name, stage, desc = raw.split("|", 3)
        concepts.append({"id": concept_id, "name": name, "stage": int(stage), "desc": desc})
    return concepts


def intermediate_state(concept_id: str, stage: int) -> dict[str, Any]:
    index = int(concept_id.removeprefix("K"))
    if stage == 1:
        mastery, errors = 0.86 + (index % 9) / 100, 0
    elif stage == 2:
        mastery, errors = 0.70 + (index % 15) / 100, 0
    elif stage == 3:
        mastery, errors = 0.30 + (index % 30) / 100, 2 + (index % 3)
    else:
        mastery, errors = 0.10 + (index % 10) / 100, 0
    mastery = round(min(mastery, 0.96), 2)
    status = "Stable" if mastery > 0.8 else "Struggling" if errors > 1 else "Learning"
    return {"mastery_level": mastery, "recent_error_count": errors, "status": status}


def micro_graph_payload() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    concepts = micro_concepts()
    nodes: list[dict[str, Any]] = [
        {
            "id": "student_intermediate_graph",
            "label": "建构期中等生学情",
            "kind": "student_state",
            "description": "测试级学情画像：基础语法较稳定，Stage 3 迁移与错误诊断仍需要支架。",
            "mastery": 0.62,
            "meta": {"profile": "建构期中等生", "note": "根据 145 个微观考点生成的测试级画像"},
        }
    ]
    edges: list[dict[str, Any]] = []
    for concept in concepts:
        state = intermediate_state(concept["id"], concept["stage"])
        node_id = f"py_{concept['id']}"
        nodes.append(
            {
                "id": node_id,
                "label": concept["name"],
                "kind": "micro_concept",
                "description": concept["desc"],
                "mastery": state["mastery_level"],
                "meta": {"concept_id": concept["id"], "stage": concept["stage"]},
            }
        )
        edges.append(
            {
                "source": "student_intermediate_graph",
                "target": node_id,
                "relation": "KNOWS",
                "weight": state["mastery_level"],
                "meta": state,
            }
        )

    for concept_id, required_id in MICRO_DEPENDENCIES:
        edges.append(
            {
                "source": f"py_{concept_id}",
                "target": f"py_{required_id}",
                "relation": "REQUIRES",
                "weight": 0.86,
                "meta": {"source": "145-node cognitive graph"},
            }
        )
    return nodes, edges
