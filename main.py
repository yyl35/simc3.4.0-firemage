import random
import time
class FireMageSimulator:
    def __init__(self, spell_power, crit_chance, haste):
        self.spell_power = spell_power
        self.crit_chance = crit_chance
        self.haste = haste
        self.cast_sequence = []

        self.hot_streak = False
        self.consecutive_crits = 0
        self.living_bomb_countdown = 0
        self.living_bomb_dot_ticks_remaining = 0
        self.living_bomb_next_dot_tick = 0  # Represents the time until the next DOT tick.

        # Counters
        self.fireball_casts = 0
        self.fireball_crits = 0
        self.pyroblast_casts = 0
        self.pyroblast_crits = 0
        self.living_bomb_dot_casts = 0
        self.living_bomb_dot_crits = 0
        self.living_bomb_explosion_casts = 0
        self.living_bomb_explosion_crits = 0
        self.bloodlust_active = False
        self.bloodlust_duration = 0  # Track the duration left of the bloodlust effect

    def reset(self):
        """重置模拟器状态"""
        self.cast_sequence = []
        self.hot_streak = False
        self.consecutive_crits = 0
        self.living_bomb_countdown = 0
        self.living_bomb_dot_ticks_remaining = 0
        self.living_bomb_next_dot_tick = 0

        # 重置计数器
        self.fireball_casts = 0
        self.fireball_crits = 0
        self.pyroblast_casts = 0
        self.pyroblast_crits = 0
        self.living_bomb_dot_casts = 0
        self.living_bomb_dot_crits = 0
        self.living_bomb_explosion_casts = 0
        self.living_bomb_explosion_crits = 0

    def get_cast_time(self, base_cast_time):
        """ Calculate the cast time with haste, but consider the GCD cap. """

        # If bloodlust is active, account for its haste
        if self.bloodlust_active:
            cast_time = base_cast_time / (1 + self.haste)/1.3
        else:
            cast_time = base_cast_time / (1 + self.haste)

        return max(1, cast_time)

    def check_critical(self, damage, spell_type):
        crit_occurred = False
        if random.random() < self.crit_chance:
            crit_occurred = True
            damage *= 2.5445  # Assuming critical hits do 2.5445 times base damage.

            # Ensure only fireball and living_bomb_explosion crits count towards consecutive crits.
            if spell_type in ["fireball", "living_bomb_explosion"]:
                self.consecutive_crits += 1

            # Update specific crit counters
            if spell_type == "fireball":
                self.fireball_crits += 1
            elif spell_type == "pyroblast":
                self.pyroblast_crits += 1
            elif spell_type == "living_bomb_dot":
                self.living_bomb_dot_crits += 1
            elif spell_type == "living_bomb_explosion":
                self.living_bomb_explosion_crits += 1

            # Check for hot streak.
            if self.consecutive_crits >= 2:
                self.hot_streak = True

        return damage, crit_occurred

    def fireball_damage(self):
        self.fireball_casts += 1
        base_damage = 1125
        damage = (base_damage + self.spell_power*1.15)*1.06*1.12*1.13*1.03*1.13
        damage, crit_occurred = self.check_critical(damage, "fireball")

        # Reset consecutive crits if fireball did not crit
        if not crit_occurred:
            self.consecutive_crits = 0
            self.hot_streak = False

        return damage

    def pyroblast_damage(self):
        self.pyroblast_casts += 1
        base_damage = 1500
        damage = (base_damage + self.spell_power * 1.15*1.15)*1.12*1.13*1.03*1.13
        damage, crit_occurred= self.check_critical(damage, "pyroblast")

        # Reset the consecutive crits and hot streak after casting Pyroblast
        self.consecutive_crits = 0
        self.hot_streak = False

        return damage

    def living_bomb_dot(self):
        self.living_bomb_dot_casts += 1
        base_damage = 350
        damage = (base_damage + self.spell_power *0.2)*1.13*1.03*1.13
        damage, crit_occurred = self.check_critical(damage, "living_bomb_dot")
        return damage

    def living_bomb_explosion(self):
        self.living_bomb_explosion_casts += 1
        base_damage = 760
        damage = (base_damage + self.spell_power *0.4)*1.13*1.03*1.13
        damage, crit_occurred = self.check_critical(damage, "living_bomb_explosion")
        if not crit_occurred:
            self.consecutive_crits = 0
            self.hot_streak = False
        return damage

    # ... [在 FireMageSimulator 类中]

    def simulate_dps(self, loops=500):
        total_damage = 0
        time_elapsed = 0
        cast_time=0
        # Activate bloodlust at the start of the fight
        self.bloodlust_active = True
        self.bloodlust_duration = 45

        for _ in range(loops):
            if time_elapsed >= 200:
                break

            # Check and decrement bloodlust duration
            if self.bloodlust_active:
                self.bloodlust_duration -= cast_time
                if self.bloodlust_duration <= 0:
                    self.bloodlust_active = False

            if self.living_bomb_countdown <= 0:
                self.living_bomb_countdown = 12
                self.living_bomb_dot_ticks_remaining = 4
                self.living_bomb_next_dot_tick = 3
                cast_time = round(self.get_cast_time(1.5), 3)
                time_elapsed = round(time_elapsed + cast_time, 3)
                self.cast_sequence.append("Living Bomb" + str(cast_time) + ' ' + str(time_elapsed))

            elif self.hot_streak:
                total_damage += self.pyroblast_damage()
                cast_time = round(self.get_cast_time(1.5), 3)
                time_elapsed = round(time_elapsed + cast_time, 3)
                self.cast_sequence.append("Pyroblast " + str(cast_time) + ' ' + str(time_elapsed))

            else:
                total_damage += self.fireball_damage()
                cast_time = round(self.get_cast_time(2.85), 3)
                time_elapsed = round(time_elapsed + cast_time, 3)
                self.cast_sequence.append("Fireball" + str(cast_time) + ' ' + str(time_elapsed))

            if self.living_bomb_countdown > 0:
                self.living_bomb_countdown -= cast_time
                self.living_bomb_next_dot_tick -= cast_time

                while self.living_bomb_next_dot_tick <= 0 and self.living_bomb_dot_ticks_remaining > 0:
                    self.cast_sequence.append("Living Bomb DOT Tick")
                    total_damage += self.living_bomb_dot()
                    self.living_bomb_dot_ticks_remaining -= 1
                    self.living_bomb_next_dot_tick += 3

                if self.living_bomb_countdown <= 0:
                    self.cast_sequence.append("Living Bomb Explosion")
                    total_damage += self.living_bomb_explosion()

        return total_damage, time_elapsed

        # Reset the time elapsed for the next iteration

    def generate_report(self, time_elapsed, total_damage):
        report = f"Total Damage: {total_damage}\n"
        report += f"Duration: {time_elapsed:.2f} seconds\n"
        report += f"DPS: {total_damage / time_elapsed:.2f}\n\n"
       # report += f"Cast Sequence: {' -> '.join(self.cast_sequence)}\n\n"

        report += f"Fireball:\n"
        report += f"- Casts: {self.fireball_casts}\n"
        report += f"- Crit Chance: {self.fireball_crits / self.fireball_casts * 100:.2f}%\n\n" if self.fireball_casts > 0 else "- Crit Chance: 0.00%\n\n"

        report += f"Pyroblast:\n"
        report += f"- Casts: {self.pyroblast_casts}\n"
        report += f"- Crit Chance: {self.pyroblast_crits / self.pyroblast_casts * 100:.2f}%\n\n" if self.pyroblast_casts > 0 else "- Crit Chance: 0.00%\n\n"

        report += f"Living Bomb DOT:\n"
        report += f"- Casts: {self.living_bomb_dot_casts}\n"
        report += f"- Crit Chance: {self.living_bomb_dot_crits / self.living_bomb_dot_casts * 100:.2f}%\n\n" if self.living_bomb_dot_casts > 0 else "- Crit Chance: 0.00%\n\n"

        report += f"Living Bomb Explosion:\n"
        report += f"- Casts: {self.living_bomb_explosion_casts}\n"
        report += f"- Crit Chance: {self.living_bomb_explosion_crits / self.living_bomb_explosion_casts * 100:.2f}%" if self.living_bomb_explosion_casts > 0 else "- Crit Chance: 0.00%"

        return report

def compute_attribute_weight():
    """计算各属性权重"""
    weights = {}

    # 计算暴击权重
    mage = FireMageSimulator(spell_power=spell_power, crit_chance=0.2 + crit_value / 45.9 * 0.01,
                             haste=1.08*haste_value / 32.8 * 0.01)
    total_damage, time_elapsed = mage.simulate_dps(loops=150)
  #  print('base_dps',time_elapsed,len(mage.cast_sequence),mage.cast_sequence)
    base_dps = total_damage / time_elapsed
    mage_crit = FireMageSimulator(spell_power=spell_power, crit_chance=0.2 + (crit_value+100) / 45.9 * 0.01, haste=1.08*haste_value/32.8*0.01)
    total_damage_crit, time_elapsed_crit = mage_crit.simulate_dps(loops=150)

    crit_dps = total_damage_crit / time_elapsed_crit
 # 重置为原值
    weights["crit"] = (crit_dps - base_dps) / 100  # DPS每点增长

    mage_haste = FireMageSimulator(spell_power=spell_power, crit_chance=0.2 + crit_value / 45.9 * 0.01,
                                  haste=1.08*(haste_value+100) / 32.8 * 0.01)
    # 计算急速权重
    total_damage_haste, time_elapsed_haste = mage_haste.simulate_dps(loops=150)
  #  print('haste_dps',time_elapsed_haste,len(mage_haste.cast_sequence), mage_haste.cast_sequence)
    haste_dps = total_damage_haste / time_elapsed_haste

    weights["haste"] = (haste_dps - base_dps) / 100  # DPS每点增长
    # 计算法伤权重
    mage_spell = FireMageSimulator(spell_power=(spell_power+100), crit_chance=0.2 + crit_value / 45.9 * 0.01,
                                   haste= 1.08*haste_value/32.8*0.01)

    total_damage_spell, time_elapsed_spell = mage_spell.simulate_dps(loops=150)
    spell_dps = total_damage_spell / time_elapsed_spell

    weights["spell_power"] = (spell_dps - base_dps) / 100  # DPS每点增长

    return weights

def compute_average_attribute_weight():
    """计算各属性的平均权重，通过循环100次模拟得到"""
    total_weights = {"crit": 0, "haste": 0, "spell_power": 0}
    iterations = 5000

    for _ in range(iterations):
        weights = compute_attribute_weight()
        for key in weights:
            total_weights[key] += weights[key]

    # 求平均权重
    for key in total_weights:
        total_weights[key] /= iterations

    return total_weights

# Usage
crit_value = 2050
haste_value = 700
spell_power = 3600
mage = FireMageSimulator(spell_power=spell_power, crit_chance=0.2+crit_value/45.9*0.01, haste=1.08*haste_value/32.8*0.01)
total_damage, time_elapsed = mage.simulate_dps(loops=100)
print(mage.cast_sequence)
base_dps = total_damage / time_elapsed
print(mage.generate_report(time_elapsed, total_damage))

average_weights = compute_average_attribute_weight()

print(f"平均暴击权重：{average_weights['crit']:.2f} DPS/点")
print(f"平均急速权重：{average_weights['haste']:.2f} DPS/点")
print(f"平均法伤权重：{average_weights['spell_power']:.2f} DPS/点")

# 将权重转换为法伤
print(f"1 暴击 = {average_weights['crit'] / average_weights['spell_power']:.2f} 法伤")
print(f"1 急速 = {average_weights['haste'] / average_weights['spell_power']:.2f} 法伤")




