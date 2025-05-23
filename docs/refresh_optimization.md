# E-Ink Refresh Optimization Guide

## Understanding E-Ink Refresh Behavior

### Why E-Ink Flashes

E-ink displays flash during updates due to the fundamental technology:
- Particles must be electrically moved between front and back
- Multiple voltage cycles ensure proper particle placement
- Color displays require coordinating multiple particle types

### Refresh Types

1. **Full Refresh (Global Update)**
   - Entire screen flashes black/white/black
   - Takes 15-35 seconds on color displays
   - Provides best image quality
   - Eliminates ghosting

2. **Partial Refresh (Partial Update)**
   - Only updates changed areas
   - Faster (~2-3 seconds)
   - Can cause ghosting over time
   - Not supported on all displays (especially color)

## Optimization Strategies

### 1. Reduce Update Frequency

```python
# In config/config.json
{
  "display": {
    "rotation_interval_minutes": 120  // Increase from 60 to 120
  }
}
```

### 2. Use Transitions Wisely

**Avoid:**
- Frequent mode changes (photo → clock → photo)
- Unnecessary clears between similar images

**Prefer:**
- Staying in one mode for extended periods
- Grouping similar content together

### 3. Optimize Image Content

**For Minimal Flashing:**
- High contrast images work better
- Simple graphics over complex photos
- Images with large areas of solid color
- Avoid gradients and fine details

### 4. Hardware Considerations

**Cannot Be Changed:**
- ACeP 7-color displays always do full refresh
- Refresh time is fixed by hardware (~35 seconds)
- Flashing pattern is determined by driver IC

**Can Be Optimized:**
- Image preprocessing (our current approach)
- Update scheduling
- Content selection

## Specific to 7.3" ACeP Display

This display has these characteristics:
- **No partial refresh support** - Every update is a full refresh
- **35-second refresh cycle** - Cannot be reduced
- **7-color limitation** - More complex than B&W
- **Temperature sensitive** - Slower in cold conditions

## Alternative Approaches

If flashing is problematic, consider:

1. **Different Display Type**
   - B&W e-ink: Faster refresh, supports partial updates
   - Grayscale e-ink: Middle ground
   - LCD/OLED: No flash but requires constant power

2. **Usage Pattern Changes**
   - Set as "always showing one image" (no rotation)
   - Update only at specific times (e.g., once daily)
   - Use for static information displays

3. **Content Optimization**
   - Use specially designed "e-ink friendly" images
   - Create content that works with the 7-color palette
   - Design around the refresh limitations

## Best Practices for Your Setup

1. **Increase rotation interval** to 2-4 hours
2. **Disable clock mode** (requires frequent updates)
3. **Use high-contrast photos** that look good with 7 colors
4. **Avoid frequent manual updates**
5. **Let the display "rest"** between updates

## Technical Reality

The 35-second dramatic flashing is simply how ACeP color e-ink works. It's the trade-off for:
- Zero power consumption when static
- Excellent daylight visibility  
- No backlight needed
- Paper-like appearance

This is why e-ink is used for e-readers (infrequent page turns) rather than video displays.