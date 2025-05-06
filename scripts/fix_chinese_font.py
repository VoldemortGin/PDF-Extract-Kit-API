import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform
import os

def find_chinese_font():
    """查找系统中支持中文的字体"""
    print("正在查找支持中文的字体...")
    
    # 获取所有字体
    fonts = fm.findSystemFonts()
    
    # 常见的中文字体名称
    chinese_font_names = [
        'SimHei', 'SimSun', 'NSimSun', 'FangSong', 'KaiTi', 'Microsoft YaHei', 
        'STHeiti', 'STKaiti', 'STSong', 'STFangsong', 'PingFang SC', 'Heiti SC',
        'Songti SC', 'Kaiti SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei',
        'Source Han Sans CN', 'Noto Sans CJK SC', 'Noto Sans SC', 'Noto Serif SC',
        'HanaMinA', 'HanaMinB', 'SimSun-ExtB', 'MingLiU', 'MingLiU-ExtB'
    ]
    
    # 检查系统类型
    system = platform.system()
    if system == 'Darwin':  # macOS
        # macOS 上常见的中文字体
        chinese_font_names.extend(['PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'Apple LiGothic'])
    elif system == 'Windows':
        # Windows 上常见的中文字体
        chinese_font_names.extend(['Microsoft YaHei', 'SimSun', 'SimHei', 'FangSong'])
    elif system == 'Linux':
        # Linux 上常见的中文字体
        chinese_font_names.extend(['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC'])
    
    # 查找中文字体
    chinese_fonts = []
    for font in fonts:
        try:
            font_name = fm.FontProperties(fname=font).get_name()
            if any(chinese_name.lower() in font_name.lower() for chinese_name in chinese_font_names):
                chinese_fonts.append(font)
        except:
            continue
    
    # 如果找到了中文字体，返回第一个
    if chinese_fonts:
        print(f"找到 {len(chinese_fonts)} 个可能支持中文的字体")
        font_names = [fm.FontProperties(fname=font).get_name() for font in chinese_fonts[:5]]
        print(f"前5个中文字体: {font_names}")
        
        # 优先选择常用的中文字体
        preferred_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'PingFang SC', 'Noto Sans CJK SC']
        for preferred in preferred_fonts:
            for font, name in zip(chinese_fonts, [fm.FontProperties(fname=font).get_name() for font in chinese_fonts]):
                if preferred.lower() in name.lower():
                    print(f"使用字体: {name}")
                    return font
        
        # 如果没有找到优先字体，使用第一个
        print(f"使用字体: {fm.FontProperties(fname=chinese_fonts[0]).get_name()}")
        return chinese_fonts[0]
    
    # 如果没有找到中文字体，返回None
    print("未找到支持中文的字体")
    return None

def setup_chinese_font():
    """设置matplotlib使用中文字体"""
    # 查找中文字体
    chinese_font = find_chinese_font()
    
    if chinese_font:
        # 设置matplotlib使用中文字体
        font_prop = fm.FontProperties(fname=chinese_font)
        plt.rcParams['font.family'] = font_prop.get_name()
        
        # 另一种方式：直接添加到fontManager
        try:
            font_path = chinese_font
            font_name = fm.FontProperties(fname=font_path).get_name()
            fm.fontManager.addfont(font_path)
            print("成功添加字体到fontManager")
            return True
        except:
            print("添加字体到fontManager失败")
            return False
    else:
        # 如果没有找到中文字体，尝试使用matplotlib内置的字体
        print("尝试使用matplotlib内置的字体...")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        return False

# 设置中文字体
setup_chinese_font()

# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 测试绘图
def test_chinese_font():
    """测试中文字体是否正常显示"""
    fig, ax = plt.subplots(figsize=(5, 1))
    ax.text(0.5, 0.5, '布局检测结果', ha='center', va='center', fontsize=12)
    ax.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 创建一个更复杂的图表
    labels = ['布局', '检测', '结果']
    values = [30, 40, 20]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title('布局检测结果')
    ax.set_xlabel('类别')
    ax.set_ylabel('数量')
    plt.tight_layout()
    plt.show()

# 运行测试
# test_chinese_font()
