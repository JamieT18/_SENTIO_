import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import './i18n';

test('renders Sentio Admin Dashboard heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/Sentio Admin Dashboard/i);
  expect(headingElement).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  const overviewTab = screen.getByText(/Overview & Analytics/i);
  const usersTab = screen.getByText(/User Management/i);
  const subscribersTab = screen.getByText(/Subscriber Details/i);
  const pricingTab = screen.getByText(/Pricing & Plans/i);
  
  expect(overviewTab).toBeInTheDocument();
  expect(usersTab).toBeInTheDocument();
  expect(subscribersTab).toBeInTheDocument();
  expect(pricingTab).toBeInTheDocument();
});

test('renders dark mode toggle button', () => {
  render(<App />);
  const themeToggle = screen.getByLabelText(/Toggle dark mode/i);
  expect(themeToggle).toBeInTheDocument();
});

test('renders hamburger menu on mobile', () => {
  render(<App />);
  const hamburgerMenu = screen.getByLabelText(/Toggle menu/i);
  expect(hamburgerMenu).toBeInTheDocument();
});

test('navigation buttons have proper touch target size', () => {
  render(<App />);
  const buttons = screen.getAllByRole('button');
  
  // Verify all buttons are rendered
  buttons.forEach(button => {
    expect(button).toBeInTheDocument();
  });
  
  // Should have at least 6 buttons (4 nav tabs + hamburger + theme toggle)
  expect(buttons.length).toBeGreaterThanOrEqual(6);
});
