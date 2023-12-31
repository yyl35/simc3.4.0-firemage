﻿# FireMageSimulator

这是一个模拟法师在 World of Warcraft3.40版本 中 DPS 输出的程序。程序会计算火球、炎爆、活体炸弹的伤害，并模拟连击点、暴击、急速等属性的权重。

## 主要功能：

- 计算火法师每种技能的基础伤害及其暴击伤害。
- 追踪热 streak 与活体炸弹的持续时间。
- 模拟一个火法师在战斗中的 DPS 输出。
- 生成战斗报告，包括每种技能的次数、暴击率等。
- 计算属性权重。

## 代码概述

### `FireMageSimulator` 类

- **属性**：
  - spell_power, crit_chance, haste: 法师的法伤、暴击率和急速。
  - 其他属性如 cast_sequence, hot_streak, consecutive_crits 等用于追踪战斗状态。
  
- **主要方法**：
  - `reset()`: 重置模拟器状态。
  - `get_cast_time()`: 计算技能施法时间。
  - `check_critical()`: 判断技能是否触发暴击。
  - 技能伤害方法：如 `fireball_damage()`, `pyroblast_damage()`, `living_bomb_dot()`, `living_bomb_explosion()` 等。
  - `simulate_dps()`: 模拟火法师的 DPS 输出。
  - `generate_report()`: 生成战斗报告。

### `compute_attribute_weight` 函数

该函数计算暴击、急速和法伤的权重。

## 使用方法：

```python
crit_value = 2100
haste_value = 650
spell_power = 3700
mage = FireMageSimulator(spell_power=spell_power, crit_chance=0.3+crit_value/45.9*0.01, haste=haste_value/32.8*0.01)
total_damage, time_elapsed = mage.simulate_dps(loops=100)
print(mage.generate_report(time_elapsed, total_damage))
```

## 输出样例：

```
Total Damage: 205000
Duration: 285.00 seconds
DPS: 720.00

Fireball:
- Casts: 50
- Crit Chance: 30.00%

Pyroblast:
- Casts: 25
- Crit Chance: 25.00%

Living Bomb DOT:
- Casts: 25
- Crit Chance: 25.00%

Living Bomb Explosion:
- Casts: 25
- Crit Chance: 25.00%
```

---

