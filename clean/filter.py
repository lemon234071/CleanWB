import collections
import emoji
from nltk.corpus import wordnet

SAFE_STR = ["的", "重庆", "四川", "海南", "然后", "电影", "系", "爷爷", "娘", "工资", "支持", "机会", "女人", "实现",
            "能力", "机场", "身高", "体重", '滚', '渣男', '绿茶', '视奸', '隔壁老王', 'me too']
SAFE_LIST = ["的",
             '生日快乐', '生日', '日子', '日常', '今日', '节日快乐', '周日', '早日', '过生日',
             '节日', '每日', '早日康复', '明日', '日记', '好日子', '生日礼物', '日日', '过日子',
             '日出', '小日子', '向日葵', '几日', '抗日', '工作日', '日期', '纪念日', '生日会',
             '生日歌', '日后', '夏日', '节假日', '白日梦', '日历', '一日游', '日落',
             '来日方长', '昨日', '风吹日晒', '假日', '冬日', '两日', '混日子', '星期日', '日程',
             '日志', '日夜', '双休日', '三日', '如日中天', '指日可待', '改日', '日渐', '周六日',
             '平日', '日照', '写日记', '没日没夜', '同月同日', '择日', '日食', '生日蛋糕',
             '烈日', '整日', '日有所思', '一日三餐', '日常生活', '抗日战争', '休息日', '有朝一日',
             '落日', '近日', '日日夜夜', '森日', '日理万机', '白日', '度日如年', '往日', '苦日子',
             '同日生', '日记本', '光天化日', '春日', '时日', '日光', '昔日', '当日', '日久见人心',
             '度日', '前几日', '风和日丽', '七日', '次日', '百日', '何日', '多日', '节日愉快',
             '每周日', '日久生情', '世风日下', '秋日', '一日不见', '六日', '过些日子', '日复一日',
             '半日', '日用品', '十日', '蒸蒸日上', '白日做梦', '日思夜想', '日用', '十年如一日',
             '终日', '那日', '日益', '生产日期', '不日', '青天白日', '上周日', '三十日',
             '颜色', '角色', '红色', '白色', '黑色', '蓝色', '粉色', '绿色', '特色', '紫色',
             '灰色', '色调', '色彩',
             '景色', '色号', '调色', '粉红色', '金色', '彩色', '配色', '试色', '本色',
             '棕色', '脸色', '橙色', '肤色', '发色', '掉色', '橘色', '银色', '出色',
             '变色', '色差', '染色', '气色', '褪色', '唇色', '上色', '深色', '清一色', '音色',
             '浅色', '色泽', '五颜六色', '血色', '米色', '花色', '成色', '青色',
             '夜色', '重色轻友', '以色列', '色系', '纯色', '月色', '色素', '秀色可餐', '显色',
             '色香味', '毛色', '号色', '逊色', '调色盘', '色味', '英雄本色', '色色', '咖啡色', '单色', '三色',
             '底色', '驼色', '色盲', '深蓝色', '国色天香', '面色', '百色', '玄色',
             '小角色', '角色扮演', '双色', '墨绿色', '褐色', '黑色幽默', '糖色', '菜色', '眼色',
             '特色小吃', '卡其色', '金黄色', '春色', '天色', '亮色', '平分秋色',
             '秋色', '暖色', '无色', '各有特色', '损色', '不动声色', '杏色', '七色',
             '撞色', '两色', '紫灰色', '颜悦色', '各色', '原色', '色温', '军绿色', '补色',
             '本来', '根本', '基本', '本人', '本事', '本身', '版本', '基本上', '本书', '剧本', '大本营', '原本', '本质',
             '本命年', '本地', '成本', '快本', '本命', '笔记本', '一本正经', '本本', '本地人', '本子', '这本', '没本事',
             '本性', '那本', '本尊', '本色', '两本', '本能', '根本就是', '课本', '几本', '本意', '我本', '本想',
             '户口本', '那本书', '本宫', '本土', '本该', '本分', '本校', '本部', '本是',
             '本领', '本周', '副本', '本体', '本名', '本仙',
             '根本无法', '基本功', '本着', '本次',
             '干了', '干嘛', '干净', '干什么', '干活', '干脆', '饼干', '能干', '不干', '没事干', '干杯', '热干面',
             '干燥', '干巴', '没干', '牛肉干', '干扰', '干锅', '干干净净', '干的事',
             '鸡蛋', '鸡汤', '鸡腿', '炸鸡', '炒鸡', '鸡翅', '鸡肉', '养鸡', '鸡皮疙瘩', '鸡血',
             '鸡爪', '火鸡', '鸡排', '心灵鸡汤', '烤鸡', '炒鸡蛋', '大盘鸡', '辣子鸡', '鸡年',
             '小姐姐', '哥哥', '妹妹',
             '消息', '好消息', '发消息', '小道消息', '最新消息', '假消息', '坏消息',
             '皮肤', '医院',
             "网络"]
BLACK_STR = ['建仓', '低开', '开户', '大盘', '涨停', '跌停', '熔断', '基金', '砸盘', '停牌', '期货', 'A股', '股市',
             'a股', '比特币', '莱特币' '以太坊', '牛市', '熊市', '多头', '空头', '买空', '做空', '做多', '利多',
             '利空', '长空', '长多', '死多', '跳空', '吊空', '实多', '开盘', '收盘', '除息', '除权', '市盈', '洗盘',
             '抢帽子', '坐轿子', '抬轿子', '洗盘', '回档', '拨档', '套牢', '多杀多', '轧空', '支撑线', '支撑位', 'K线',
             '对冲', '抄底', '爆仓', '蓝筹股', 'ST股', '绩优股', '级市场', '券商', '证监会', '股民', '股票', '股东',
             '房价', '油价',
             '安眠药', '胶囊', '注射液', '霉素', '头孢', '粒剂', '复方', '软膏', '嘧啶', '啶', '唑', '沙星', '呋喃',
             '盐酸', '匹林', '布洛芬', '氨基', '胺',
             '税', '法律', '宪法', '民法', '枪毙', '刑', '阉割', '强奸', '港独', '台独', '嫌疑犯',
             '嫌疑人', '涉嫌', '吸毒', '拘役', '行政拘留', '保释', '取保候审', '贪污', '贿', '威胁', '罪', '香港',
             '废青', '南海', '国务院',
             '婊', '贱', '搞基', '草你', '擦你', '靠你', '操你', 'tmd', '特么', '他妈的', '卧槽', '屌',
             '䒑', '点解', '做咩', '唔该', '唔见', '冇', '睇', '乜', '嘢', '边个', '侬', '佢', '乜', '嘅', '嘅', '嬲',
             '系', '咁', '哋', '哋', '睇', '啲', '冧', '冇', '惗', '惗', '咩', '嗻', '嗟', '嚟', '叻', '喺', '抦',
             '俾', '噏', '掟', '囖', '揾', '嗮', '嘥', '攞', '咗', '疴', '乸', '掂', '唓', '嘢', '瞓',
             '微博', '微信', '评论', '楼上', '沙发', '楼主', '私信', '掉粉', '涨粉', '头像', '一楼沙发', '互动话题',
             '互粉', '活动时间', '黑粉', '路转粉', '脑残粉', '私生饭', '爱豆 ', '图一', '图二', '图三', '图四',
             '图五', '图六', '图七', '图八', '图九', '图1', '图2', '图3', '图4', '图5', '图6', '图7', '图8', '图9',
             '视频', '链接', '点赞', '配图',
             '@', '网页链接', '[', '^', '(', '_', '☹️', '¡', '\xa0', '#'
             ]
BLACK_LIST = ['唔', '甘', '操', '擦', '靠', '伐']


class Filter(object):
    def __init__(self, **kwargs):
        self.person_name_set = kwargs.get('person_name_set', set())
        self.black_list_set = kwargs.get('black_list_set', set())
        self.black_str_set = kwargs.get('black_str_set', set())
        self.confuse_set = kwargs.get('confuse_set', set())
        self.is_en = kwargs.get('is_en', set())
        self.database = collections.defaultdict(list)

    def process_str(self, seq_str):
        pass

    def process_word_list(self, seq_word_list):
        pass

    def check_confuse(self, word_list):
        for word in word_list:
            for confuse in self.confuse_set:
                if confuse in word:
                    return word
        return False

    @staticmethod
    def emoji(seq_str):
        emoji.get_emoji_regexp()
        if emoji.emoji_any(seq_str):
            return True
        return False

    def person_name(self, seq_list):
        for word in seq_list:
            if word in self.person_name_set:
                return word
        return False

    def black_str(self, seq_str):
        for word in self.black_str_set:
            if word in seq_str:
                return word
        return False

    def black_wordlist(self, seq_list):
        for word in seq_list:
            if word in self.black_list_set:
                return word
        # for word in self.black_list_set:
        #     if word in seq_list:
        #         return word
        return False

    def not_en(self, seq_list):
        for word in seq_list:
            if word.encode('UTF-8').isalpha():
                if not wordnet.synsets(word):
                    if word not in self.is_en:
                        return word
        return False

    @staticmethod
    def dedup(seq_str):
        char_set = set()
        n = 0
        last_char = None
        seven_i = 0
        new_list = []
        last_i = 0
        for i, char in enumerate(seq_str):
            char_set.add(char)
            if char == last_char:
                n += 1
                if n == 6:
                    seven_i = i
            else:
                if n > 5:
                    new_list.append(seq_str[last_i:seven_i])
                    last_i = i
                n = 0
            last_char = char
        end = seven_i if n > 5 else len(seq_str)
        new_list.append(seq_str[last_i:end])
        if len(char_set) < 2 < len(seq_str):
            return None
        return "".join(new_list) if new_list else seq_str

    def duplicated_original(self, seq_str):
        """
        :type seq_str: str
        :rtype: bool
        """
        n = len(seq_str)
        for i in range(1, n // 2 + 1):
            if n % i == 0:
                a = seq_str[:i]
                j = i
                while j < n and seq_str[j:j + i] == a:
                    j += i
                if j == n:
                    return True
        return False

    @staticmethod
    def duplicated(seq_str, times, length=2):
        """
        :type seq_str: str
        :rtype: bool
        """
        count = 0
        n = len(seq_str)
        for k in range(0, n - (times + 1) * (length + 1)):
            for i in range(times - 1, (n - k) // times + 1):
                a = seq_str[k: k + i]
                j = k + i
                while j < n and i > length and seq_str[j:j + i] == a:
                    j += i
                    count += 1
                    if count > (times - 2):
                        return True
        return False

    @staticmethod
    def duplicated_list(seq_list, times, length=1):
        count = 0
        last_word = None
        for word in seq_list:
            if word == last_word:
                count += 1
                if count > times:
                    if len(word) > length:
                        return True
            else:
                count = 0
            last_word = word
        return False

    @staticmethod
    def my_duplicated(seq_list):
        word_dict = {}
        for word in seq_list:
            if word not in word_dict.keys():
                word_dict[word] = 1
            else:
                word_dict[word] += 1
        # fitler duplicate
        num_list = list(word_dict.values())
        num_list.sort(reverse=True)

        if len(num_list) <= 1 / 3 * len(seq_list):
            return True

        if len(num_list) > 3 and len(num_list) < len(seq_list):
            if sum(num_list[: 3]) > 0.75 * len(seq_list):
                return True
        return False

    def too_short(self, seq_str, length):
        if len(seq_str) < length:
            return True
        return False
