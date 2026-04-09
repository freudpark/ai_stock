import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Wallet, Search, BarChart3, 
  Settings, LogOut, Bell, ShieldCheck, Cpu 
} from 'lucide-react';
import './App.css';

const App = () => {
  // 초기 상태를 더 안전하게 설정
  const [balance, setBalance] = useState({ tot_evlu_amt: "0", evlu_pfls_amt: "0" });
  const [ticker, setTicker] = useState("005930");
  const [analysis, setAnalysis] = useState(null);
  const [market, setMarket] = useState("kr");
  const [loading, setLoading] = useState(false);
  const [autoTrading, setAutoTrading] = useState(false);

  const BACKEND_URL = 'https://ai-stock-backend.pyhgoshift.workers.dev';

  const fetchBalance = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/balance`);
      if (!res.ok) throw new Error('서버 응답 오류');
      const data = await res.json();
      
      if (data && data.summary) {
        const summary = Array.isArray(data.summary) ? data.summary[0] : data.summary;
        // 데이터가 에러 객체인 경우 처리
        if (summary && !summary.error) {
          setBalance(summary);
        } else {
          console.warn("잔고 데이터에 오류가 포함됨:", summary?.error);
        }
      }
    } catch (e) { 
      console.error("잔고 조회 실패:", e); 
    }
  };

  const analyzeStock = async (t) => {
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/quote/${market}/${t || ticker}`);
      if (!res.ok) throw new Error('분석 서버 응답 오류');
      const data = await res.json();
      setAnalysis(data);
    } catch (e) { 
      console.error("종목 분석 실패:", e); 
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const executeAutoTrade = async () => {
    setAutoTrading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/auto-trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: ticker, market: market })
      });
      const data = await res.json();
      
      if (data.status === 'success') {
        const decision = data.ai_decision;
        const exec = data.execution_result;
        let msg = `[AI 결정] ${decision.reason}\n\n`;
        if (exec && exec.error) {
          msg += `[주문 실패] ${exec.error}`;
        } else if (exec) {
          msg += `[주문 성공] 체결 대기 또는 완료됨. (주문번호: ${exec.ODNO || '확인필요'})`;
        } else {
          msg += `[실행 결과] 실제 주문이 발생하지 않았습니다.`;
        }
        alert(msg);
        fetchBalance(); // 주문 후 잔고 갱신
      } else {
        alert(`자동매매 오류: ${data.error}`);
      }
    } catch (e) {
      console.error("Auto trade failed", e);
      alert("네트워크 또는 서버 오류로 자동매매가 실패했습니다.");
    } finally {
      setAutoTrading(false);
    }
  };

  useEffect(() => {
    fetchBalance();
  }, []);


  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <Cpu color="#00d2ff" size={32} />
          <h2 style={{fontSize: '1.5rem', fontWeight: 800, color: 'white'}}>프로이트 트레이더</h2>
        </div>
        
        <nav style={{marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <div className="btn-primary" style={{display: 'flex', gap: '10px', alignItems: 'center', cursor: 'pointer'}}>
            <BarChart3 size={20} /> 대시보드
          </div>
          <div style={{color: 'rgba(255,255,255,0.6)', display: 'flex', gap: '10px', padding: '10px', cursor: 'pointer'}}>
            <Wallet size={20} /> 자산 현황
          </div>
          <div style={{color: 'rgba(255,255,255,0.6)', display: 'flex', gap: '10px', padding: '10px', cursor: 'pointer'}}>
            <Bell size={20} /> 알림 설정
          </div>
          <div style={{color: 'rgba(255,255,255,0.6)', display: 'flex', gap: '10px', padding: '10px', cursor: 'pointer'}}>
            <Settings size={20} /> 환경 설정
          </div>
        </nav>
        
        <div style={{marginTop: 'auto', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '12px'}}>
          <p style={{fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)'}}>시스템 상태</p>
          <div style={{display: 'flex', alignItems: 'center', gap: '5px', color: '#00ff88', fontSize: '0.9rem'}}>
            <ShieldCheck size={16} /> 보안 엣지 활성
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header style={{display: 'flex', justifyContent: 'space-between', marginBottom: '2rem'}}>
          <div>
            <h1 style={{fontSize: '2rem', marginBottom: '0.5rem', color: 'white'}}>트레이딩 허브</h1>
            <p style={{color: 'rgba(255,255,255,0.6)'}}>환영합니다, 프로이트 박 매니저님.</p>
          </div>
          <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
            <div className="glass-card" style={{padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px'}}>
              <div style={{width: '10px', height: '10px', background: '#00ff88', borderRadius: '50%'}}></div>
              <span style={{color: 'white'}}>실시간 연결됨</span>
            </div>
          </div>
        </header>

        <section className="stat-grid">
          <div className="glass-card" style={{background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
              <span style={{color: 'rgba(255,255,255,0.6)'}}>총 평가 자산</span>
              <Wallet color="#00d2ff" />
            </div>
            <h2 style={{fontSize: '1.8rem', color: 'white'}}>{Number(balance.tot_evlu_amt || 0).toLocaleString()} <small style={{fontSize: '0.8rem'}}>원</small></h2>
          </div>
          
          <div className="glass-card" style={{background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
              <span style={{color: 'rgba(255,255,255,0.6)'}}>당일 손익</span>
              {Number(balance.evlu_pfls_amt || 0) >= 0 ? <TrendingUp color="#00ff88" /> : <TrendingDown color="#ff4d4d" />}
            </div>
            <h2 style={{color: Number(balance.evlu_pfls_amt || 0) >= 0 ? "#00ff88" : "#ff4d4d"}}>
              {Number(balance.evlu_pfls_amt || 0).toLocaleString()} <small style={{fontSize: '0.8rem'}}>원</small>
            </h2>
          </div>
        </section>

        <div style={{display: 'grid', gridTemplateColumns: '1fr 340px', gap: '2rem', marginTop: '2rem'}}>
          <section className="glass-card" style={{background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '2rem'}}>
              <h3 style={{color: 'white'}}>실시간 종목 분석</h3>
              <div style={{display: 'flex', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '4px'}}>
                <button 
                  onClick={() => setMarket("kr")} 
                  style={{border: 'none', background: market === "kr" ? "#00d2ff" : "transparent", color: 'white', padding: '4px 12px', borderRadius: '4px', cursor: 'pointer'}}>국내</button>
                <button 
                  onClick={() => setMarket("us")} 
                  style={{border: 'none', background: market === "us" ? "#00d2ff" : "transparent", color: 'white', padding: '4px 12px', borderRadius: '4px', cursor: 'pointer'}}>해외</button>
              </div>
            </div>

            <div style={{display: 'flex', gap: '1rem', marginBottom: '2rem'}}>
              <div style={{flex: 1, position: 'relative'}}>
                <Search style={{position: 'absolute', left: '12px', top: '12px', color: 'rgba(255,255,255,0.4)'}} size={20} />
                <input 
                  type="text" 
                  value={ticker} 
                  onChange={(e) => setTicker(e.target.value)}
                  placeholder="종목 코드 (예: 005930)" 
                  style={{width: '100%', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '12px 12px 12px 42px', borderRadius: '8px', color: 'white'}}
                />
              </div>
              <button onClick={() => analyzeStock()} className="btn-primary" disabled={loading} style={{background: '#00d2ff', color: 'black', fontWeight: 'bold', padding: '0 20px', borderRadius: '8px', border: 'none', cursor: 'pointer'}}>
                {loading ? '분석 중...' : '분석하기'}
              </button>
            </div>

            {analysis && analysis.price_info && (
              <div style={{padding: '1.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
                  <span style={{fontSize: '1.2rem', fontWeight: 600, color: 'white'}}>{analysis.price_info.hts_kor_isnm || ticker}</span>
                  <span style={{fontSize: '1.2rem', color: '#00d2ff'}}>{Number(analysis.price_info.stck_prpr || analysis.price_info.last || 0).toLocaleString()} 원</span>
                </div>
                <div style={{display: 'flex', gap: '2rem'}}>
                  <div>
                    <p style={{color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem'}}>전략 신호</p>
                    <p style={{
                      fontSize: '1.5rem', 
                      fontWeight: 800, 
                      color: analysis.analysis.signal === "BUY" ? "#00ff88" : analysis.analysis.signal === "SELL" ? "#ff4d4d" : "white"
                    }}>
                      {analysis.analysis.signal === "BUY" ? "매수" : analysis.analysis.signal === "SELL" ? "매도" : "관망"}
                    </p>
                  </div>
                  <div style={{flex: 1}}>
                    <p style={{color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem'}}>신호 강도</p>
                    <div style={{width: '100%', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', marginTop: '12px'}}>
                      <div style={{width: `${analysis.analysis.strength * 100}%`, height: '100%', background: '#00d2ff', borderRadius: '4px', transition: 'width 0.5s ease'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>

          <aside className="glass-card" style={{background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <h3 style={{marginBottom: '1.5rem', color: 'white'}}>간편 주문</h3>
            <div style={{display: 'flex', flexDirection: 'column', gap: '1.5rem'}}>
              <div>
                <label style={{display: 'block', fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginBottom: '8px'}}>주문 유형</label>
                <select style={{width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '8px', color: 'white'}}>
                  <option>시장가</option>
                  <option>지정가</option>
                </select>
              </div>
              <div>
                <label style={{display: 'block', fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', marginBottom: '8px'}}>수량</label>
                <input type="number" defaultValue="1" style={{width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '8px', color: 'white'}} />
              </div>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '1rem'}}>
                <button style={{background: '#00ff88', color: 'black', fontWeight: 'bold', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer'}}>매수</button>
                <button style={{background: '#ff4d4d', color: 'white', fontWeight: 'bold', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer'}}>매도</button>
              </div>
              
              <div style={{marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                <h4 style={{color: '#00d2ff', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <Cpu size={18} /> 프로이트 AI 엔진
                </h4>
                <p style={{fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', marginBottom: '15px'}}>
                  지정된 종목의 시장 데이터와 지표를 분석하여 AI가 스스로 매수/매도를 결정하고 실제 주문을 집행합니다.
                </p>
                <button 
                  onClick={executeAutoTrade} 
                  disabled={autoTrading}
                  style={{
                    width: '100%',
                    background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)', 
                    color: 'white', 
                    fontWeight: 'bold', 
                    padding: '14px', 
                    borderRadius: '8px', 
                    border: 'none', 
                    cursor: autoTrading ? 'not-allowed' : 'pointer',
                    boxShadow: '0 4px 15px rgba(0, 210, 255, 0.3)',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                  {autoTrading ? 'AI 분석 및 주문 실행 중...' : 'AI 자동매매 시작'}
                </button>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default App;
