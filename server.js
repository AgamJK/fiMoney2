const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.json());
app.use(cors()); // Enable CORS for all routes
app.use(express.static(path.join(__dirname, 'frontend'))); // Serve static files

// Mock endpoints

// Expanded mock data
app.get('/mcp/get_assets', (req, res) => {
  res.json({
    assets: [
      { type: 'bank', name: 'HDFC Savings', value: 500000, currency: 'INR' },
      { type: 'bank', name: 'ICICI Current', value: 120000, currency: 'INR' },
      { type: 'mutual_fund', name: 'Axis Bluechip', value: 150000, currency: 'INR' },
      { type: 'stock', name: 'Reliance', value: 80000, currency: 'INR' },
      { type: 'epf', name: 'EPF Account', value: 95000, currency: 'INR' },
      { type: 'real_estate', name: 'Apartment', value: 3500000, currency: 'INR' },
      { type: 'gold', name: 'Gold Coins', value: 60000, currency: 'INR' }
    ]
  });
});

app.get('/mcp/get_liabilities', (req, res) => {
  res.json({
    liabilities: [
      { type: 'home_loan', name: 'HDFC Home Loan', value: 2500000, currency: 'INR', interest_rate: 7.5 },
      { type: 'car_loan', name: 'SBI Car Loan', value: 400000, currency: 'INR', interest_rate: 9.0 },
      { type: 'credit_card', name: 'ICICI Credit Card', value: 35000, currency: 'INR', interest_rate: 36.0 },
      { type: 'personal_loan', name: 'Bajaj Personal Loan', value: 100000, currency: 'INR', interest_rate: 13.5 }
    ]
  });
});

app.get('/mcp/get_flows', (req, res) => {
  res.json({
    flows: [
      { month: '2025-06', inflow: 48000, outflow: 32000 },
      { month: '2025-07', inflow: 51000, outflow: 29500 },
      { month: '2025-08', inflow: 50000, outflow: 30000 },
      { month: '2025-09', inflow: 52000, outflow: 31000 }
    ]
  });
});

  // New endpoints
  app.get('/mcp/get_transactions', (req, res) => {
    res.json({
      transactions: [
        { id: 1, date: '2025-08-01', type: 'credit', amount: 50000, description: 'Salary', account: 'HDFC Savings' },
        { id: 2, date: '2025-08-03', type: 'debit', amount: 1200, description: 'Groceries', account: 'HDFC Savings' },
        { id: 3, date: '2025-08-05', type: 'debit', amount: 2500, description: 'Electricity Bill', account: 'HDFC Savings' },
        { id: 4, date: '2025-08-10', type: 'debit', amount: 15000, description: 'SIP Investment', account: 'Axis Bluechip' },
        { id: 5, date: '2025-08-15', type: 'credit', amount: 2000, description: 'Interest', account: 'ICICI Current' }
      ]
    });
  });

  app.get('/mcp/get_goals', (req, res) => {
    res.json({
      goals: [
        { id: 1, name: 'Buy a House', target_amount: 5000000, current_amount: 350000, target_year: 2030 },
        { id: 2, name: 'Retirement', target_amount: 20000000, current_amount: 1200000, target_year: 2050 },
        { id: 3, name: 'Child Education', target_amount: 1500000, current_amount: 250000, target_year: 2035 }
      ]
    });
  });

  app.get('/mcp/get_profile', (req, res) => {
    res.json({
      profile: {
        name: 'Agam',
        email: 'agam@example.com',
        phone: '+91-9876543210',
        dob: '1995-04-15',
        city: 'Mumbai',
        occupation: 'Software Engineer'
      }
    });
  });

app.listen(port, () => {
  console.log(`MCP mock server running at http://localhost:${port}`);
  console.log(`Frontend available at http://localhost:${port}/index.html`);
});