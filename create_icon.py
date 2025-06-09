from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """创建程序图标"""
    # 创建一个 256x256 的图像
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形背景
    circle_color = (41, 128, 185)  # 蓝色
    draw.ellipse([(0, 0), (size, size)], fill=circle_color)
    
    # 添加文字
    try:
        # 尝试加载系统字体
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # 如果找不到系统字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制文字
    text = "帧"
    text_color = (255, 255, 255)  # 白色
    
    # 计算文字位置使其居中
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # 绘制文字
    draw.text((x, y), text, font=font, fill=text_color)
    
    # 保存为 ICO 文件
    image.save('app.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon() 