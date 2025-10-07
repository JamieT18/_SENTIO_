// Sample Cypress test for Sentio dashboard
it('loads dashboard', () => {
  cy.visit('/');
  cy.contains('Sentio');
});