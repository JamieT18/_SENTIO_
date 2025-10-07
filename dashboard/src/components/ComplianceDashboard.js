import React, { useState, useEffect } from 'react';
function ComplianceDashboard() {
  const [reports, setReports] = useState([]);
  useEffect(() => {
    // Stub: Replace with actual API call
    setReports([
      { trade_id: 'T123', compliant: true, issues: [] },
      { trade_id: 'T124', compliant: false, issues: ['Missing KYC'] },
    ]);
  }, []);
  return (
    <div className="compliance-dashboard">
      <h3>Compliance Reports</h3>
      <table>
        <thead>
          <tr>
            <th>Trade ID</th>
            <th>Compliant</th>
            <th>Issues</th>
          </tr>
        </thead>
        <tbody>
          {reports.map(r => (
            <tr key={r.trade_id}>
              <td>{r.trade_id}</td>
              <td>{r.compliant ? 'Yes' : 'No'}</td>
              <td>{r.issues.length ? r.issues.join(', ') : 'None'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export default ComplianceDashboard;
