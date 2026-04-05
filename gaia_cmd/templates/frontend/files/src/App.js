import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Hero />
      </main>
      <footer className="bg-white py-8 border-t">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500">
          &copy; 2026 Gaia Project. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;
