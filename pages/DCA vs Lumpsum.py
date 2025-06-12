import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, DollarSign, Calendar, BarChart3, Calculator, AlertCircle } from 'lucide-react';

const THAI_STOCKS = {
  "SET 50": ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK", "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK", "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK", "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK"],
  "Banking": ["BBL.BK", "KBANK.BK", "KTB.BK", "SCB.BK", "TISCO.BK", "TTB.BK"],
  "Energy": ["PTT.BK", "PTTEP.BK", "PTTGC.BK", "BANPU.BK", "GULF.BK"],
  "Technology": ["ADVANC.BK", "INTUCH.BK", "TRUE.BK", "COM7.BK", "DELTA.BK"],
  "Popular ETFs": ["TFFIF.BK", "QQQQ-R.BK", "SPY-R.BK", "VTI-R.BK"]
};

// Simulate stock price data (in real app, this would fetch from Yahoo Finance API)
const generateStockData = (ticker, startDate, months) => {
  const data = [];
  let price = 100 + Math.random() * 50; // Starting price between 100-150
  const volatility = 0.02 + Math.random() * 0.03; // Daily volatility 2-5%
  const trend = (Math.random() - 0.3) * 0.001; // Slight upward bias
  
  for (let i = 0; i < months * 22; i++) { // 22 trading days per month
    const dailyReturn = (Math.random() - 0.5) * volatility + trend;
    price = price * (1 + dailyReturn);
    
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    data.push({
      date: date.toISOString().split('T')[0],
      price: Math.max(price, 1), // Ensure price doesn't go negative
      dailyReturn
    });
  }
  return data;
};

const DCAAnalyzer = () => {
  const [selectedCategory, setSelectedCategory] = useState("SET 50");
  const [selectedStock, setSelectedStock] = useState("ADVANC.BK");
  const [monthlyAmount, setMonthlyAmount] = useState(10000);
  const [lumpSumAmount, setLumpSumAmount] = useState(120000);
  const [durationMonths, setDurationMonths] = useState(12);
  const [startDate, setStartDate] = useState("2023-01-01");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const calculateDCA = (stockData, monthlyInvestment, duration) => {
    let totalShares = 0;
    let totalInvested = 0;
    const transactions = [];
    
    // Invest monthly
    for (let month = 0; month < duration; month++) {
      const dayIndex = month * 22; // Approximately 22 trading days per month
      if (dayIndex >= stockData.length) break;
      
      const price = stockData[dayIndex].price;
      const shares = monthlyInvestment / price;
      totalShares += shares;
      totalInvested += monthlyInvestment;
      
      const currentValue = totalShares * price;
      transactions.push({
        month: month + 1,
        price,
        shares,
        totalShares,
        invested: totalInvested,
        value: currentValue,
        return: ((currentValue - totalInvested) / totalInvested) * 100
      });
    }
    
    const finalPrice = stockData[Math.min((duration - 1) * 22, stockData.length - 1)].price;
    const finalValue = totalShares * finalPrice;
    
    return {
      transactions,
      totalInvested,
      totalShares,
      finalValue,
      totalReturn: ((finalValue - totalInvested) / totalInvested) * 100,
      avgPrice: totalInvested / totalShares
    };
  };

  const calculateLumpSum = (stockData, investment, duration) => {
    const initialPrice = stockData[0].price;
    const shares = investment / initialPrice;
    const transactions = [];
    
    // Track portfolio value over time
    for (let month = 0; month < duration; month++) {
      const dayIndex = month * 22;
      if (dayIndex >= stockData.length) break;
      
      const price = stockData[dayIndex].price;
      const value = shares * price;
      
      transactions.push({
        month: month + 1,
        price,
        value,
        return: ((value - investment) / investment) * 100
      });
    }
    
    const finalPrice = stockData[Math.min((duration - 1) * 22, stockData.length - 1)].price;
    const finalValue = shares * finalPrice;
    
    return {
      transactions,
      totalInvested: investment,
      shares,
      finalValue,
      totalReturn: ((finalValue - investment) / investment) * 100,
      initialPrice
    };
  };

  const runAnalysis = () => {
    setLoading(true);
    
    setTimeout(() => {
      const stockData = generateStockData(selectedStock, new Date(startDate), durationMonths);
      const dcaResults = calculateDCA(stockData, monthlyAmount, durationMonths);
      const lumpSumResults = calculateLumpSum(stockData, lumpSumAmount, durationMonths);
      
      setResults({
        stockData,
        dca: dcaResults,
        lumpSum: lumpSumResults,
        winner: dcaResults.totalReturn > lumpSumResults.totalReturn ? 'DCA' : 'Lump Sum'
      });
      setLoading(false);
    }, 1000);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: 'THB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-xl mb-6 shadow-lg">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <TrendingUp className="w-8 h-8" />
            DCA vs Lump Sum Analyzer
          </h1>
          <p className="mt-2 opacity-90">Compare Dollar Cost Averaging vs Lump Sum investment strategies</p>
        </div>

        {/* Settings Panel */}
        <div className="bg-white rounded-xl p-6 mb-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            Investment Settings
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {/* Stock Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock Category</label>
              <select 
                value={selectedCategory} 
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setSelectedStock(THAI_STOCKS[e.target.value][0]);
                }}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {Object.keys(THAI_STOCKS).map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
              <select 
                value={selectedStock} 
                onChange={(e) => setSelectedStock(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {THAI_STOCKS[selectedCategory].map(stock => (
                  <option key={stock} value={stock}>{stock}</option>
                ))}
              </select>
            </div>

            {/* Investment Amounts */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DCA Monthly (THB)</label>
              <input 
                type="number" 
                value={monthlyAmount} 
                onChange={(e) => setMonthlyAmount(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="1000"
                step="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lump Sum (THB)</label>
              <input 
                type="number" 
                value={lumpSumAmount} 
                onChange={(e) => setLumpSumAmount(Number(e.target.value))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="10000"
                step="10000"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duration (Months)</label>
              <input 
                type="range" 
                min="6" 
                max="36" 
                value={durationMonths} 
                onChange={(e) => setDurationMonths(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{durationMonths} months</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input 
                type="date" 
                value={startDate} 
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
          </div>

          <button 
            onClick={runAnalysis}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 className="w-5 h-5" />
                Run Analysis
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* DCA Card */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-blue-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  DCA Strategy
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Final Value: <span className="font-semibold text-gray-800">{formatCurrency(results.dca.finalValue)}</span></p>
                  <p className="text-sm text-gray-600">Total Invested: <span className="font-semibold text-gray-800">{formatCurrency(results.dca.totalInvested)}</span></p>
                  <p className="text-sm text-gray-600">Average Price: <span className="font-semibold text-gray-800">{formatCurrency(results.dca.avgPrice)}</span></p>
                  <p className={`text-lg font-bold ${results.dca.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(results.dca.totalReturn)}
                  </p>
                </div>
              </div>

              {/* Lump Sum Card */}
              <div className="bg-white rounded-xl p-6 shadow-lg border-l-4 border-purple-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <DollarSign className="w-5 h-5" />
                  Lump Sum Strategy
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Final Value: <span className="font-semibold text-gray-800">{formatCurrency(results.lumpSum.finalValue)}</span></p>
                  <p className="text-sm text-gray-600">Total Invested: <span className="font-semibold text-gray-800">{formatCurrency(results.lumpSum.totalInvested)}</span></p>
                  <p className="text-sm text-gray-600">Entry Price: <span className="font-semibold text-gray-800">{formatCurrency(results.lumpSum.initialPrice)}</span></p>
                  <p className={`text-lg font-bold ${results.lumpSum.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(results.lumpSum.totalReturn)}
                  </p>
                </div>
              </div>

              {/* Winner Card */}
              <div className={`bg-gradient-to-r ${results.winner === 'DCA' ? 'from-blue-500 to-blue-600' : 'from-purple-500 to-purple-600'} text-white rounded-xl p-6 shadow-lg`}>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Winner
                </h3>
                <div className="text-center">
                  <p className="text-2xl font-bold">{results.winner}</p>
                  <p className="text-sm opacity-90 mt-1">
                    Better by {Math.abs(results.dca.totalReturn - results.lumpSum.totalReturn).toFixed(2)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <h3 className="text-xl font-semibold mb-4">Portfolio Value Comparison</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(value) => formatCurrency(value)} />
                  <Tooltip 
                    formatter={(value, name) => [formatCurrency(value), name]}
                    labelFormatter={(month) => `Month ${month}`}
                  />
                  <Legend />
                  <Line 
                    data={results.dca.transactions}
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3B82F6" 
                    strokeWidth={3}
                    name="DCA Portfolio"
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    data={results.lumpSum.transactions}
                    type="monotone" 
                    dataKey="value" 
                    stroke="#8B5CF6" 
                    strokeWidth={3}
                    name="Lump Sum Portfolio"
                    dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Warning */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <p className="font-semibold mb-1">Important Disclaimer</p>
                  <p>This analysis uses simulated data and is for educational purposes only. Past performance does not guarantee future results. Consider transaction fees, taxes, and market conditions in real investments. Always consult with a financial advisor before making investment decisions.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DCAAnalyzer;
