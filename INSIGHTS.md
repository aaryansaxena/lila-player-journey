# Gameplay Insights from Player Journey Data

Analysis of 89,104 telemetry events across 5 days of LILA BLACK gameplay, using the Player Journey Visualization Tool.

---

## Insight 1: Human Players Dominate in Combat (3.5× Kill Ratio)

### What Caught Our Eye

Humans killed bots **2,415 times** while bots killed humans only **700 times**—a 3.5:1 ratio. This suggests human players significantly outskill the current bot AI in direct combat.

### Supporting Evidence

- **BotKill events** (humans killing bots): 2,415
- **BotKilled events** (bots killing humans): 700
- **Ratio**: 3.5x more successful human engagements
- **Data source**: Across all 5 days (Feb 10-14), all maps

Kill heatmaps (accessible via "Kill Zones" overlay) show human kills concentrated in high-value loot areas, suggesting deliberate tactical hunting. Bot kills, by contrast, scatter more randomly—indicating reactive rather than strategic behavior.

### Actionable Insights

**Metrics Affected**:
- Player retention (humans want challenge; current bots aren't challenging)
- Difficulty balance tuning
- Bot behavior evaluation

**Recommended Actions for Level Designers**:
1. **Increase bot skill** — Tighten aiming, improve positioning, add evasion behavior
2. **Create "bot champion" variants** — Elite bots in specific high-value zones to force engagement
3. **Redistribute loot near bot spawn areas** — Force humans to fight (not avoid) bots
4. **Review kill hotspots** — Are bots spawning in zones where humans can easily farm kills? (Suggests poor spawn placement)

**Why Level Designers Should Care**: If bots are too weak, skilled players bypass them entirely, reducing combat encounters and making traversal feel empty. This hurts emergent gameplay and pacing.

---

## Insight 2: Loot Spawns Are Effectively Random (No True Clustering)

### What Caught Our Eye

Loot events averaged **17.5 per match** with **no meaningful spatial clustering**. We expected high-value items to cluster in landmark rooms (e.g., "weapons cache," "vault"), but instead found loot spread uniformly across the map.

### Supporting Evidence

- **Total loot events**: 12,885
- **Avg loot per match**: 17.5 (ranging 1–68)
- **Spatial distribution**: Most-looted pixel location had only **13 events** (~0.1% of total)
- **Top 5 loot hotspots**: Account for only **0.3% of all loot pickups**
- **Conclusion**: Loot is NOT meaningfully clustered by location

Visualization via "Traffic" heatmap shows loot (green markers) scattered throughout traversal paths, not concentrated in specific rooms. This is different from most extraction games where high-tier loot is locked to specific bunkers.

### Actionable Insights

**Metrics Affected**:
- Player decision-making (when to risk engagement)
- Risk/reward balance
- Map flow incentives

**Recommended Actions for Level Designers**:
1. **Create loot zones** — Designate 3-4 "loot rooms" and concentrate spawns there
2. **Increase spawn density in high-risk areas** — Force players to choose between speed and reward
3. **Test in playtests** — If loot is intentionally random, validate that players still explore the full map (current tool shows they might be following efficient "loot corridors")
4. **Monitor "dead zones"** — Are players avoiding certain map sections because loot never spawns there?

**Why Level Designers Should Care**: Clustering loot creates emotional landmarks ("everyone knows where the weapons cache is") and drives emergent PvP hotspots. Random loot can feel aimless and reduce replayability.

---

## Insight 3: Storm Deaths Are Match Enders, Not Threats (Occur at Match End)

### What Caught Our Eye

Storm deaths (**39 events** across 5 days) happen almost exclusively at the **end of each match**—not during the mid-match chaos as a threat. This suggests the storm's purpose is to enforce extraction, not to create high-stakes survival moments.

### Supporting Evidence

- **Total storm death events**: 39 (across all matches)
- **Matches with storm deaths**: 39 (exactly 1 per match, or none)
- **Timing**: Storm deaths occur at **0.7–0.85s into matches** where match duration is typically **0.7–0.8s**
  - Match `c3a6fc96...`: storm death at 0.72s / 0.72s duration (100% into match)
  - Match `f2858ebc...`: storm death at 0.70s / 0.70s duration (100% into match)
  - Match `9d3b73ad...`: storm death at 0.85s / 0.85s duration (100% into match)
- **Pattern**: Storm deaths cluster at the **very end of telemetry**—suggesting they're logged as match-end events

Storm heatmap (via "Death Zones" overlay) shows storm kills in scattered locations across the map, not a advancing ring—they're residual deaths as players are still extracting.

### Actionable Insights

**Metrics Affected**:
- Tension curve (storm should create climactic moments mid-match, not just cleanup)
- Player survival strategy
- Risk-taking behavior

**Recommended Actions for Level Designers**:
1. **Adjust storm timing** — Advance the storm **earlier** (at 50% match time) to force mid-match repositioning
2. **Increase storm damage** — Make players panic and extract early, creating action-packed finales
3. **Add safe zones** — Designate extraction zones that are safe from storm; make reaching them a goal
4. **Telemetry tracking** — Add "storm damage taken" and "extraction time" metrics; verify current storm is creating tension
5. **Stress-test extraction zones** — Are all players clustering in one location? Storm can help balance player distribution

**Why Level Designers Should Care**: A well-tuned storm is the **pacing engine** of extraction shooters. If it only activates at the end, you lose half your design space for tension and strategy. Players should fear the storm, not ignore it.

---

## Summary

| Insight | Finding | Level Designer Action |
|---------|---------|----------------------|
| **1. Bot Weakness** | Humans kill bots 3.5× more often | Increase bot difficulty; create high-skill bot variants |
| **2. Loot Chaos** | Loot is uniformly distributed, not clustered | Create loot zones to drive emergent hotspots |
| **3. Storm Timing** | Storm activates at match end, not mid-game | Advance storm timer to create mid-match tension |

All three insights are **immediately actionable** and grounded in measurable data from the visualization tool. Use the heatmaps to spot-check these patterns in live matches.
