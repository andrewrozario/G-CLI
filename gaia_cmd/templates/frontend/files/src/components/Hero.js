import React from 'react';

const Hero = () => (
  <div className="bg-white py-20 px-4">
    <div className="max-w-4xl mx-auto text-center">
      <h1 className="text-5xl font-extrabold text-gray-900 mb-6">
        Build Faster with <span className="text-blue-600">Gaia CLI</span>
      </h1>
      <p className="text-xl text-gray-600 mb-10 leading-relaxed">
        Autonomous development for modern developers. From idea to deployment, Gaia has your back.
      </p>
      <div className="flex justify-center gap-4">
        <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold shadow-lg hover:bg-blue-700">
          Get Started
        </button>
        <button className="bg-white text-gray-800 border px-8 py-3 rounded-lg font-semibold shadow-sm hover:bg-gray-50">
          Learn More
        </button>
      </div>
    </div>
  </div>
);

export default Hero;
