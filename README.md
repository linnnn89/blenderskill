# Blender Skill Handbook / Blender 技能生产指南

[English](#english) | [中文说明](#中文说明)

---

<a name="english"></a>
## English

### Overview
**blender-skill** is a comprehensive 3D production handbook and router designed for Blender, containing **123 specialized manuals across 10 core domain groups**. It acts as an expert bridge for AI assistants and creators to perform end-to-end 3D creation, modification, lighting, animation, simulation, rendering, and export tasks in Blender.

### Core Structure

```text
blender-skill/
├── SKILL.md                 # Level-0 Entry router and global always-on rules
├── 01-orchestration/        # Multi-step workflows, precedence rules, execution coordination
├── 02-modeling/             # Geometry, hard-surface, character, creature, procedural, sculpting
├── 03-surfacing/            # Materials, look-dev, PBR textures, UV mapping, decals
├── 04-imaging/              # Lighting schemes, camera composition, Cycles/EEVEE, compositing
├── 05-motion/               # Keyframe animation, rigging & armatures, cloth/physics, VFX
├── 06-scene/                # Scene assembly, collection hierarchies, set dressing & props
├── 07-delivery/             # Multi-engine export (glTF, FBX, USD, OBJ, STL), LODs & optimization
├── 08-reference-locked/     # 1:1 Reference matching, blueprint alignment, dimension verification
├── 09-quality-gates/        # Final asset and animation QA validation checklists
├── 10-art-direction/        # Style archetypes (anime, stylized, voxel, sci-fi, realistic)
├── references/              # Shared dimension references, naming rules, error recovery, MCP specs
├── scripts/                 # Utility Python scripts (world reset, camera setup, version check)
├── assets/                  # Visual validation renders and evaluation assets
└── evals/                   # Benchmark test cases
```

### How to Use

1. **Navigation (3 Levels)**:
   - **Level 0 (`SKILL.md`)**: Main entry router and scope-preserving rules.
   - **Level 1 (`<group>/INDEX.md`)**: Group index mapping user requests to specific manuals.
   - **Level 2 (`<group>/<skill>/MANUAL.md`)**: Step-by-step instructions for concrete tasks.
2. **MCP Integration**:
   - Best paired with Blender MCP servers (such as `ahujasid/blender-mcp`) to execute Python code, inspect scene data, control viewports, and manipulate Blender programmatically.

---

<a name="中文说明"></a>
## 中文说明

### 简介
**blender-skill** 是一套面向 Blender 的全面 3D 制作技能指南与路由器，包含 **10 大核心领域分组、共 123 本专业手册**。无论是 AI 编程助手还是 3D 创作者，均可借助该指南完成从建模、材质着色、灯光摄影机、骨骼动画、特效物理、场景组装到多引擎导出的全流程工作。

### 目录与模块划分

```text
blender-skill/
├── SKILL.md                 # 0 级入口：路由分发中心与全局必备规则
├── 01-orchestration/        # 复杂工序编排、多技能协作与失败回退机制
├── 02-modeling/             # 几何体造型：硬表面、角色、生物、程序化生成与雕刻
├── 03-surfacing/            # 材质系统：Look-dev、PBR 贴图、UV 展开、图集与贴花
├── 04-imaging/              # 影像系统：灯光布光、镜头构图、渲染引擎设置与后期节点
├── 05-motion/               # 动态系统：关键帧动画、骨骼绑定、布料/刚体解算与粒子特效
├── 06-scene/                # 场景装配：集合管理、大场景搭建、道具陈设
├── 07-delivery/             # 交付导出：面向 Unity/Unreal/Godot 的多格式优化与 LOD
├── 08-reference-locked/     # 参考锁定：1:1 像素级匹配设计图、线框及尺寸校验
├── 09-quality-gates/        # 交付门禁：模型规格、法线、材质与动画最终审核清单
├── 10-art-direction/        # 风格指引：二次元、赛博朋克、复古、低模、像素与体素等风格
├── references/              # 共享基准：常用尺寸表、命名规范、故障排查与 MCP 协议规范
├── scripts/                 # 辅助脚本：世界环境重置、摄像机创建、版本探针等常用脚本
├── assets/                  # 验证产物：视觉回归验证渲染图与历史样例
└── evals/                   # 自动化测评集
```

### 使用方式

1. **三级导航规则**：
   - **第 0 级（`SKILL.md`）**：全局入口，负责根据用户意图进行路由匹配并执行前置规则（如检查并保留现有场景；世界重置仅在需要时显式调用）。
   - **第 1 级（`<group>/INDEX.md`）**：进入对应的领域模块，查看手册索引与触发条件。
   - **第 2 级（`<group>/<skill>/MANUAL.md`）**：按需载入具体手册，执行对应步骤。
2. **配合 MCP 工具**：
   - 配合 Blender MCP（如 `ahujasid/blender-mcp` 或 `blender-finisher`），可在 AI 环境中直接执行 Blender Python 脚本、抓取视口渲染与检查场景拓扑。

### 维护与验证 / Maintenance and validation

在手册根目录运行（无需 `manifest.json`）：

```text
python 01-orchestration/blender-skill-harmonizer/scripts/skill_graph_audit.py --skill-root .
python -m unittest discover -s tests -v
```

结构检查覆盖领域索引、手册名称、显式资源引用、Python 语法与 eval JSON；错误返回非零退出码，缺少历史示例图片单独报告为警告。回归用例使用临时文件；Blender 集成用例通过独立后台进程、出厂配置和临时场景检查辅助脚本及指定对象的 GLB 导出，不连接已打开的场景。可用 `BLENDER_EXECUTABLE` 指定程序路径；未找到 Blender 时该用例会跳过。它不覆盖完整渲染、动画或所有引擎的验收。

`reset_world.py`、`apply_transforms.py`、`cleanup_unused.py` 加载时仅定义函数。旧的“执行整个脚本即修改场景”调用必须改成加载后显式调用：变换需要对象名称和操作选项；清理需要候选数据块并默认预览。运行示例前，将 `${COMMANDCODE_SKILL_DIR}` 替换为当前安装目录的绝对路径。

恢复制作失败默认只修复作品；修改技能、持久化经验、发布提交分别按明确请求执行。`release_readiness_check.py` 仅适用于上游插件仓库布局，不是当前独立手册的制作门禁。
