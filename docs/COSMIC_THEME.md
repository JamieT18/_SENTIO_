# Cosmic Theme Color Palette

This document defines the cosmic color palette applied to the Sentio 2.0 dashboard for a consistent, branded look.

## Color Palette

### Primary Colors
- **Deep Space Blue**: `#0f1729` - Primary background color for navigation and cards
- **Dark Space**: `#0a0e1a` - Main application background
- **Secondary Dark**: `#1a2332` - Secondary background for gradients

### Accent Colors
- **Cosmic Purple**: `#533483` - Secondary accent for gradients and emphasis
- **Nebula Blue**: `#1a4d7e` - Interactive elements (hover states, active tabs)
- **Stellar Cyan**: `#4fd1c5` - Primary accent for highlights, borders, and interactive elements

### Text Colors
- **Light Gray**: `#e2e8f0` - Primary text and headings
- **Muted Gray**: `#94a3b8` - Secondary text and labels

### Status Colors
- **Success Green**: `#68d391` - Active status, success messages
- **Warning Orange**: `#ed8936` - Trial status, warnings
- **Error Red**: `#fc8181` - Error states, canceled/expired status

### Tier Badge Colors
- **Free Tier**: `rgba(148, 163, 184, 0.2)` background, `#94a3b8` text
- **Basic Tier**: `rgba(79, 209, 197, 0.2)` background, `#4fd1c5` text
- **Professional Tier**: `rgba(83, 52, 131, 0.3)` background, `#9f7aea` text
- **Enterprise Tier**: `rgba(26, 77, 126, 0.3)` background, `#63b3ed` text

## Usage

### Gradients
- **Header Gradient**: `linear-gradient(135deg, #0f1729 0%, #533483 100%)`
- **Card Gradient**: `linear-gradient(135deg, #0f1729 0%, #1a2332 100%)`
- **Button Gradient**: `linear-gradient(135deg, #1a4d7e 0%, #533483 100%)`
- **Table Header Gradient**: `linear-gradient(135deg, #1a4d7e 0%, #533483 100%)`

### Shadows and Glows
- **Card Shadow**: `0 4px 6px rgba(79, 209, 197, 0.1)` with `1px solid rgba(79, 209, 197, 0.2)` border
- **Hover Shadow**: `0 6px 12px rgba(79, 209, 197, 0.3)`
- **Header Glow**: `0 4px 20px rgba(79, 209, 197, 0.3)`
- **Button Glow**: `0 2px 8px rgba(79, 209, 197, 0.3)` (normal), `0 4px 12px rgba(79, 209, 197, 0.5)` (hover)

### Transparency
Most cosmic elements use semi-transparent colors to create depth:
- Background overlays: `rgba(26, 77, 126, 0.3)`
- Input fields: `rgba(15, 23, 41, 0.5)`
- Borders: `rgba(79, 209, 197, 0.2)` to `rgba(79, 209, 197, 0.3)`

## Files Modified

1. **dashboard/src/App.css** - Main application styles with cosmic theme
2. **dashboard/src/index.css** - Body background and base text colors
3. **dashboard/public/index.html** - Meta theme-color tag

## Design Principles

1. **Dark Background**: Deep space colors create an immersive, professional environment
2. **Cyan Accents**: Stellar cyan provides high contrast for interactive elements
3. **Gradient Depth**: Subtle gradients add visual interest without overwhelming
4. **Glow Effects**: Cyan glows on shadows create a futuristic, cosmic feel
5. **Semi-transparency**: Layered transparency creates depth and sophistication
6. **Consistent Spacing**: Maintained all original spacing and layout structure

## Accessibility

- Text contrast ratios maintained for readability
- Lighter text (`#e2e8f0`) on dark backgrounds ensures WCAG AA compliance
- Interactive elements have clear visual states (hover, active, focus)
- Cyan accent color (`#4fd1c5`) provides strong contrast against dark backgrounds

## Future Enhancements

Potential additions to the cosmic theme:
- Star field background animation
- Gradient animations on hover
- Particle effects for loading states
- Additional cosmic illustrations or icons
- Dark/light mode toggle (space/day theme)
