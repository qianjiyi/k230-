import time
import os
import image

from media.sensor import *
from media.display import *
from media.media import *
from machine import TOUCH

# 屏幕和图像参数
lcd_width = 800
lcd_height = 480

img_width = 480
img_height = 480

# 从 1920x1080 图像中裁剪 480x480
cut_roi = (540, 300, 480, 480)

# 480x480 图像居中显示到 800x480 屏幕
show_x_offset = (lcd_width - img_width) // 2
show_y_offset = (lcd_height - img_height) // 2

sensor = None


# 工作模式
MODE_NORMAL = 0      # 正常摄像头显示模式
MODE_ADJUST = 1      # 灰度阈值调节模式
# 开机默认进入调阈值模式
# 如果想开机直接正常显示，改成 MODE_NORMAL
work_mode = MODE_ADJUST

# 正常模式下长按触发区域，坐标是 480x480 图像坐标，这里设置在右上角
NORMAL_TRIGGER_X = 360
NORMAL_TRIGGER_Y = 0
NORMAL_TRIGGER_W = 120
NORMAL_TRIGGER_H = 60
# 长按 8 秒进入调阈值模式
NORMAL_HOLD_MS = 8000
# 触摸丢失容错时间，防止手指没松，但 tp.read() 偶尔读不到点，导致 Hold 时间清零
NORMAL_TOUCH_LOST_GRACE_MS = 500
# 调阈值模式长按参数，按住超过 500ms 后开始连续变化
HOLD_START_MS = 500
# 长按连续变化间隔
REPEAT_MS = 80

# 按键配置表
# 坐标是 480x480 图像坐标
#
# name   : 按键名称
# x y w h: 触摸区域
# text   : 显示文字
# repeat : 是否允许长按连续触发
# enable : 是否启用
BUTTONS = [
    {
        "name": "l_min_down",
        "x": 0,
        "y": 60,
        "w": 120,
        "h": 60,
        "text": "Lmin-",
        "repeat": True,
        "enable": True,
    },
    {
        "name": "l_min_up",
        "x": 360,
        "y": 60,
        "w": 120,
        "h": 60,
        "text": "Lmin+",
        "repeat": True,
        "enable": True,
    },

    {
        "name": "l_max_down",
        "x": 0,
        "y": 180,
        "w": 120,
        "h": 60,
        "text": "Lmax-",
        "repeat": True,
        "enable": True,
    },
    {
        "name": "l_max_up",
        "x": 360,
        "y": 180,
        "w": 120,
        "h": 60,
        "text": "Lmax+",
        "repeat": True,
        "enable": True,
    },

    {
        "name": "step_down",
        "x": 0,
        "y": 300,
        "w": 120,
        "h": 60,
        "text": "step-",
        "repeat": False,
        "enable": True,
    },
    {
        "name": "step_up",
        "x": 360,
        "y": 300,
        "w": 120,
        "h": 60,
        "text": "step+",
        "repeat": False,
        "enable": True,
    },

    {
        "name": "reset",
        "x": 0,
        "y": 420,
        "w": 120,
        "h": 60,
        "text": "RESET",
        "repeat": False,
        "enable": True,
    },
    {
        "name": "save",
        "x": 360,
        "y": 420,
        "w": 120,
        "h": 60,
        "text": "SAVE",
        "repeat": False,
        "enable": True,
    },

    # 退出按钮
    # 按下后退出调阈值模式
    # 进入正常摄像头显示模式
    {
        "name": "exit",
        "x": 180,
        "y": 360,
        "w": 120,
        "h": 50,
        "text": "EXIT",
        "repeat": False,
        "enable": True,
    },

    # 预留空按键
    # 后面可自己加功能
    {
        "name": "empty_1",
        "x": 140,
        "y": 60,
        "w": 80,
        "h": 60,
        "text": "K1",
        "repeat": False,
        "enable": True,
    },
    {
        "name": "empty_2",
        "x": 260,
        "y": 60,
        "w": 80,
        "h": 60,
        "text": "K2",
        "repeat": False,
        "enable": True,
    },
    {
        "name": "empty_3",
        "x": 140,
        "y": 420,
        "w": 80,
        "h": 60,
        "text": "K3",
        "repeat": False,
        "enable": True,
    },
    {
        "name": "empty_4",
        "x": 260,
        "y": 420,
        "w": 80,
        "h": 60,
        "text": "K4",
        "repeat": False,
        "enable": True,
    },
]

# 显示函数
def show_img(img):
    Display.show_image(
        img,
        x=show_x_offset,
        y=show_y_offset
    )

# LCD触摸坐标转图像坐标
def lcd_to_img_touch(x, y):
    img_x = x - show_x_offset
    img_y = y - show_y_offset
    return img_x, img_y

# 判断是否按在正常模式触发区域
def is_in_normal_trigger_area(x, y):
    if NORMAL_TRIGGER_X <= x < NORMAL_TRIGGER_X + NORMAL_TRIGGER_W:
        if NORMAL_TRIGGER_Y <= y < NORMAL_TRIGGER_Y + NORMAL_TRIGGER_H:
            return True

    return False

# 根据按钮名查按钮配置
def get_button_cfg(button_name):
    for btn in BUTTONS:
        if btn["name"] == button_name:
            return btn

    return None

# 判断按下哪个按钮
def get_touch_button(x, y):
    """
    x, y 是 480x480 图像坐标
    返回按钮 name
    """
    if x < 0 or x >= 480 or y < 0 or y >= 480:
        return None

    for btn in BUTTONS:
        if not btn["enable"]:
            continue

        bx = btn["x"]
        by = btn["y"]
        bw = btn["w"]
        bh = btn["h"]

        if bx <= x < bx + bw and by <= y < by + bh:
            return btn["name"]

    return None

# 执行按钮功能
def apply_touch_button(button, l_min, l_max, step):
    global work_mode

    if button == "l_min_down":
        l_min = max(0, l_min - step)

    elif button == "l_min_up":
        l_min = min(255, l_min + step)

    elif button == "l_max_down":
        l_max = max(0, l_max - step)

    elif button == "l_max_up":
        l_max = min(255, l_max + step)

    elif button == "step_down":
        step = max(1, step - 1)

    elif button == "step_up":
        step = min(20, step + 1)

    elif button == "reset":
        l_min = 0
        l_max = 255
        step = 1
        print("阈值已复位: [({}, {})], step={}".format(l_min, l_max, step))

    elif button == "save":
        print("当前灰度阈值: [({}, {})]".format(l_min, l_max))
        print("当前 step:", step)

    elif button == "exit":
        work_mode = MODE_NORMAL
        print("已退出阈值调节模式，进入正常摄像头显示模式")

    # 预留空按键功能区
    # 后面想加功能就在这里写
    elif button == "empty_1":
        print("按下预留按键 K1")

    elif button == "empty_2":
        print("按下预留按键 K2")

    elif button == "empty_3":
        print("按下预留按键 K3")

    elif button == "empty_4":
        print("按下预留按键 K4")

    # 防止最小值大于最大值
    if l_min > l_max:
        l_min = l_max

    return l_min, l_max, step

# 画单个按钮
def draw_one_button(img, btn, current_button):
    x = btn["x"]
    y = btn["y"]
    w = btn["w"]
    h = btn["h"]
    text = btn["text"]

    fill_color = (255, 255, 255)
    border_color = (255, 0, 0)
    text_color = (255, 0, 0)

    # 预留按键：蓝色
    if btn["name"].startswith("empty"):
        border_color = (0, 0, 255)
        text_color = (0, 0, 255)

    # 退出按键：黄色
    if btn["name"] == "exit":
        border_color = (255, 255, 0)
        text_color = (255, 255, 0)

    # 当前按下的按键：绿色
    if btn["name"] == current_button:
        border_color = (0, 255, 0)
        text_color = (0, 255, 0)

    # 禁用按键：灰色
    if not btn["enable"]:
        border_color = (120, 120, 120)
        text_color = (120, 120, 120)

    # 背景
    img.draw_rectangle(
        x,
        y,
        w,
        h,
        color=fill_color,
        thickness=1,
        fill=True
    )

    # 外框：实际触摸范围
    img.draw_rectangle(
        x,
        y,
        w,
        h,
        color=border_color,
        thickness=4,
        fill=False
    )

    # 内框：增强边界
    if w > 12 and h > 12:
        img.draw_rectangle(
            x + 5,
            y + 5,
            w - 10,
            h - 10,
            color=border_color,
            thickness=2,
            fill=False
        )

    # 文字
    img.draw_string_advanced(
        x + 8,
        y + 14,
        24,
        text,
        color=text_color
    )

# 画调阈值UI界面
def draw_adjust_ui(img, l_min, l_max, step, fps, current_button):
    # 顶部信息栏
    img.draw_rectangle(
        0,
        0,
        480,
        45,
        color=(255, 255, 255),
        thickness=1,
        fill=True
    )

    img.draw_string_advanced(
        5,
        5,
        22,
        "Lmin:{} Lmax:{} step:{} FPS:{:.1f}".format(
            l_min,
            l_max,
            step,
            fps
        ),
        color=(255, 0, 0)
    )

    # 画所有按键
    for btn in BUTTONS:
        draw_one_button(img, btn, current_button)

# 正常摄像头模式，左上角显示FPS，右上角小区域长按 8 秒进入调阈值模式，加入触摸丢失容错，防止 Hold 时间一直刷新
def normal_mode_process(
    tp,
    img,
    fps,
    normal_touch_down,
    normal_touch_start_time,
    normal_last_touch_time
):
    global work_mode

    points = tp.read()
    now = time.ticks_ms()

    # 左上角显示 FPS
    img.draw_rectangle(
        0,
        0,
        145,
        40,
        color=(255, 255, 255),
        thickness=1,
        fill=True
    )

    img.draw_string_advanced(
        5,
        5,
        24,
        "FPS:{:.1f}".format(fps),
        color=(255, 0, 0)
    )
    # 右上角长按触发区域
    img.draw_rectangle(
        NORMAL_TRIGGER_X,
        NORMAL_TRIGGER_Y,
        NORMAL_TRIGGER_W,
        NORMAL_TRIGGER_H,
        color=(255, 255, 255),
        thickness=1,
        fill=True
    )

    img.draw_rectangle(
        NORMAL_TRIGGER_X,
        NORMAL_TRIGGER_Y,
        NORMAL_TRIGGER_W,
        NORMAL_TRIGGER_H,
        color=(0, 255, 0),
        thickness=3,
        fill=False
    )

    img.draw_string_advanced(
        NORMAL_TRIGGER_X + 8,
        NORMAL_TRIGGER_Y + 18,
        20,
        "HOLD 8s",
        color=(0, 255, 0)
    )
    # 判断这一帧触摸是否有效
    touch_valid = False

    if len(points) > 0:
        lcd_x = points[0].x
        lcd_y = points[0].y

        # LCD 坐标转 480x480 图像坐标
        touch_x, touch_y = lcd_to_img_touch(lcd_x, lcd_y)

        # 只有按在右上角绿色框内才有效
        if is_in_normal_trigger_area(touch_x, touch_y):
            touch_valid = True
            normal_last_touch_time = now

            # 第一次按下
            if not normal_touch_down:
                normal_touch_down = True
                normal_touch_start_time = now
                print("开始长按 HOLD 区域")
    # 长按计时逻辑
    if normal_touch_down:
        lost_time = time.ticks_diff(now, normal_last_touch_time)

        # touch_valid=True：当前帧还按着
        # lost_time < 容错时间：当前帧没读到，但认为还没松手
        if touch_valid or lost_time < NORMAL_TOUCH_LOST_GRACE_MS:
            press_time = time.ticks_diff(now, normal_touch_start_time)

            # 显示长按时间
            img.draw_rectangle(
                150,
                0,
                205,
                40,
                color=(255, 255, 255),
                thickness=1,
                fill=True
            )

            img.draw_string_advanced(
                155,
                5,
                22,
                "Hold:{:.1f}s".format(press_time / 1000),
                color=(0, 255, 0)
            )

            # 画长按进度条
            progress_w = int(NORMAL_TRIGGER_W * press_time / NORMAL_HOLD_MS)

            if progress_w > NORMAL_TRIGGER_W:
                progress_w = NORMAL_TRIGGER_W

            img.draw_rectangle(
                NORMAL_TRIGGER_X,
                NORMAL_TRIGGER_Y + NORMAL_TRIGGER_H - 8,
                progress_w,
                8,
                color=(0, 255, 0),
                thickness=1,
                fill=True
            )

            # 长按满 8 秒，进入调阈值模式
            if press_time >= NORMAL_HOLD_MS:
                work_mode = MODE_ADJUST

                normal_touch_down = False
                normal_touch_start_time = 0
                normal_last_touch_time = 0

                print("长按右上角区域 8 秒，进入灰度阈值调节模式")

        else:
            # 超过容错时间还没检测到触摸，才认为松手
            normal_touch_down = False
            normal_touch_start_time = 0
            normal_last_touch_time = 0

            print("HOLD 松开或离开区域，计时清零")

    show_img(img)

    return normal_touch_down, normal_touch_start_time, normal_last_touch_time

# 调阈值模式触摸处理，短按一次，长按连续
def adjust_touch_process(
    tp,
    l_min,
    l_max,
    step,
    touch_was_down,
    touch_start_time,
    last_repeat_time,
    last_button
):
    points = tp.read()
    now = time.ticks_ms()
    current_button = None

    if len(points) > 0:
        lcd_x = points[0].x
        lcd_y = points[0].y

        touch_x, touch_y = lcd_to_img_touch(lcd_x, lcd_y)
        button = get_touch_button(touch_x, touch_y)

        current_button = button

        if button is not None:
            btn_cfg = get_button_cfg(button)

            # 第一次按下，立即执行一次
            if not touch_was_down:
                touch_was_down = True
                touch_start_time = now
                last_repeat_time = now
                last_button = button

                l_min, l_max, step = apply_touch_button(
                    button,
                    l_min,
                    l_max,
                    step
                )

            else:
                # 按住时滑到另一个按钮，重新执行一次并重新计时
                if button != last_button:
                    touch_start_time = now
                    last_repeat_time = now
                    last_button = button

                    l_min, l_max, step = apply_touch_button(
                        button,
                        l_min,
                        l_max,
                        step
                    )

                else:
                    # repeat=True 的按钮才允许长按连续触发
                    if btn_cfg is not None and btn_cfg["repeat"]:
                        if time.ticks_diff(now, touch_start_time) > HOLD_START_MS:
                            if time.ticks_diff(now, last_repeat_time) > REPEAT_MS:
                                last_repeat_time = now

                                l_min, l_max, step = apply_touch_button(
                                    button,
                                    l_min,
                                    l_max,
                                    step
                                )

        else:
            touch_was_down = False
            last_button = None
            current_button = None

    else:
        touch_was_down = False
        last_button = None
        current_button = None

    return (
        l_min,
        l_max,
        step,
        touch_was_down,
        touch_start_time,
        last_repeat_time,
        last_button,
        current_button
    )

# 主程序
try:
    # 摄像头初始化
    sensor = Sensor(width=1920, height=1080)
    sensor.reset()
    sensor.set_framesize(width=1920, height=1080)
    sensor.set_pixformat(Sensor.RGB565)
    # LCD初始化
    Display.init(
        Display.ST7701,
        width=lcd_width,
        height=lcd_height,
        to_ide=True
    )

    MediaManager.init()
    sensor.run()
    # 触摸屏初始化
    tp = TOUCH(0)
    # 灰度阈值
    l_min = 0
    l_max = 255
    # 每次变化的值
    step = 1
    # 调阈值模式：短按 / 长按状态变量
    touch_was_down = False
    touch_start_time = 0
    last_repeat_time = 0
    last_button = None
    current_button = None
    # 正常模式：长按右上角区域 8 秒进入调阈值
    normal_touch_down = False
    normal_touch_start_time = 0
    normal_last_touch_time = 0
    clock = time.clock()
    print("程序启动")
    print("默认进入灰度阈值调节模式")
    print("EXIT：退出到正常摄像头显示")
    print("正常模式右上角 HOLD 8s 区域：长按 8 秒重新进入调阈值模式")
    print("SAVE：打印当前灰度阈值")
    #---------------------  主循环 ----------------------
    while True:
        clock.tick()
        os.exitpoint()
        # 读取原始图像
        img = sensor.snapshot(chn=CAM_CHN_ID_0)
        img = img.copy(roi=cut_roi)
        # 正常摄像头显示模式
        if work_mode == MODE_NORMAL:
            normal_touch_down, normal_touch_start_time, normal_last_touch_time = normal_mode_process(
                tp,
                img,
                clock.fps(),
                normal_touch_down,
                normal_touch_start_time,
                normal_last_touch_time
            )
        # 灰度阈值调节模式
        elif work_mode == MODE_ADJUST:
            gray = img.to_grayscale(copy=True)

            threshold = [(l_min, l_max)]

            binary = gray.binary(threshold)
            binary = binary.to_rgb565()

            (
                l_min,
                l_max,
                step,
                touch_was_down,
                touch_start_time,
                last_repeat_time,
                last_button,
                current_button
            ) = adjust_touch_process(
                tp,
                l_min,
                l_max,
                step,
                touch_was_down,
                touch_start_time,
                last_repeat_time,
                last_button
            )

            draw_adjust_ui(
                binary,
                l_min,
                l_max,
                step,
                clock.fps(),
                current_button
            )

            show_img(binary)


except KeyboardInterrupt as e:
    print("用户停止:", e)

except BaseException as e:
    print("异常:", e)

finally:
    if isinstance(sensor, Sensor):
        sensor.stop()

    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
