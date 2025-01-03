import "./App.css"
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Bell, Menu, Upload, Plus, FileText, CheckCircle } from 'lucide-react';
import { taxService, expenseService, forecastingService } from './services/api'; // Import services

const App = () => {
  const [chartData] = useState([
    { month: 'Jan', expenses: 4500 },
    { month: 'Feb', expenses: 5200 },
    { month: 'Mar', expenses: 4800 },
    { month: 'Apr', expenses: 5700 },
    { month: 'May', expenses: 5100 },
    { month: 'Jun', expenses: 6200 },
  ]);

  const [taxAlerts, setTaxAlerts] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);

  // Fetch tax alerts on component mount
  useEffect(() => {
    const fetchTaxAlerts = async () => {
      try {
        const alerts = await taxService.getAlerts();
        setTaxAlerts(alerts);
      } catch (error) {
        console.error('Failed to fetch alerts:', error);
      }
    };

    const fetchForecast = async () => {
      try {
        const data = await forecastingService.predictTaxLiability();
        setForecast(data);
      } catch (error) {
        console.error('Failed to fetch forecast:', error);
      }
    };

    fetchTaxAlerts();
    fetchForecast();
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append('files', file);
      });

      const response = await expenseService.uploadReceipt(formData);
      setUploadStatus('Upload successful!');
      console.log('Upload successful:', response);
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
      console.error('Upload failed:', error);
    }
  };

  return (
    <div className="bg-gradient-to-br from-indigo-950 w-full to-indigo-900 text-gray-100 m-0 p-0">
      <nav className="fixed top-0 z-50 w-full bg-opacity-70 backdrop-blur-lg border-b border-gray-700">
        <div className="px-3 py-3 lg:px-5 lg:pl-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-start">
              <button className="p-2 rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-600">
                <Menu className="w-6 h-6" />
              </button>
              <span className="ml-4 text-xl font-semibold">AI Tax Management</span>
            </div>
            <div className="flex items-center gap-4">
              <button className="relative p-2 rounded-lg hover:bg-gray-700">
                <Bell className="w-6 h-6" />
                <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-gray-700">
                <img src="/api/placeholder/32/32" className="w-8 h-8 rounded-full" alt="User" />
                <span>John Doe</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="px-4 pt-10 pb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6 m-6">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20 shadow-lg">
            <h3 className="text-lg font-medium">Tax Alerts</h3>
            <div className="space-y-3">
              {taxAlerts.length > 0 ? (
                taxAlerts.map((alert, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-red-500 bg-opacity-20">
                    <Bell className="w-6 h-6 text-red-400" />
                    <div>
                      <p className="font-medium">{alert.title}</p>
                      <p className="text-sm opacity-75">{alert.message}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p>No alerts available.</p>
              )}
            </div>
          </div>

          {/* Quick Actions Section */}
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20 shadow-lg">
            <h3 className="text-lg font-medium mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-3">
              <button className="p-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 transition-colors flex flex-col items-center">
                <Plus className="w-6 h-6 mb-2" />
                Upload Receipt
              </button>
              <button className="p-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 transition-colors flex flex-col items-center">
                <FileText className="w-6 h-6 mb-2" />
                View Report
              </button>
            </div>
          </div>
        </div>

        {/* Receipt Upload Section */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 m-6 border border-white border-opacity-20">
          <h2 className="text-2xl font-semibold mb-4">Upload Receipts</h2>
          <div
            className="border-2 border-dashed border-gray-400 rounded-xl p-8 text-center cursor-pointer hover:border-indigo-500 hover:bg-indigo-500 hover:bg-opacity-10 transition-all"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="mb-2 text-lg">
              Drop your receipts here or <span className="text-indigo-400">browse</span>
            </p>
            <p className="text-sm opacity-75">Supported formats: PNG, JPG, PDF</p>
          </div>
          {uploadStatus && (
            <div className="mt-4 text-center text-sm text-green-500">{uploadStatus}</div>
          )}
        </div>

        {/* AI Analysis Section */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 m-6 border border-white border-opacity-20  pb-10 mb-0">
          <h2 className="text-2xl font-semibold mb-4">AI Tax Analysis</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <XAxis dataKey="month" stroke="#e5e7eb" />
                  <YAxis stroke="#e5e7eb" />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="expenses"
                    stroke="#818cf8"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-green-500 bg-opacity-20">
                <h4 className="font-medium mb-2">Tax Saving Opportunities</h4>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Home Office Deduction: $2,400
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Retirement Contributions: $3,100
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
