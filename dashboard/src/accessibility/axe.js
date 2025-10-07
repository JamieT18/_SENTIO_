// axe-core accessibility audit stub
import axe from 'axe-core';
export function runAxeAudit() {
  axe.run(document, {}, (err, results) => {
    if (err) throw err;
    window.auditResults = results;
  });
}