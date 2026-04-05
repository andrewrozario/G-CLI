import React from 'react';

const Navbar = () => (
  <nav className="bg-white border-b shadow-sm">
    <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div className="text-xl font-bold text-blue-600">Gaia App</div>
      <div className="flex gap-6">
        <a href="#" className="text-gray-600 hover:text-blue-600">Home</a>
        <a href="#" className="text-gray-600 hover:text-blue-600">Features</a>
        <a href="#" className="text-gray-600 hover:text-blue-600">About</a>
      </div>
    </div>
  </nav>
);

export default Navbar;
