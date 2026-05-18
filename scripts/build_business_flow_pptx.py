"""Build an editable swimlane business flowchart for CT-GraphMAS."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SPEC_PATH = DOCS / "ct_graphmas_business_flow_spec.json"
PPTX_PATH = DOCS / "CT-GraphMAS业务流程图.pptx"
LEGACY_PPTX_PATH = DOCS / "CT-GraphMAS系统流程图.pptx"
PPTX_ENGINE = Path("/Users/charleslu/.codex/skills/academic-ppt-figures/scripts/json_to_editable_pptx.py")


def shape(x: float, y: float, w: float, h: float, preset: str, text: str, fill: str = "#FFFFFF", stroke: str = "#111111") -> list[dict[str, Any]]:
    if preset == "flowChartDocument":
        return [
            {
                "type": "shape",
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "preset": "rect",
                "fill": fill,
                "stroke": stroke,
                "stroke_width": 1.0,
            },
            {
                "type": "polyline",
                "points": [
                    [x + 0.02, y + h - 0.10],
                    [x + w * 0.25, y + h - 0.02],
                    [x + w * 0.50, y + h - 0.14],
                    [x + w * 0.75, y + h - 0.02],
                    [x + w - 0.02, y + h - 0.10],
                ],
                "color": stroke,
                "width": 0.8,
                "end_arrow": False,
            },
            {
                "type": "text",
                "x": x + 0.04,
                "y": y + 0.05,
                "w": w - 0.08,
                "h": h - 0.16,
                "text": text,
                "font_size": 8.0,
                "align": "center",
                "valign": "middle",
                "color": "#111111",
                "margin": 0,
            },
        ]
    return [
        {
            "type": "shape",
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "preset": preset,
            "fill": fill,
            "stroke": stroke,
            "stroke_width": 1.0,
        },
        {
            "type": "text",
            "x": x + 0.04,
            "y": y + 0.06,
            "w": w - 0.08,
            "h": h - 0.08,
            "text": text,
            "font_size": 8.0,
            "align": "center",
            "valign": "middle",
            "color": "#111111",
            "margin": 0,
        },
    ]


def label(x: float, y: float, w: float, h: float, text: str, size: float = 9.0, bold: bool = False) -> dict[str, Any]:
    return {
        "type": "text",
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "text": text,
        "font_size": size,
        "bold": bold,
        "align": "center",
        "valign": "middle",
        "color": "#111111",
        "margin": 0,
    }


def line(x1: float, y1: float, x2: float, y2: float, arrow: bool = False) -> dict[str, Any]:
    return {
        "type": "arrow" if arrow else "line",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "color": "#111111",
        "width": 0.9,
    }


def poly(points: list[list[float]], arrow: bool = True) -> dict[str, Any]:
    return {
        "type": "polyline",
        "points": points,
        "color": "#111111",
        "width": 0.9,
        "end_arrow": arrow,
    }


def vertical_chain(x: float, ys: list[tuple[float, float]]) -> list[dict[str, Any]]:
    arrows: list[dict[str, Any]] = []
    for (_, bottom), (top, _) in zip(ys, ys[1:]):
        arrows.append(line(x, bottom, x, top, True))
    return arrows


def build_flow_slide() -> dict[str, Any]:
    x0, y0, w, h = 0.38, 0.42, 7.51, 10.85
    lane_w = w / 3
    admin_x, student_x, teacher_x = x0, x0 + lane_w, x0 + lane_w * 2
    body_y = y0 + 1.16
    objects: list[dict[str, Any]] = [
        {"type": "rect", "x": x0, "y": y0, "w": w, "h": h, "fill": "none", "stroke": "#111111", "stroke_width": 1.0},
        line(x0, y0 + 0.65, x0 + w, y0 + 0.65),
        line(x0, y0 + 1.16, x0 + w, y0 + 1.16),
        line(student_x, y0 + 0.65, student_x, y0 + h),
        line(teacher_x, y0 + 0.65, teacher_x, y0 + h),
        label(x0, y0 + 0.12, w, 0.38, "CT-GraphMAS 系统业务流程图", 12.0, True),
        label(admin_x, y0 + 0.78, lane_w, 0.24, "管理员", 10.0, True),
        label(student_x, y0 + 0.78, lane_w, 0.24, "学生", 10.0, True),
        label(teacher_x, y0 + 0.78, lane_w, 0.24, "教师", 10.0, True),
    ]

    aw = sw = tw = 1.58
    ax = admin_x + 0.46
    sx = student_x + 0.46
    tx = teacher_x + 0.46
    admin_steps = [
        (ax, 1.94, aw, 0.44, "roundRect", "开始", "#FFFFFF"),
        (ax, 2.72, aw, 0.46, "parallelogram", "输入管理员\n账号密码", "#FFFFFF"),
        (ax + 0.14, 3.50, aw - 0.28, 0.58, "diamond", "账号密码\n是否正确", "#FFFFFF"),
        (ax, 4.34, aw, 0.48, "rect", "维护用户角色\n与班级信息", "#FFFFFF"),
        (ax, 5.14, aw, 0.52, "rect", "配置 API\n与多智能体策略", "#FFFFFF"),
        (ax, 6.02, aw, 0.56, "rect", "维护 145 节点\n知识图谱", "#FFFFFF"),
        (ax, 6.92, aw, 0.52, "flowChartDocument", "系统配置\n与账号信息", "#FFFFFF"),
    ]
    for x, y, ww, hh, preset, text, fill in admin_steps:
        objects.extend(shape(x, y, ww, hh, preset, text, fill))
    objects.extend(vertical_chain(ax + aw / 2, [(1.94, 2.38), (2.72, 3.18), (3.50, 4.08), (4.34, 4.82), (5.14, 5.66), (6.02, 6.58), (6.92, 7.44)]))
    objects.append(poly([[ax + aw, 3.79], [ax + aw + 0.22, 3.79], [ax + aw + 0.22, 2.95], [ax + aw, 2.95]], True))
    objects.append(label(ax + aw + 0.16, 3.32, 0.22, 0.2, "否", 7.5))
    objects.append(label(ax + aw / 2 + 0.08, 4.12, 0.22, 0.2, "是", 7.5))

    student_steps = [
        (sx, 2.72, sw, 0.46, "parallelogram", "输入学生\n账号密码", "#FFFFFF"),
        (sx + 0.14, 3.50, sw - 0.28, 0.58, "diamond", "账号密码\n是否正确", "#FFFFFF"),
        (sx, 4.34, sw, 0.48, "rect", "登录进入\n学生端", "#FFFFFF"),
        (sx, 5.86, sw, 0.54, "flowChartDocument", "查看班级任务\n与学习画像", "#FFFFFF"),
        (sx + 0.12, 6.62, sw - 0.24, 0.62, "diamond", "选择日常通用\n或教学模式", "#FFFFFF"),
        (sx, 7.42, sw, 0.52, "parallelogram", "输入问题 / 代码\n或报错信息", "#FFFFFF"),
        (sx, 8.16, sw, 0.74, "rect", "系统自动处理\n意图映射 + 2-hop 图谱\nL1-L2-L3 + 门控", "#FFFFFF"),
        (sx, 9.18, sw, 0.58, "flowChartDocument", "查看反馈、相关知识\n与图谱节点", "#FFFFFF"),
        (sx + 0.14, 9.96, sw - 0.28, 0.58, "diamond", "问题是否\n已解决", "#FFFFFF"),
        (sx, 10.62, sw, 0.44, "rect", "完成任务\n或继续练习", "#FFFFFF"),
        (sx, 11.20, sw, 0.36, "roundRect", "结束", "#FFFFFF"),
    ]
    for x, y, ww, hh, preset, text, fill in student_steps:
        objects.extend(shape(x, y, ww, hh, preset, text, fill))
    objects.extend(vertical_chain(sx + sw / 2, [(2.72, 3.18), (3.50, 4.08), (4.34, 4.82), (5.86, 6.40), (6.62, 7.24), (7.42, 7.94), (8.16, 8.90), (9.18, 9.76), (9.96, 10.54), (10.62, 11.06), (11.20, 11.56)]))
    objects.append(poly([[sx + sw, 3.79], [sx + sw + 0.22, 3.79], [sx + sw + 0.22, 2.95], [sx + sw, 2.95]], True))
    objects.append(label(sx + sw + 0.16, 3.32, 0.22, 0.2, "否", 7.5))
    objects.append(label(sx + sw / 2 + 0.08, 4.12, 0.22, 0.2, "是", 7.5))
    objects.append(poly([[sx, 10.25], [sx - 0.20, 10.25], [sx - 0.20, 7.68], [sx, 7.68]], True))
    objects.append(label(sx - 0.34, 10.06, 0.20, 0.2, "否", 7.5))
    objects.append(label(sx + sw / 2 + 0.08, 10.58, 0.22, 0.2, "是", 7.5))

    teacher_steps = [
        (tx, 2.72, tw, 0.46, "parallelogram", "输入教师\n账号密码", "#FFFFFF"),
        (tx + 0.14, 3.50, tw - 0.28, 0.58, "diamond", "账号密码\n是否正确", "#FFFFFF"),
        (tx, 4.34, tw, 0.48, "rect", "登录进入\n教师端", "#FFFFFF"),
        (tx, 5.10, tw, 0.50, "rect", "分配班级任务\n与教学流程", "#FFFFFF"),
        (tx, 5.86, tw, 0.54, "flowChartDocument", "班级任务\n与课程资料", "#FFFFFF"),
        (tx, 6.66, tw, 0.50, "rect", "上传教学材料\n或课堂案例", "#FFFFFF"),
        (tx, 7.42, tw, 0.54, "flowChartDocument", "相关知识切分\nEmbedding 入库", "#FFFFFF"),
        (tx, 9.18, tw, 0.50, "flowChartDocument", "收到学生\n交互记录", "#FFFFFF"),
        (tx, 9.86, tw, 0.50, "rect", "查看学情图谱\n与门控日志", "#FFFFFF"),
        (tx, 10.58, tw, 0.50, "rect", "调整任务、知识库\n或提示词配置", "#FFFFFF"),
    ]
    for x, y, ww, hh, preset, text, fill in teacher_steps:
        objects.extend(shape(x, y, ww, hh, preset, text, fill))
    objects.extend(vertical_chain(tx + tw / 2, [(2.72, 3.18), (3.50, 4.08), (4.34, 4.82), (5.10, 5.60), (5.86, 6.40), (6.66, 7.16), (7.42, 7.96), (9.18, 9.68), (9.86, 10.36), (10.58, 11.08)]))
    objects.append(poly([[tx + tw, 3.79], [tx + tw + 0.20, 3.79], [tx + tw + 0.20, 2.95], [tx + tw, 2.95]], True))
    objects.append(label(tx + tw + 0.12, 3.32, 0.22, 0.2, "否", 7.5))
    objects.append(label(tx + tw / 2 + 0.08, 4.12, 0.22, 0.2, "是", 7.5))

    objects.append(line(tx, 6.13, sx + sw, 6.13, True))
    objects.append(label(5.08, 5.94, 0.54, 0.2, "发布", 7.0))
    objects.append(line(sx + sw, 9.47, tx, 9.43, True))
    objects.append(label(4.90, 9.25, 0.72, 0.2, "学习记录", 7.0))
    objects.append(poly([[tx + tw / 2, 11.08], [tx + tw / 2, 11.30], [5.58, 11.30], [5.58, 5.35], [tx, 5.35]], True))
    objects.append(label(6.12, 11.12, 0.44, 0.2, "迭代", 7.0))
    return {"background": "#FFFFFF", "objects": objects}


def build_legend_slide() -> dict[str, Any]:
    objects: list[dict[str, Any]] = [
        label(0.55, 0.55, 7.15, 0.38, "流程图各个符号的含义", 20.0, True),
        {"type": "rect", "x": 0.68, "y": 1.45, "w": 6.92, "h": 7.62, "fill": "none", "stroke": "#111111", "stroke_width": 1.0},
    ]
    x_name, x_symbol, x_note = 0.68, 2.48, 4.45
    w_name, w_symbol, w_note = 1.80, 1.97, 3.15
    y_top, row_h = 1.45, 0.82
    objects.extend([
        line(x_symbol, y_top, x_symbol, y_top + row_h * 7),
        line(x_note, y_top, x_note, y_top + row_h * 7),
    ])
    for i in range(1, 8):
        objects.append(line(0.68, y_top + row_h * i, 7.60, y_top + row_h * i))
    objects.extend([
        label(x_name, y_top + 0.22, w_name, 0.26, "名称", 10.0, True),
        label(x_symbol, y_top + 0.22, w_symbol, 0.26, "符号", 10.0, True),
        label(x_note, y_top + 0.22, w_note, 0.26, "解释", 10.0, True),
    ])
    rows = [
        ("起止框", "roundRect", "表示流程的开始或者结束"),
        ("处理框（矩形）", "rect", "代表一个特定的操作、步骤或处理动作"),
        ("判断框（菱形）", "diamond", "表示过程中的判断内容，用于决定流程走向"),
        ("输入/输出", "parallelogram", "表示输入数据、输出结果或用户提交的信息"),
        ("文档框", "flowChartDocument", "表示过程中的任务单、配置、相关知识或记录文件"),
        ("流程线", "arrow", "用于表示流程的具体走向"),
    ]
    for idx, (name, preset, note) in enumerate(rows, start=1):
        y = y_top + row_h * idx
        objects.append(label(x_name + 0.08, y + 0.24, w_name - 0.16, 0.26, name, 9.0, True))
        objects.append(label(x_note + 0.08, y + 0.24, w_note - 0.16, 0.26, note, 9.0, False))
        if preset == "arrow":
            objects.append(line(x_symbol + 0.55, y + 0.41, x_symbol + 1.40, y + 0.41, True))
        else:
            objects.extend(shape(x_symbol + 0.62, y + 0.20, 0.72, 0.42, preset, "", "#FFFFFF"))
    return {"background": "#FFFFFF", "objects": objects}


def build_spec() -> dict[str, Any]:
    return {
        "title": "CT-GraphMAS Business Swimlane Flowchart",
        "slide": {"width": 8.27, "height": 11.69, "units": "in"},
        "slides": [build_flow_slide(), build_legend_slide()],
    }


def load_engine():
    spec = importlib.util.spec_from_file_location("editable_pptx_engine", PPTX_ENGINE)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load PPTX engine: {PPTX_ENGINE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    original_apply = module._apply_object

    def apply_object(slide: Any, obj: dict[str, Any]) -> None:
        if obj.get("type") == "shape":
            slide.add_rect(
                float(obj["x"]),
                float(obj["y"]),
                float(obj["w"]),
                float(obj["h"]),
                fill=obj.get("fill", "#FFFFFF"),
                stroke=obj.get("stroke", "#111111"),
                stroke_width=float(obj.get("stroke_width", 1.0)),
                preset=obj.get("preset", "rect"),
                dash=obj.get("dash"),
            )
            return
        original_apply(slide, obj)

    module._apply_object = apply_object
    return module


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    spec = build_spec()
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    engine = load_engine()
    engine.write_pptx(spec, str(PPTX_PATH))
    engine.write_pptx(spec, str(LEGACY_PPTX_PATH))
    print(f"Wrote editable PPTX: {PPTX_PATH}")
    print(f"Wrote editable PPTX: {LEGACY_PPTX_PATH}")
    print(f"Wrote source spec: {SPEC_PATH}")


if __name__ == "__main__":
    main()
