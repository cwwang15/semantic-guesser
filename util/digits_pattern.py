import os
import pickle
import re
from enum import Enum, unique


@unique
class DigitsPattern(Enum):
    """
    year: 1800 - 2100
    """
    same = 8  # 11111, 2222
    repeat_asc = 10  # 123123, 234234
    repeat_des = 14  # 321321
    full_round = 9  # 1232123, 1234321234
    partial_round = 15  # 232123
    palindrome = 7  # 1234321
    ascending = 5  # 1234567
    descending = 6  # 43210
    redundant = 11  # 112233
    yyyymmdd = 0
    # mmddyy = 1
    ddmmyyyy = 2  # 29021997, 290297
    yyyy_plus = 4  # 19881988, 19881989
    yyyy = 3  # 1988
    # mmdd_pair = 13  # 127204
    mmdd = 12
    default = 16
    pass


class Digits:

    def __init__(self):
        self.__pattern = {
            DigitsPattern.ascending: re.compile(
                r"((?:0(?=1)|1(?=2)|2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)|9(?=0)){3,}\d)"
                r"|(012|(?:2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)|9(?=0)){2,}\d)"),
            DigitsPattern.descending: re.compile(
                r"((?:0(?=9)|9(?=8)|8(?=7)|7(?=6)|6(?=5)|5(?=4)|4(?=3)|3(?=2)|2(?=1)|1(?=0)){2,}\d)"),
            DigitsPattern.repeat_asc: re.compile(
                r"((?:0(?=1)|1(?=2)|2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)|9(?=0)){2,}\d)\1+"),
            DigitsPattern.repeat_des: re.compile(
                r"((?:0(?=9)|9(?=8)|8(?=7)|7(?=6)|6(?=5)|5(?=4)|4(?=3)|3(?=2)|2(?=1)|1(?=0)){2,}\d)\1+"),
            DigitsPattern.same: re.compile(r"(\d)\1{2,}"),
            DigitsPattern.redundant: re.compile(r"(\d)\1+(\d)\2+(\d?)\3+(\d?)\4+(\d?)\5+(\d?)\6+"),
            DigitsPattern.palindrome: re.compile(
                r"(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d)(\d)\d?\10\9\8\7\6\5\4\3\2\1"),
            DigitsPattern.full_round: re.compile(
                r"(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d?)(\d)(\d)\9\8\7\6\5\4\3\2\1\2\3\4\5\6\7\8\9\10"),
            DigitsPattern.partial_round: re.compile(
                r"(\d)(\d)\1(\d)\1\2"),
            DigitsPattern.yyyymmdd: re.compile(
                r"("
                r"(((1[89]|20)\d{2})([-/._]?)(10|12|0[13578])([-/._]?)(3[01]|[12][0-9]|0[1-9]))"
                # r"|(((1[89]|20)\d{2})([-/._]?)(10|12|0?[13578])([-/._]?)(3[01]|[12][0-9]|0?[1-9]))"
                r"|(((1[89]|20)\d{2})([-/._]?)(11|0[469])([-/._])(30|[12][0-9]|0[1-9]))"
                r"|(((1[89]|20)\d{2})([-/._]?)02([-/._]?)(2[0-8]|1[0-9]|0[1-9]))"
                r"|(((1[89])0[48])([-/._]?)(02)([-/._]?)(29))"
                r"|(((1[89])[2468][048])([-/._]?)(02)([-/.1_])(29))"
                r"|(((20)[02468][048])([-/._]?)(02)([-/._]?)(29))"
                r"|(((1[89]|20)[13579][26])([-/._]?)(02)([-/._]?)(29))"
                r")"),
            DigitsPattern.yyyy: re.compile(r"(1[89]|20)\d{2}"),
            DigitsPattern.yyyy_plus: re.compile(r"((1[89]|20)\d{2}){2,}"),
            DigitsPattern.mmdd: re.compile(
                r"(((1[02]|0?[13578])([-/._]?)(3[01]|[12][0-9]|0[1-9]))"
                r"|((11|0?[469])([-/._]?)(30|[12][0-9]|0[1-9]))"
                r"|((02)([-/._]?)(2[0-8]|1[0-9]|0[1-9])))"),
            # DigitsPattern.mmdd_pair: re.compile(
            #     r"("
            #     r"((1[02]|0[13578])([-/._]?)(3[01]|[12][0-9]|0[1-9]))"
            #     r"|((1[02]|[13578])([-/._]?)(3[01]|[12][0-9]|0[1-9]))"
            #     r"|((1[02]|0[13578])([-/._]?)(3[01]|[12][0-9]|[1-9]))"
            #     r"|((11|[469])([-/._]?)(30|[12][0-9]|0[1-9]))"
            #     r"|((11|[469])([-/._]?)(30|[12][0-9]|[1-9]))"
            #     r"|((02)([-/._]?)(2[0-8]|1[0-9]|0[1-9]))"
            #     r"|((2)([-/._]?)(2[0-8]|1[0-9]|0[1-9]))"
            #     r"|((02)([-/._]?)(2[0-8]|1[0-9]|[1-9]))"
            #     r"){2}"),
            DigitsPattern.ddmmyyyy: re.compile(
                r"(((10|12|0[13578])([-/._]?)(3[01]|[12][0-9]|0[1-9])([-/._]?)((1[89]|20)\d{2}))"
                r"|((11|0[469])([-/._]?)(30|[12][0-9]|0[1-9])([-/._]?)((1[89]|20)\d{2}))"
                r"|((02)([-/._]?)(2[0-8]|1[0-9]|0[1-9])([-/._]?)((1[89]|20)\d{2}))"
                r"|((02)([-/._]?)(29)([-/._]?)((1[89])0[48]))"
                r"|((02)([-/._]?)(29)([-/._]?)((1[89])[2468][048]))"
                r"|((02)([-/._]?)(29)([-/._]?)((20)[02468][048]))"
                r"|((02)([-/._]?)(29)([-/._]?)((1[89]|20)[13579][26]))"
                r")"),
            # DigitsPattern.ddmmyy: re.compile(
            #     r"((3[01]|[12][0-9]|0[1-9])([-/._]?)((10|12|0[13578])([-/._]?)((1[89]|20)?\d{2}))"
            #     r"|((30|[12][0-9]|0[1-9])([-/._]?)(11|0[469])([-/._]?)((1[89]|20)?\d{2}))"
            #     r"|((2[0-8]|1[0-9]|0[1-9])([-/._]?)(02)([-/._]?)((1[89]|20)?\d{2}))"
            #     r"|((29)([-/._]?)(02)([-/._]?)((1[89])?0[48]))"
            #     r"|((29)([-/._]?)(02)([-/._]?)((1[89])?[2468][048]))"
            #     r"|((29)([-/._]?)(02)([-/._]?)((20)?[02468][048]))"
            #     r"|((29)([-/._]?)(02)([-/._]?)((1[89]|20)?[13579][26]))"
            #     r")"),
            DigitsPattern.default: re.compile(r"\d"),

        }

        self.__pattern2digit = {}
        self.__digit2pattern = {}
        self.__digit2chunk = {}
        pass

    @property
    def digit2pattern_cache(self):
        return self.__digit2pattern

    @property
    def pattern2digit_cache(self):
        return self.__pattern2digit

    @property
    def digit2chunk(self):
        return self.__digit2chunk

    def __which_pattern_segmentation(self, num: str) -> ([DigitsPattern], [str]):
        p_map = self.__pattern
        pattern_list = []
        segment_list = []
        bak_num = str(num)
        while len(num) != 0:
            for p in DigitsPattern:
                m = p_map.get(p).match(num)
                if m is None or len(num) == 0:
                    continue
                else:
                    split = m.group()
                    num = num[len(split):]
                    if p == DigitsPattern.default and len(pattern_list) != 0 \
                            and pattern_list[-1] == DigitsPattern.default:
                        previous = segment_list[-1]
                        segment_list[-1] = previous + split
                    else:
                        pattern_list.append(p)
                        segment_list.append(split)
                    break
        for pattern, instance in zip(pattern_list, segment_list):
            if pattern not in self.__pattern2digit:
                self.__pattern2digit[pattern] = set()
            self.__pattern2digit.get(pattern).add(instance)
            self.__digit2pattern[instance] = pattern
            # print(instance, pattern)
        self.__digit2chunk[bak_num] = segment_list
        return pattern_list, segment_list

    def __which_pattern_no_segmentation(self, num: str) -> ([DigitsPattern], [str]):
        p_map = self.__pattern
        pattern_list = []
        segment_list = []
        for p in DigitsPattern:
            m = p_map.get(p).match(num)
            if m is None:
                continue
            else:
                pattern_list.append(p)
                if p not in self.__pattern2digit:
                    self.__pattern2digit[p] = set()
                self.__pattern2digit.get(p).add(num)
                self.__digit2pattern[num] = p
                break
        self.__digit2chunk[len(num)] = segment_list
        segment_list.append(num)
        return pattern_list, segment_list
        pass

    def which_pattern(self, num: str) -> ([DigitsPattern], [str]):
        return self.__which_pattern_segmentation(num=num)
        pass

    def print_cache(self):
        print(self.__pattern2digit)
        print(self.__digit2pattern)

    def parse_file(self, training_set):
        digit_part = re.compile(r"\d+")
        for line in training_set:
            for d in digit_part.finditer(line):
                self.which_pattern(num=d.group())
        training_set.seek(0)

    def to_pickle(self, file_path):
        print("hello, dump pickle")
        fout = open(file_path, "wb")
        pickle.dump((self.__digit2chunk, self.__digit2pattern, self.__pattern2digit), fout)
        fout.close()

    def from_pickle(self, file_path):
        if os.path.exists(file_path):
            fin = open(file_path, "rb")
            self.__digit2chunk, self.__digit2pattern, self.__pattern2digit = pickle.load(fin)


digits = Digits()
# digits.parse_file("/home/cw/Documents/Passwords/RockYou/rockyou-14-255/tmp.txt")
# digits.print_cache()
# fin = open("/home/cw/Documents/Passwords/RockYou/rockyou-14-255/tmp.txt", "r")
# print(fin.readline())
# fin.seek(0)
# print(fin.readline())
