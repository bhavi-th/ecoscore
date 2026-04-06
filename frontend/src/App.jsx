import { useState, useEffect } from "react";
import InputPanel from "./components/InputPanel";
import ConsumerInputPanel from "./components/ConsumerInputPanel";
import BusinessInputPanel from "./components/BusinessInputPanel";
import Score from "./components/Score";
import Simulator from "./components/Simulator";
import AlternativesPanel from "./components/AlternativesPanel";
import { calculateEcoScore } from "./utils/calcEngine";
import "./styles/App.css";

function App() {
  const [mode, setMode] = useState("consumer"); // "business" or "consumer"
  
  // Core state for environmental factors
  const [inputs, setInputs] = useState({
    categoryVal: 0,
    materialVal: 0,
    transportVal: 0,
    packagingVal: 0,
    name: "AWAITING_SCAN"
  });

  const [baselineCarbon, setBaselineCarbon] = useState(null);
  const [foundProducts, setFoundProducts] = useState([]);
  const [businessData, setBusinessData] = useState(null);
  
  // Real-Time Response: Results are computed instantly on every state change
  const results = calculateEcoScore(inputs);

  // Effect: Capture the baseline only once when the first valid data arrives
  useEffect(() => {
    if (results.carbon > 0 && baselineCarbon === null) {
      setBaselineCarbon(results.carbon);
    }
  }, [results.carbon, baselineCarbon]);

  // Handler for switching modes to prevent data cross-contamination
  const handleModeChange = (newMode) => {
    setMode(newMode);
    setBaselineCarbon(null); // Reset baseline for fresh What-If simulation
    setFoundProducts([]);    // Clear scan history
    setBusinessData(null);   // Clear business data
    setInputs({
      categoryVal: 0,
      materialVal: 0,
      transportVal: 0,
      packagingVal: 0,
      name: "AWAITING_SCAN"
    });
  };

  return (
    <div className="dashboard-container">
      <header className="hud-header">
        <h1 className="highlight">ECOSCORE // SUSTAINABILITY_TRACKER</h1>
        
        <div className="mode-tabs">
          <button 
            className={`mode-tab ${mode === "consumer" ? "active" : ""}`}
            onClick={() => handleModeChange("consumer")}
          >
            CONSUMER_OS
          </button>
          <button 
            className={`mode-tab ${mode === "business" ? "active" : ""}`}
            onClick={() => handleModeChange("business")}
          >
            BUSINESS_PRO
          </button>
        </div>
        
        <div className="status highlight">
          {mode.toUpperCase()}_LINK_ACTIVE
        </div>
      </header>

      <main className="hud-grid">
        {/* LEFT PANEL: DATA ACQUISITION */}
        <section className="glass-card">
          {mode === "business" ? (
            <BusinessInputPanel 
              businessData={businessData} 
              setBusinessData={setBusinessData}
            />
          ) : (
            <ConsumerInputPanel 
              setInputs={setInputs}
              setFoundProducts={setFoundProducts}
            />
          )}
        </section>

        {/* CENTER PANEL: ANALYSIS HUD */}
        <section className="glass-card main-display">
          <Score 
            data={businessData?.analysis || results} 
            foundProducts={foundProducts}
            productName={businessData?.analysis ? "BUSINESS_ANALYSIS" : inputs.name} 
            mode={mode} 
          />
        </section>

        {/* RIGHT PANEL: OPTIMIZATION & ALTERNATIVES */}
        <section className="glass-card">
          {mode === "business" ? (
            <Simulator 
              currentResults={results} 
              baselineCarbon={baselineCarbon} 
            />
          ) : (
            <AlternativesPanel 
              foundProducts={foundProducts} 
            />
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
