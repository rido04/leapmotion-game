# Object Catcher Game - Setup Guide

## 📁 Folder Structure

```
assets/
└── object-catcher/
    ├── game_config.json          # Main configuration file
    ├── baskets/
    │   ├── basket_default.png
    │   ├── basket_adidas.png     # Brand specific (optional)
    │   └── basket_custom.png     # Custom brand (optional)
    │
    ├── good-items/
    │   ├── good_1.png            # Good items to catch
    │   ├── good_2.png
    │   ├── good_3.png
    │   ├── good_4.png
    │   └── good_5.png
    │
    ├── bad-items/
    │   ├── bad_1.png             # Items to avoid
    │   ├── bad_2.png
    │   └── bad_3.png
    │
    └── bonus-items/
        ├── bonus_1.png           # Special bonus items
        └── bonus_2.png
```

## 🎮 Quick Start

### Option 1: With Images (Recommended)

1. Create folder structure above
2. Place your PNG images in respective folders
3. Update `game_config.json` with image paths
4. Run the game!

### Option 2: Without Images (Fallback Graphics)

1. Just create `assets/object-catcher/game_config.json`
2. Leave image paths empty or remove them
3. Game will use beautiful fallback graphics automatically!

## ⚙️ Configuration Guide

### Basket Configuration

```json
"basket": {
  "image": "baskets/basket_default.png",  // Optional
  "width": 140,                            // Basket width
  "height": 70,                            // Basket height
  "color_fallback": [100, 150, 200]       // RGB color if no image
}
```

### Good Items Configuration

```json
"good_items": [
  {
    "image": "good-items/good_1.png",     // Optional
    "points": 10,                          // Points awarded
    "size": 50,                            // Object size in pixels
    "color_fallback": [100, 200, 100],    // RGB if no image
    "name": "Item A",                      // Display name
    "spawn_weight": 50                     // Higher = more common
  }
]
```

### Bad Items Configuration

```json
"bad_items": [
  {
    "image": "bad-items/bad_1.png",       // Optional
    "penalty": -1,                         // Lives lost when caught
    "size": 55,
    "color_fallback": [200, 50, 50],
    "name": "Bad Item",
    "spawn_weight": 100
  }
]
```

### Bonus Items Configuration

```json
"bonus_items": [
  {
    "image": "bonus-items/bonus_1.png",   // Optional
    "points": 50,                          // Big points!
    "size": 65,
    "color_fallback": [255, 215, 0],      // Gold color
    "name": "Bonus Star",
    "spawn_weight": 100
  }
]
```

### Difficulty Settings

```json
"difficulty": {
  "initial_spawn_rate": 1.5,    // Seconds between spawns (start)
  "min_spawn_rate": 0.6,        // Fastest spawn rate
  "initial_fall_speed": 3.0,    // Starting fall speed
  "speed_increment": 0.2,       // Speed increase per level
  "bad_item_chance": 0.15,      // 15% chance bad item spawns
  "bonus_item_chance": 0.05     // 5% chance bonus item spawns
}
```

### Game Settings

```json
"game_settings": {
  "game_duration": 60,          // Game length in seconds
  "starting_lives": 3,          // Starting lives
  "miss_penalty": true,         // Lose life if miss good item?
  "combo_enabled": true         // Enable combo system?
}
```

## 🎨 Customization for Different Brands

### Example: Adidas Theme

```json
{
  "game_title": "Adidas Shoe Catcher",
  "basket": {
    "image": "baskets/adidas_shoebox.png",
    "color_fallback": [0, 0, 0]
  },
  "good_items": [
    {
      "image": "good-items/ultraboost.png",
      "points": 15,
      "size": 60,
      "name": "Ultraboost"
    },
    {
      "image": "good-items/nmd.png",
      "points": 20,
      "size": 65,
      "name": "NMD"
    }
  ],
  "bad_items": [
    {
      "image": "bad-items/competitor_shoe.png",
      "penalty": -1,
      "size": 60,
      "name": "Wrong Brand"
    }
  ]
}
```

### Example: Generic Food Theme

```json
{
  "game_title": "Food Catcher",
  "basket": {
    "color_fallback": [139, 69, 19] // Brown basket
  },
  "good_items": [
    {
      "points": 10,
      "size": 50,
      "color_fallback": [255, 0, 0], // Red apple
      "name": "Apple"
    },
    {
      "points": 15,
      "size": 55,
      "color_fallback": [255, 165, 0], // Orange
      "name": "Orange"
    }
  ],
  "bad_items": [
    {
      "penalty": -1,
      "size": 50,
      "color_fallback": [100, 100, 100], // Gray rock
      "name": "Rock"
    }
  ]
}
```

## 🎯 Gameplay Features

### Controls

- **Mouse**: Move mouse horizontally to control basket
- **Hand Tracking**: Move hand left/right to control basket
- **Pinch Gesture**: Interact with UI buttons

### Scoring System

- Catch good items: +10 to +30 points (configurable)
- Catch bonus items: +50 points (configurable)
- Combo multiplier: Catch items consecutively for bonus!
- Miss penalty: Lose 1 life per missed good item (configurable)
- Catch bad item: Lose 1 life (configurable)

### Combo System

- Catch 2+ items in a row: Combo active!
- Combo bonus: Extra points = (item_points × combo_count) / 2
- Combo breaks when: Miss an item or catch bad item
- Max combo tracked and shown at game over

### Progressive Difficulty

- Spawn rate increases (faster spawning)
- Fall speed increases (objects fall faster)
- More bad items appear over time

## 🔧 Troubleshooting

### Images not showing?

- Check file paths in `game_config.json`
- Make sure PNG files are in correct folders
- Fallback graphics will show if images missing (this is OK!)

### Game too easy/hard?

- Adjust `initial_spawn_rate` (higher = easier)
- Adjust `initial_fall_speed` (lower = easier)
- Adjust `starting_lives` (more = easier)
- Change `bad_item_chance` (lower = easier)

### Want more items?

- Add more entries to `good_items`, `bad_items`, or `bonus_items`
- Each entry can have different points, sizes, and weights
- `spawn_weight` determines rarity (higher = more common)

## 📊 Tips for Best Experience

1. **Image Size**: Use PNG images around 200x200px for best quality
2. **Transparency**: Use PNG with transparency for cleaner look
3. **Color Contrast**: Use bright colors for good items, dark for bad
4. **Spawn Weights**: Rare items should have lower spawn_weight
5. **Testing**: Start with 3 lives and 60 seconds for balanced gameplay

## 🚀 Next Steps

1. Create your assets folder structure
2. Copy `game_config.json` to `assets/object-catcher/`
3. (Optional) Add your PNG images
4. Test the game!
5. Adjust config values based on playtesting

---

**Note**: The game works perfectly WITHOUT any images! Fallback graphics are professionally designed and look great. Images are purely optional for branding purposes.
