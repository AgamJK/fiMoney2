import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { 
  FiArrowRight, 
  FiCheck, 
  FiDollarSign, 
  FiPieChart, 
  FiUsers, 
  FiTrendingUp, 
  FiShield, 
  FiSmartphone,
  FiLogIn
} from 'react-icons/fi';

const HomePage: React.FC = () => {
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    // You can add any additional logic here before navigating
    console.log('Navigating to Get Started page');
    navigate('/get-started');
  };

  const features = [
    {
      icon: <FiDollarSign className="w-6 h-6 text-primary-600" />,
      title: 'Unified Finance',
      description: 'Connect all your financial accounts in one place for a complete view of your money.'
    },
    {
      icon: <FiUsers className="w-6 h-6 text-primary-600" />,
      title: 'Collaborative Budgeting',
      description: 'Plan and track shared expenses with family, friends, or roommates.'
    },
    {
      icon: <FiTrendingUp className="w-6 h-6 text-primary-600" />,
      title: 'AI-Powered Insights',
      description: 'Get personalized financial advice powered by Gemini AI.'
    },
    {
      icon: <FiPieChart className="w-6 h-6 text-primary-600" />,
      title: 'Advanced Analytics',
      description: 'Visualize your spending patterns and financial health.'
    },
    {
      icon: <FiShield className="w-6 h-6 text-primary-600" />,
      title: 'Bank-Grade Security',
      description: 'Your data is encrypted and protected with enterprise-grade security.'
    },
    {
      icon: <FiSmartphone className="w-6 h-6 text-primary-600" />,
      title: 'Mobile First',
      description: 'Access your finances on the go with our mobile-optimized platform.'
    }
  ];

  const stats = [
    { value: '10K+', label: 'Active Users' },
    { value: '100M+', label: 'Transactions Analyzed' },
    { value: '50+', label: 'Financial Institutions' },
    { value: '4.9/5', label: 'User Rating' }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    console.log('Email submitted:', email);
  };

  return (
    <div className="overflow-hidden">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <FiDollarSign className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">FinCollab</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <a href="#" className="border-primary-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">Home</a>
                <a href="#features" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">Features</a>
                <a href="#how-it-works" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">How It Works</a>
                <a href="#pricing" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">Pricing</a>
              </div>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:items-center">
              <a href="/login" className="text-gray-900 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">Log in</a>
              <a href="/signup" className="ml-4 bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors">Sign up free</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary-700 to-primary-900 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="relative z-10 text-center">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-4xl md:text-6xl font-bold text-white mb-6"
            >
              Smarter Finance, Together
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-xl text-primary-100 max-w-3xl mx-auto mb-10"
            >
              The all-in-one platform for managing your personal and shared finances with AI-powered insights and seamless collaboration.
            </motion.p>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <a 
                href="/signup" 
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-primary-700 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10 transition-colors duration-200"
              >
                Get Started Free
              </a>
              <a 
                href="#demo" 
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-10 transition-colors duration-200"
              >
                Watch Demo
              </a>
            </motion.div>
          </div>
        </div>
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-grid-white/[0.05] [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]"></div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center">
            {/* Link Navigation Example */}
            <div className="mb-8">
              <Link 
                to="/get-started" 
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-lg md:px-8 transition-colors"
              >
                Get Started with Link <FiArrowRight className="ml-2" />
              </Link>
            </div>
            
            {/* Programmatic Navigation Example */}
            <button
              onClick={handleGetStartedClick}
              className="mb-8 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 md:py-4 md:text-lg md:px-8 transition-colors"
            >
              Get Started Programmatically <FiLogIn className="ml-2" />
            </button>
            
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Everything you need to manage your finances
            </h2>
            <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
              Powerful features to help you take control of your financial life.
            </p>
          </div>
          
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100"
              >
                <div className="w-12 h-12 rounded-full bg-primary-50 flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-primary-700 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 text-center sm:grid-cols-4">
            {stats.map((stat, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="px-4"
              >
                <p className="text-4xl font-extrabold text-white">{stat.value}</p>
                <p className="mt-2 text-sm font-medium text-primary-100">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-primary-700 rounded-2xl p-8 md:p-12 shadow-xl overflow-hidden">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="md:w-1/2 mb-8 md:mb-0">
                <h2 className="text-3xl font-extrabold text-white">Ready to take control of your finances?</h2>
                <p className="mt-4 text-lg text-primary-100">Join thousands of users who trust FinCollab for their financial management needs.</p>
              </div>
              <div className="w-full md:w-1/2 md:pl-8">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="flex flex-col sm:flex-row gap-4">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      className="flex-1 px-4 py-3 rounded-md border border-transparent focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-700"
                      required
                    />
                    <button
                      type="submit"
                      className="px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-700 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-primary-700 focus:ring-white transition-colors duration-200"
                    >
                      Get Started
                    </button>
                  </div>
                  <p className="text-sm text-primary-100">
                    We care about your data. Read our{' '}
                    <a href="/privacy" className="text-white underline hover:text-gray-200">Privacy Policy</a>.
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
