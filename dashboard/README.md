# Sentio Trading Dashboard

A modern, responsive React dashboard for the Sentio trading platform.

## Features

### Performance Overview
- **Portfolio Value**: Real-time portfolio valuation with percentage change
- **Daily P&L**: Profit and Loss tracking for the current day
- **Win Rate**: Trading success rate with wins/losses breakdown
- **Total Trades**: Complete trade count with open positions indicator

### Trade Signals
- Live trading signals for multiple symbols
- Signal type (BUY/SELL/HOLD) with color-coded badges
- Confidence scores for each signal
- Consensus strength metrics

### Earnings Summary
- Comprehensive portfolio value tracking
- Total return with percentage gains
- Daily profit/loss calculations
- Profit sharing information (for premium tiers)

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

```bash
cd dashboard
npm install
```

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

## API Integration

The dashboard connects to the Sentio backend API endpoints:

- `/api/v1/dashboard/performance-cards` - Performance metrics cards
- `/api/v1/dashboard/trade-signals` - Trading signals
- `/api/v1/dashboard/earnings` - Earnings summary

### Configuration

Set the API URL via environment variable:

```bash
REACT_APP_API_URL=http://localhost:8000
```

Or create a `.env` file in the dashboard directory:

```
REACT_APP_API_URL=http://localhost:8000
```

## Features

### Offline Mode
The dashboard gracefully handles API failures by displaying demo data, allowing users to preview the interface even when the backend is unavailable.

### Responsive Design
Optimized for desktop, tablet, and mobile devices with a modern gradient design and smooth animations.

### Real-time Updates
Click the "Refresh Data" button to fetch the latest trading metrics from the API.

## Technology Stack

- **React 19** - UI framework
- **React Hooks** - State management
- **CSS3** - Modern styling with gradients and animations
- **Jest & React Testing Library** - Testing framework

## Improvements Made

1. **Dynamic Data Loading**: Replaced static content with API-driven data
2. **Performance Cards**: Visual cards displaying key trading metrics
3. **Trade Signals Table**: Interactive table showing current trading signals
4. **Earnings Widget**: Comprehensive earnings and profit tracking
5. **Modern UI/UX**: Gradient backgrounds, smooth animations, and responsive design
6. **Error Handling**: Graceful degradation with demo data when API is unavailable
7. **Test Coverage**: Comprehensive test suite for all major features

## Future Enhancements

- Real-time WebSocket updates for live data
- Charts and graphs for historical performance
- Trade journal integration
- AI-powered insights panel
- Advanced filtering and search
- Dark mode support

---

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
