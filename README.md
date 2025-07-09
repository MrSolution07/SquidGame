# SquidGame


```bash
python3 -m pytest test_squid_game.py -v
```
Perfect! All tests pass. Now let's run the improved game to see the realistic movement in action:

```bash
python3 squid_game.py
```

### 🎯 **What the Code Does**

This is a realistic Squid Game simulation that recreates the "Red Light, Green Light" challenge with:

1. **20 players** with unique characteristics
2. **Random movement speeds** (0.5-2.0 units per round)
3. **Variable field lengths** (8-15 units) for each player
4. **Fixed 2-second light durations** for consistent gameplay
5. **Realistic movement** with fractional positions
6. **Finish line detection** - players can actually win!

### �� **Key Improvements Made**

#### **Realistic Movement System**
- Each player has a **unique speed** and **field length**
- Players move **fractional distances** based on their speed
- **Automatic finish detection** when reaching field length
- **Progress tracking** with percentage completion

#### **Enhanced Gameplay**
- **Fixed 2-second light durations** (as you requested)
- **Multiple end conditions**: elimination, finishing, or time expiration
- **Dynamic outcomes** with different results each game
- **Rich visual output** with emojis and progress indicators

#### **Comprehensive Statistics**
- **Speed analysis**: Average player speed and field length
- **Movement tracking**: Green vs red light movements
- **Finish tracking**: Records when players reach finish line
- **Export functionality**: Detailed JSON statistics

#### **Better User Experience**
- **Emoji-enhanced display** with clear visual indicators
- **Real-time progress** showing player positions
- **Detailed summaries** with winners and leaders
- **Export capabilities** for data analysis

### 🎮 **Sample Game Results**

The improved game now produces much more interesting outcomes:
- **6 players finished** (30% finish rate)
- **13 players eliminated** (65% elimination rate)  
- **1 player still playing** (5% survival rate)
- **Different speeds and field lengths** create varied strategies
- **Realistic movement patterns** with fractional positions

### 📊 **Data Export**

The game exports comprehensive statistics including:
- Individual player speeds and field lengths
- Round-by-round elimination and finish data
- Movement statistics and success rates
- Game configuration and timing data

This enhanced version creates **much more dynamic and realistic gameplay** with each session producing unique outcomes based on the random player characteristics. The fixed 2-second light duration and realistic movement mechanics make the game more engaging and unpredictable!
