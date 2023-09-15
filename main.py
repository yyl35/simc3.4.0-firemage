import random

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
        cast_time = base_cast_time / (1 + self.haste)
        return cast_time


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
        damage = (base_damage + self.spell_power)*2
        damage, crit_occurred = self.check_critical(damage, "fireball")

        # Reset consecutive crits if fireball did not crit
        if not crit_occurred:
            self.consecutive_crits = 0
            self.hot_streak = False

        return damage

    def pyroblast_damage(self):
        self.pyroblast_casts += 1
        base_damage = 1500
        damage = (base_damage + self.spell_power * 1.15)*2
        damage, _ = self.check_critical(damage, "pyroblast")

        # Reset the consecutive crits and hot streak after casting Pyroblast
        self.consecutive_crits = 0
        self.hot_streak = False

        return damage

    def living_bomb_dot(self):
        self.living_bomb_dot_casts += 1
        base_damage = 350
        damage = (base_damage + self.spell_power * 0.26)*2
        damage, _ = self.check_critical(damage, "living_bomb_dot")
        return damage

    def living_bomb_explosion(self):
        self.living_bomb_explosion_casts += 1
        base_damage = 760
        damage = (base_damage + self.spell_power * 1.05)*2
        damage, _ = self.check_critical(damage, "living_bomb_explosion")
        return damage

    # ... [在 FireMageSimulator 类中]

    def simulate_dps(self, loops=500):
        total_damage = 0
        time_elapsed = 0

        for _ in range(loops):
            cast_time = 0  # To keep track of the current cast time

            # If Hot Streak is active, cast Pyroblast
            if self.hot_streak:
                self.cast_sequence.append("Pyroblast")
                total_damage += self.pyroblast_damage()
                cast_time = self.get_cast_time(1.5)
                # Since it's an instant cast, we don't add to time_elapsed here.

            # If Living Bomb is not active, cast it
            elif self.living_bomb_countdown <= 0:
                self.cast_sequence.append("Living Bomb")
               # total_damage += self.living_bomb_dot()
                self.living_bomb_countdown = 12  # Set the Living Bomb duration
                self.living_bomb_dot_ticks_remaining = 4  # Assuming it ticks 4 times over 12 seconds
                self.living_bomb_next_dot_tick = 3  # First tick is after 3 seconds
                cast_time = self.get_cast_time(1.5) # Casting time for Living Bomb

            # Else, cast Fireball
            else:
                self.cast_sequence.append("Fireball")
                total_damage += self.fireball_damage()
                cast_time = self.get_cast_time(2.85)   # Casting time for fireball.

            # Handle Living Bomb DOT and explosion
            if self.living_bomb_countdown > 0:
                # Reduce the countdown by the cast time
                self.living_bomb_countdown -= cast_time
                self.living_bomb_next_dot_tick -= cast_time

                # Apply DOT tick if necessary
                while self.living_bomb_next_dot_tick <= 0 and self.living_bomb_dot_ticks_remaining > 0:
                    self.cast_sequence.append("Living Bomb DOT Tick")
                    total_damage += self.living_bomb_dot()
                    self.living_bomb_dot_ticks_remaining -= 1
                    self.living_bomb_next_dot_tick += 3  # Next tick after 3 seconds

                # If Living Bomb expires after the cast, explode and deal damage
                if self.living_bomb_countdown <= 0:
                    self.cast_sequence.append("Living Bomb Explosion")
                    total_damage += self.living_bomb_explosion()

            time_elapsed += cast_time

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
    mage = FireMageSimulator(spell_power=spell_power, crit_chance=0.3 + crit_value / 45.9 * 0.01,
                             haste=haste_value / 32.8 * 0.01)
    total_damage, time_elapsed = mage.simulate_dps(loops=500000)
    base_dps = total_damage / time_elapsed
    mage_crit = FireMageSimulator(spell_power=spell_power, crit_chance=0.3 + (crit_value+100) / 45.9 * 0.01, haste=haste_value/32.8*0.01)
    total_damage_crit, time_elapsed_crit = mage_crit.simulate_dps(loops=500000)


    crit_dps = total_damage_crit / time_elapsed_crit
 # 重置为原值
    weights["crit"] = (crit_dps - base_dps) / 100  # DPS每点增长

    mage_haste = FireMageSimulator(spell_power=spell_power, crit_chance=0.3 + crit_value  / 45.9 * 0.01,
                                  haste=(haste_value+100) / 32.8 * 0.01)
    # 计算急速权重



    total_damage_haste, time_elapsed_haste = mage_haste.simulate_dps(loops=500000)
    haste_dps = total_damage_haste / time_elapsed_haste

    weights["haste"] = (haste_dps - base_dps) / 100  # DPS每点增长

    # 计算法伤权重

    mage_spell = FireMageSimulator(spell_power=(spell_power+100), crit_chance=0.3 + crit_value / 45.9 * 0.01,
                                   haste= haste_value / 32.8 * 0.01)

    total_damage_spell, time_elapsed_spell = mage_spell.simulate_dps(loops=500000)
    spell_dps = total_damage_spell / time_elapsed_spell

    weights["spell_power"] = (spell_dps - base_dps) / 100  # DPS每点增长

    return weights

# Usage
crit_value = 2100
haste_value = 650
spell_power = 3700
mage = FireMageSimulator(spell_power=spell_power, crit_chance=0.3+crit_value/45.9*0.01, haste=haste_value/32.8*0.01)
total_damage, time_elapsed = mage.simulate_dps(loops=100)
base_dps = total_damage / time_elapsed
print(mage.generate_report(time_elapsed, total_damage))


weights = compute_attribute_weight()
print(f"暴击权重：{weights['crit']:.2f} DPS/点")
print(f"急速权重：{weights['haste']:.2f} DPS/点")
print(f"法伤权重：{weights['spell_power']:.2f} DPS/点")

# 将权重转换为法伤
print(f"1 暴击 = {weights['crit'] / weights['spell_power']:.2f} 法伤")
print(f"1 急速 = {weights['haste'] / weights['spell_power']:.2f} 法伤")
print(mage.cast_sequence)