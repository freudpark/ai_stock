import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Wallet, Search, BarChart3, 
  Settings, LogOut, Bell, ShieldCheck, Cpu 
} from 'lucide-react';
import './App.css';

const App = () => {
  const [balance, setBalance] = useState({ tot_evlu_amt: "0", evlu_pfls_amt: "0" });
  const [ticker, setTicker] = useState("005930");
  const [analysis, setAnalysis] = useState(null);
  const [market, setMarket] = useState("kr");

  const fetchBalance = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/balance');
      const data = await res.json();
      if (data.summary) setBalance(data.summary[0]);
    } catch (e) { console.error("Balance fetch error", e); }
  };

  const analyzeStock = async (t) => {
    try {
      const res = await fetch(`http://localhost:8000/api/quote/${market}/${t || ticker}`);
      const data = await res.json();
      setAnalysis(data);
    } catch (e) { console.error("Analysis error", e); }
  };

  useEffect(() => {
    fetchBalance();
  }, []);

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <Cpu color="#00d2ff" size={32} />
          <h2 style={{fontSize: '1.5rem', fontWeight: 800}}>FREUDP TRADER</h2>
        </div>
        
        <nav style={{marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <div className="btn-primary" style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
            <BarChart3 size={20} /> Dashboard
          </div>
          <div style={{color: 'var(--text-secondary)', display: 'flex', gap: '10px', padding: '10px'}}>
            <Wallet size={20} /> Assets
          </div>
          <div style={{color: 'var(--text-secondary)', display: 'flex', gap: '10px', padding: '10px'}}>
            <Bell size={20} /> Alerts
          </div>
          <div style={{color: 'var(--text-secondary)', display: 'flex', gap: '10px', padding: '10px'}}>
            <Settings size={20} /> Settings
          </div>
        </nav>
        
        <div style={{marginTop: 'auto', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '12px'}}>
          <p style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>System Status</p>
          <div style={{display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--success)', fontSize: '0.9rem'}}>
            <ShieldCheck size={16} /> Secure Edge Active
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header style={{display: 'flex', justifyContent: 'space-between', marginBottom: '2rem'}}>
          <div>
            <h1 style={{fontSize: '2rem', marginBottom: '0.5rem'}}>Trading Hub</h1>
            <p style={{color: 'var(--text-secondary)'}}>Welcome back, Manager Freud Park.</p>
          </div>
          <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
            <div className="glass-card" style={{padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '10px'}}>
              <div style={{width: '10px', height: '10px', background: 'var(--success)', borderRadius: '50%'}}></div>
              <span>Live Market</span>
            </div>
          </div>
        </header>

        <section className="stat-grid">
          <div className="glass-card">
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
              <span style={{color: 'var(--text-secondary)'}}>Total Assets</span>
              <Wallet color="var(--accent-blue)" />
            </div>
            <h2 style={{fontSize: '1.8rem'}}>{Number(balance.tot_evlu_amt).toLocaleString()} <small style={{fontSize: '0.8rem'}}>KRW</small></h2>
          </div>
          
          <div className="glass-card">
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
              <span style={{color: 'var(--text-secondary)'}}>P/L (Today)</span>
              {Number(balance.evlu_pfls_amt) >= 0 ? <TrendingUp color="var(--success)" /> : <TrendingDown color="var(--danger)" />}
            </div>
            <h2 style={{color: Number(balance.evlu_pfls_amt) >= 0 ? "var(--success)" : "var(--danger)"}}>
              {Number(balance.evlu_pfls_amt).toLocaleString()} <small style={{fontSize: '0.8rem'}}>KRW</small>
            </h2>
          </div>
        </section>

        <div style={{display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem'}}>
          <section className="glass-card">
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '2rem'}}>
              <h3>Real-time Analysis</h3>
              <div style={{display: 'flex', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '4px'}}>
                <button 
                  onClick={() => setMarket("kr")} 
                  style={{border: 'none', background: market === "kr" ? "var(--accent-blue)" : "transparent", color: 'white', padding: '4px 12px', borderRadius: '4px', cursor: 'pointer'}}>KR</button>
                <button 
                  onClick={() => setMarket("us")} 
                  style={{border: 'none', background: market === "us" ? "var(--accent-blue)" : "transparent", color: 'white', padding: '4px 12px', borderRadius: '4px', cursor: 'pointer'}}>US</button>
              </div>
            </div>

            <div style={{display: 'flex', gap: '1rem', marginBottom: '2rem'}}>
              <div style={{flex: 1, position: 'relative'}}>
                <Search style={{position: 'absolute', left: '12px', top: '12px', color: 'var(--text-secondary)'}} size={20} />
                <input 
                  type="text" 
                  value={ticker} 
                  onChange={(e) => setTicker(e.target.value)}
                  placeholder="Enter Ticker (e.g. 005930)" 
                  style={{width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', padding: '12px 12px 12px 42px', borderRadius: '8px', color: 'white'}}
                />
              </div>
              <button onClick={() => analyzeStock()} className="btn-primary">Analyze</button>
            </div>

            {analysis && (
              <div style={{padding: '1.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
                  <span style={{fontSize: '1.2rem', fontWeight: 600}}>{analysis.price_info.hts_kor_isnm || ticker}</span>
                  <span style={{fontSize: '1.2rem', color: 'var(--accent-blue)'}}>{Number(analysis.price_info.stck_prpr || analysis.price_info.last).toLocaleString()}</span>
                </div>
                <div style={{display: 'flex', gap: '2rem'}}>
                  <div>
                    <p style={{color: 'var(--text-secondary)', fontSize: '0.8rem'}}>Strategy Signal</p>
                    <p className={analysis.analysis.signal === "BUY" ? "signal-buy" : "signal-sell"}>{analysis.analysis.signal}</p>
                  </div>
                  <div>
                    <p style={{color: 'var(--text-secondary)', fontSize: '0.8rem'}}>Signal Strength</p>
                    <div style={{width: '100px', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', marginTop: '8px'}}>
                      <div style={{width: `${analysis.analysis.strength * 100}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: '4px'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>

          <aside className="glass-card">
            <h3 style={{marginBottom: '1.5rem'}}>Quick Trade</h3>
            <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
              <div>
                <label style={{display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '5px'}}>Order Type</label>
                <select style={{width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', padding: '10px', borderRadius: '8px', color: 'white'}}>
                  <option>Market Price</option>
                  <option>Limit Price</option>
                </select>
              </div>
              <div>
                <label style={{display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '5px'}}>Quantity</label>
                <input type="number" defaultValue="1" style={{width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', padding: '10px', borderRadius: '8px', color: 'white'}} />
              </div>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '1rem'}}>
                <button className="btn-primary" style={{background: 'var(--success)'}}>BUY</button>
                <button className="btn-primary" style={{background: 'var(--danger)'}}>SELL</button>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default App;
