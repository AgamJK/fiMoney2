import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiArrowRight, FiCheck, FiLock, FiShield, FiSmartphone } from 'react-icons/fi';

const GetStartedPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Form submitted:', formData);
  };

  const features = [
    {
      icon: <FiLock className="w-6 h-6 text-primary-500" />,
      title: "Secure & Private",
      description: "Bank-level encryption to keep your data safe"
    },
    {
      icon: <FiShield className="w-6 h-6 text-primary-500" />,
      title: "No Credit Card Required",
      description: "Start your free trial with no commitment"
    },
    {
      icon: <FiSmartphone className="w-6 h-6 text-primary-500" />,
      title: "Access Anywhere",
      description: "Use on any device, anywhere"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold mb-6"
          >
            Start Your Financial Journey Today
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl mb-8 max-w-3xl mx-auto"
          >
            Join thousands of users who are taking control of their finances with our powerful tools.
          </motion.p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Signup Form */}
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white p-8 rounded-xl shadow-lg"
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Your Free Account</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="John Doe"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="you@example.com"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="••••••••"
                  minLength={8}
                  required
                />
                <p className="mt-1 text-xs text-gray-500">Minimum 8 characters</p>
              </div>
              
              <button
                type="submit"
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center"
              >
                Get Started Free
                <FiArrowRight className="ml-2" />
              </button>
              
              <p className="text-xs text-gray-500 text-center">
                By signing up, you agree to our Terms of Service and Privacy Policy
              </p>
            </form>
          </motion.div>
          
          {/* Features */}
          <div className="space-y-8">
            <h3 className="text-2xl font-semibold text-gray-900">Why Choose Us?</h3>
            
            <div className="space-y-6">
              {features.map((feature, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: 50 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * (index + 1) }}
                  className="flex items-start"
                >
                  <div className="flex-shrink-0 bg-primary-100 p-2 rounded-lg">
                    {feature.icon}
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-medium text-gray-900">{feature.title}</h4>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
            
            <div className="bg-blue-50 p-6 rounded-xl">
              <h4 className="font-medium text-gray-900 mb-3">What's included in your free account:</h4>
              <ul className="space-y-2">
                {[
                  'Unlimited budget tracking',
                  'Up to 3 connected bank accounts',
                  'Basic financial insights',
                  'Email support',
                  '14-day free trial of premium features'
                ].map((item, index) => (
                  <li key={index} className="flex items-start">
                    <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="bg-primary-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to take control of your finances?</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">Join thousands of users who are already managing their money smarter.</p>
          <a
            href="#"
            className="inline-block bg-white text-primary-700 font-medium px-8 py-3 rounded-lg hover:bg-gray-100 transition duration-200"
          >
            Get Started Free
          </a>
        </div>
      </div>
    </div>
  );
};

export default GetStartedPage;
