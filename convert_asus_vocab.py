#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
華碩智慧輸入法 (ASUS Smart Input) 個人詞庫自動化轉換工具
功能：
1. 讀取每行一詞的純中文文字檔 (如 a.txt)
2. 自動校正為台灣教育部 (MOE) 標準發音 (解決兩岸拼音發音差異)
3. 修正輕聲符號位置 (移至音節最前端，如 ˙ㄗ)
4. 補齊第一聲專用符號 (ˉ, Unicode \\u02C9)
5. 嚴格排版為「詞彙 + 雙半形空格 + 連續注音」之華碩相容格式
"""

import os
import sys

try:
    from pypinyin import pinyin, Style, load_single_dict
except ImportError:
    print("錯誤：尚未安裝 pypinyin 套件。請先執行：pip install pypinyin")
    sys.exit(1)

# 1. 台灣教育部標準注音字典強制覆寫表
# 修正兩岸常用字發音分歧，防止被華碩輸入法嚴格字音校驗引擎退件
taiwan_moe_dict = {
    ord('期'): 'qí',   # 定期、期中 (台灣二聲，大陸一聲)
    ord('息'): 'xí',   # 除息、休息 (台灣二聲，大陸一聲)
    ord('質'): 'zhí',  # 品質、物質 (台灣二聲，大陸四聲)
    ord('微'): 'wéi',  # 微軟、微小 (台灣二聲，大陸一聲)
    ord('危'): 'wéi',  # 危險、危機 (台灣二聲，大陸一聲)
    ord('識'): 'shì',  # 知識、常識
    ord('伺'): 'sì',   # 伺服器 (台灣四聲 ㄙˋ，大陸四聲 ㄘˋ ci4)
    ord('檔'): 'dǎng',  # 檔案、檔期
    ord('擊'): 'jí',   # 攻擊、點擊
    ord('企'): 'qì',   # 企業、企劃 (台灣四聲，大陸三聲)
    ord('究'): 'jiù',  # 研究、究竟
    ord('垃'): 'lè',   # 垃圾 (台灣 ㄌㄜˋ)
    ord('圾'): 'sè',   # 垃圾 (台灣 ㄙㄜˋ)
    ord('崖'): 'yái',  # 懸崖 (台灣 ㄧㄞˊ)
    ord('括'): 'guā',  # 包括、概括 (台灣 ㄍㄨㄚˉ)
    ord('剖'): 'pǒu',  # 剖析 (台灣 ㄆㄡˇ)
    ord('攜'): 'xī',   # 攜帶 (台灣 ㄒㄧˉ)
    ord('寂'): 'jí',   # 寂寞
    ord('偽'): 'wèi',  # 偽造、虛偽
    ord('署'): 'shù',  # 部署、公署 (台灣四聲，大陸三聲)
    ord('蹈'): 'dào',  # 舞蹈 (台灣四聲，大陸三聲)
    ord('蝸'): 'guā',  # 蝸牛 (台灣 ㄍㄨㄚˉ)
    ord('液'): 'yè',   # 液體、血液 (台灣四聲，大陸四聲/一聲)
    ord('亞'): 'yà',   # 亞洲 (台灣四聲 ㄧㄚˋ)
    ord('綜'): 'zòng'  # 綜合 (台灣四聲 ㄗㄨㄥˋ)
}
load_single_dict(taiwan_moe_dict)

TONE_MARKS = {'ˊ', 'ˇ', 'ˋ', '˙'}
FIRST_TONE = 'ˉ'  # Unicode \u02C9 (一聲橫線)

def get_asus_bopomofo(word: str) -> str:
    """將單個中文詞彙轉譯為華碩智慧輸入法相容的注音字串。"""
    raw_syllables = pinyin(word, style=Style.BOPOMOFO)
    bopomofo_parts = []
    
    for item in raw_syllables:
        syllable = item[0]
        
        # 輕聲符號處理：華碩規定輕聲點 ˙ 必須位於音節最前方
        if '˙' in syllable:
            syllable = '˙' + syllable.replace('˙', '')
            
        # 第一聲補齊：若未帶有二三四聲或輕聲標記，補上 ˉ
        if not any(mark in syllable for mark in TONE_MARKS):
            syllable += FIRST_TONE
            
        bopomofo_parts.append(syllable)
        
    return "".join(bopomofo_parts)

def convert_vocab(input_file: str, output_file: str = None) -> int:
    if not os.path.exists(input_file):
        print(f"錯誤：找不到檔案 {input_file}")
        return 0

    if output_file is None:
        base, _ = os.path.splitext(input_file)
        output_file = f"asus_ready_{base}.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    results = []
    skipped = 0
    for w in words:
        if len(w) < 2 or len(w) > 9:
            skipped += 1
            continue
        bopo = get_asus_bopomofo(w)
        # 規格：詞彙 + 恰好兩個半形空格 + 連續注音
        results.append(f"{w}  {bopo}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n")

    print(f"轉換完成！共處理 {len(results)} 筆詞彙（略過長度不符 {skipped} 筆）。")
    print(f"已產出華碩格式檔案：{output_file}")
    return len(results)

if __name__ == "__main__":
    candidate_files = ["a.txt", "homophones.txt", "raw_words.txt", "user_vocab.txt"]
    target = sys.argv[1] if len(sys.argv) > 1 else next((f for f in candidate_files if os.path.exists(f)), None)

    if target is None:
        print("未指定輸入檔案。候選檔案皆不存在。請傳入檔名參數，例如：python convert_asus_vocab.py my_words.txt")
        sys.exit(1)

    convert_vocab(target)
