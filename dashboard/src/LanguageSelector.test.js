import { render, screen, fireEvent } from '@testing-library/react';
import LanguageSelector from './LanguageSelector';
import './i18n';

test('renders language selector with all language options', () => {
  render(<LanguageSelector />);
  
  const selector = screen.getByLabelText(/language/i);
  expect(selector).toBeInTheDocument();
  
  // Check that all language options are available
  const options = screen.getAllByRole('option');
  expect(options).toHaveLength(5);
  expect(options[0]).toHaveValue('en');
  expect(options[1]).toHaveValue('es');
  expect(options[2]).toHaveValue('fr');
  expect(options[3]).toHaveValue('de');
  expect(options[4]).toHaveValue('zh');
});

test('allows changing language', () => {
  render(<LanguageSelector />);
  
  const selector = screen.getByLabelText(/language/i);
  
  // Change to Spanish
  fireEvent.change(selector, { target: { value: 'es' } });
  expect(selector.value).toBe('es');
  
  // Change to French
  fireEvent.change(selector, { target: { value: 'fr' } });
  expect(selector.value).toBe('fr');
});
