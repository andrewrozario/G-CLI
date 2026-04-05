import React, { useState, useEffect } from 'react';

const App = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>SaaS Admin Dashboard</h1>
      {loading ? (
        <p>Loading stats...</p>
      ) : stats ? (
        <div style={{ display: 'flex', gap: '20px' }}>
          <StatCard title="Total Users" value={stats.total_users} />
          <StatCard title="Active Projects" value={stats.active_projects} />
          <StatCard title="Revenue" value={`$${stats.revenue}`} />
        </div>
      ) : (
        <p>Failed to load statistics.</p>
      )}
    </div>
  );
};

const StatCard = ({ title, value }) => (
  <div style={{ 
    padding: '15px', 
    border: '1px solid #ddd', 
    borderRadius: '8px',
    width: '200px' 
  }}>
    <h3 style={{ color: '#666', margin: '0 0 10px 0' }}>{title}</h3>
    <p style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>{value}</p>
  </div>
);

export default App;
