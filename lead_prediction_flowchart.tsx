import React, { useState } from 'react';
import { Database, Brain, TrendingUp, Users, Settings, RefreshCw, BarChart3, Smartphone } from 'lucide-react';

const LeadPredictionFlowchart = () => {
  const [hoveredSection, setHoveredSection] = useState(null);

  const sections = [
    {
      id: 'data-sources',
      title: 'Data Sources',
      icon: Database,
      color: 'bg-blue-500',
      items: [
        'CRM Data (Salesforce/Zoho)',
        'Website Analytics',
        'WhatsApp Business',
        'Email Campaigns',
        'Social Media (LinkedIn)',
        'Regional Demographics'
      ]
    },
    {
      id: 'data-processing',
      title: 'Data Processing',
      icon: Settings,
      color: 'bg-green-500',
      items: [
        'Data Cleaning & Validation',
        'Handle Missing Values',
        'Regional Standardization',
        'Multilingual Processing',
        'Feature Engineering',
        'Time-based Features'
      ]
    },
    {
      id: 'feature-engineering',
      title: 'Feature Engineering',
      icon: TrendingUp,
      color: 'bg-purple-500',
      items: [
        'Engagement Score',
        'Budget Cycle Alignment',
        'Regional Indicators',
        'Festival Season Impact',
        'Decision Maker Activity',
        'Industry Vertical Tags'
      ]
    },
    {
      id: 'model-training',
      title: 'Model Training',
      icon: Brain,
      color: 'bg-orange-500',
      items: [
        'XGBoost/LightGBM',
        'Random Forest',
        'Train-Test Split (80-20)',
        'Cross-Validation',
        'Hyperparameter Tuning',
        'Handle Class Imbalance'
      ]
    },
    {
      id: 'evaluation',
      title: 'Model Evaluation',
      icon: BarChart3,
      color: 'bg-red-500',
      items: [
        'AUC-ROC Score',
        'Precision & Recall',
        'Conversion Rate Analysis',
        'Sales Cycle Metrics',
        'Revenue Impact',
        'A/B Testing Results'
      ]
    },
    {
      id: 'deployment',
      title: 'Deployment',
      icon: Smartphone,
      color: 'bg-teal-500',
      items: [
        'REST API (FastAPI)',
        'Docker Container',
        'Cloud Deployment (AWS/Azure)',
        'CRM Integration',
        'Real-time Scoring',
        'Batch Processing'
      ]
    },
    {
      id: 'scoring',
      title: 'Lead Scoring & Action',
      icon: Users,
      color: 'bg-indigo-500',
      items: [
        'Hot Leads (80-100)',
        'Warm Leads (50-79)',
        'Cold Leads (<50)',
        'Auto-assign to Sales',
        'Trigger Nurture Campaigns',
        'WhatsApp Automation'
      ]
    },
    {
      id: 'monitoring',
      title: 'Monitoring & Feedback',
      icon: RefreshCw,
      color: 'bg-pink-500',
      items: [
        'Performance Tracking',
        'Data Drift Detection',
        'Sales Feedback Loop',
        'Weekly Reports',
        'Quarterly Retraining',
        'Continuous Optimization'
      ]
    }
  ];

  return (
    <div className="w-full h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-3">
            AI Lead Prediction Model
          </h1>
          <p className="text-xl text-gray-300">Enterprise Implementation for Indian Market</p>
        </div>

        <div className="relative">
          {/* Connection Lines */}
          <div className="absolute inset-0 pointer-events-none">
            <svg className="w-full h-full">
              {/* Vertical flow lines */}
              <path
                d="M 400 180 L 400 240"
                stroke="#4B5563"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
              />
              <path
                d="M 400 420 L 400 480"
                stroke="#4B5563"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
              />
              <path
                d="M 400 660 L 400 720"
                stroke="#4B5563"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
              />
              <path
                d="M 400 900 L 400 960"
                stroke="#4B5563"
                strokeWidth="2"
                fill="none"
                strokeDasharray="5,5"
              />
            </svg>
          </div>

          {/* Flow Sections */}
          <div className="space-y-8">
            {sections.map((section, index) => {
              const Icon = section.icon;
              const isHovered = hoveredSection === section.id;
              
              return (
                <div
                  key={section.id}
                  onMouseEnter={() => setHoveredSection(section.id)}
                  onMouseLeave={() => setHoveredSection(null)}
                  className="relative z-10"
                >
                  <div className={`
                    bg-gray-800 rounded-xl border-2 border-gray-700 
                    transition-all duration-300 
                    ${isHovered ? 'transform scale-105 border-gray-500 shadow-2xl' : ''}
                  `}>
                    <div className={`${section.color} p-4 rounded-t-lg flex items-center gap-3`}>
                      <Icon className="text-white" size={28} />
                      <h2 className="text-2xl font-bold text-white">{section.title}</h2>
                    </div>
                    
                    <div className="p-6 grid grid-cols-2 md:grid-cols-3 gap-3">
                      {section.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-700 px-4 py-3 rounded-lg text-gray-200 text-sm font-medium hover:bg-gray-600 transition-colors"
                        >
                          • {item}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Arrow indicator */}
                  {index < sections.length - 1 && (
                    <div className="flex justify-center my-4">
                      <div className="text-gray-500 text-3xl">↓</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Additional Info Boxes */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-lg border border-blue-700">
            <h3 className="text-xl font-bold text-white mb-3">Indian Market Specifics</h3>
            <ul className="text-gray-200 space-y-2 text-sm">
              <li>✓ Regional customization</li>
              <li>✓ Festival season tracking</li>
              <li>✓ Multilingual support</li>
              <li>✓ UPI/digital payment factors</li>
              <li>✓ GST compliance consideration</li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-green-900 to-green-800 p-6 rounded-lg border border-green-700">
            <h3 className="text-xl font-bold text-white mb-3">Tech Stack</h3>
            <ul className="text-gray-200 space-y-2 text-sm">
              <li>✓ Python + XGBoost/LightGBM</li>
              <li>✓ FastAPI + Docker</li>
              <li>✓ AWS/Azure/GCP</li>
              <li>✓ PostgreSQL database</li>
              <li>✓ MLflow monitoring</li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-6 rounded-lg border border-purple-700">
            <h3 className="text-xl font-bold text-white mb-3">Success Metrics</h3>
            <ul className="text-gray-200 space-y-2 text-sm">
              <li>✓ 25-40% conversion lift</li>
              <li>✓ 30% faster sales cycles</li>
              <li>✓ 85%+ AUC-ROC score</li>
              <li>✓ Sales team adoption rate</li>
              <li>✓ ROI tracking per quarter</li>
            </ul>
          </div>
        </div>

        {/* Timeline */}
        <div className="mt-12 bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Implementation Timeline</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3 text-xl font-bold">1-2</div>
              <p className="text-white font-semibold mb-1">Months 1-2</p>
              <p className="text-gray-400 text-sm">Data collection & baseline model</p>
            </div>
            <div className="text-center">
              <div className="bg-green-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3 text-xl font-bold">3</div>
              <p className="text-white font-semibold mb-1">Month 3</p>
              <p className="text-gray-400 text-sm">Optimization & testing</p>
            </div>
            <div className="text-center">
              <div className="bg-orange-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3 text-xl font-bold">4</div>
              <p className="text-white font-semibold mb-1">Month 4</p>
              <p className="text-gray-400 text-sm">System integration</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3 text-xl font-bold">∞</div>
              <p className="text-white font-semibold mb-1">Ongoing</p>
              <p className="text-gray-400 text-sm">Monitor & improve</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadPredictionFlowchart;