from io import BytesIO
from pathlib import Path
from typing import List, Protocol

from PIL.Image import Image
from pil_utils import BuildImage


class Maker(Protocol):
    def __call__(self, img: BuildImage) -> BuildImage:
        ...


def save_gif(frames: List[Image], duration: float) -> BytesIO:
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration * 1000,
        loop=0,
        disposal=2,
        optimize=False,
    )

    # 没有超出最大大小，直接返回
    n = output.getbuffer().nbytes
    if n <= 10 * 10**6:
        return output

    # 超出最大大小，帧数超出最大帧数时，缩减帧数
    n_frames = len(frames)
    gif_max_frames = 100
    if n_frames > gif_max_frames:
        ratio = n_frames / gif_max_frames
        index = (int(i * ratio) for i in range(gif_max_frames))
        new_duration = duration * ratio
        new_frames = [frames[i] for i in index]
        return save_gif(new_frames, new_duration)

    # 超出最大大小，帧数没有超出最大帧数时，缩小尺寸
    new_frames = [
        frame.resize((int(frame.width * 0.9), int(frame.height * 0.9)))
        for frame in frames
    ]
    return save_gif(new_frames, duration)


def draw(images: List[BuildImage]):
    img_dir = Path(__file__).parent / "draw"
    img = images[0].convert("RGBA").resize((175, 120), keep_ratio=True)
    params = (
        (((27, 0), (207, 12), (179, 142), (0, 117)), (30, 16)),
        (((28, 0), (207, 13), (180, 137), (0, 117)), (34, 17)),
    )
    raw_frames = [BuildImage.open(img_dir / f"{i}.png") for i in range(6)]
    for i in range(2):
        points, pos = params[i]
        raw_frames[4 + i].paste(img.perspective(points), pos, below=True)

    frames: List[Image] = [raw_frames[0].image]
    for i in range(4):
        frames.append(raw_frames[1].image)
        frames.append(raw_frames[2].image)
    frames.append(raw_frames[3].image)
    for i in range(6):
        frames.append(raw_frames[4].image)
        frames.append(raw_frames[5].image)

    return save_gif(frames, 0.1)


def rip(images: List[BuildImage]):
    img_dir = Path(__file__).parent / "rip"
    img = images[0].convert("RGBA").resize((150, 100), keep_ratio=True)
    img_left = img.crop((0, 0, 75, 100))
    img_right = img.crop((75, 0, 150, 100))
    params1 = [
        [(61, 196), ((140, 68), (0, 59), (33, 0), (165, 8))],
        [(63, 196), ((136, 68), (0, 59), (29, 0), (158, 13))],
        [(62, 195), ((137, 72), (0, 58), (27, 0), (167, 11))],
        [(95, 152), ((0, 8), (155, 0), (163, 107), (13, 112))],
        [(108, 129), ((0, 6), (128, 0), (136, 113), (10, 117))],
        [(84, 160), ((0, 6), (184, 0), (190, 90), (10, 97))],
    ]
    params2 = [
        (
            [(78, 158), ((0, 3), (86, 0), (97, 106), (16, 106))],
            [(195, 156), ((0, 4), (82, 0), (85, 106), (15, 110))],
        ),
        (
            [(89, 156), ((0, 0), (80, 0), (94, 100), (14, 100))],
            [(192, 151), ((0, 7), (79, 3), (82, 107), (11, 112))],
        ),
    ]
    raw_frames = [BuildImage.open(img_dir / f"{i}.png") for i in range(8)]
    for i in range(6):
        pos, points = params1[i]
        raw_frames[i].paste(img.perspective(points), pos, below=True)
    for i in range(2):
        (pos1, points1), (pos2, points2) = params2[i]
        raw_frames[i + 6].paste(img_left.perspective(points1), pos1, below=True)
        raw_frames[i + 6].paste(img_right.perspective(points2), pos2, below=True)

    new_frames: List[BuildImage] = []
    for i in range(3):
        new_frames += raw_frames[0:3]
    new_frames += raw_frames[3:]
    new_frames.append(raw_frames[-1])

    frames = [frame.image for frame in new_frames]
    return save_gif(frames, 0.1)


def rub(images: List[BuildImage]):
    img_dir = Path(__file__).parent / "rub"
    img = images[0].convert("RGBA").square().resize((180, 180))
    frames: List[Image] = []
    locs = [
        (178, 184, 78, 260),
        (178, 174, 84, 269),
        (178, 174, 84, 269),
        (178, 178, 84, 264),
    ]
    for i in range(4):
        frame = BuildImage.open(img_dir / f"{i}.png")
        w, h, x, y = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.1)


def strike(images: List[BuildImage]):
    img_dir = Path(__file__).parent / "strike"
    params = (
        (((0, 4), (153, 0), (138, 105), (0, 157)), (28, 47)),
        (((1, 13), (151, 0), (130, 104), (0, 156)), (28, 48)),
        (((9, 10), (156, 0), (152, 108), (0, 155)), (18, 51)),
        (((0, 21), (150, 0), (146, 115), (7, 145)), (17, 53)),
        (((0, 19), (156, 0), (199, 109), (31, 145)), (2, 62)),
        (((0, 28), (156, 0), (171, 115), (12, 154)), (16, 58)),
        (((0, 25), (157, 0), (169, 113), (13, 147)), (18, 63)),
    )

    def maker(i: int) -> Maker:
        def make(img: BuildImage) -> BuildImage:
            img = img.convert("RGBA").resize((200, 160), keep_ratio=True)
            points, pos = params[i]
            frame = BuildImage.open(img_dir / f"{i}.png")
            frame.paste(img.perspective(points), pos, below=True)
            return frame

        return make

    return save_gif([maker(i)(images[0]).image for i in range(7)], 0.05)
