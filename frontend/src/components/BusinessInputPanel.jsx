import { useState } from "react";
import "../styles/BusinessInputPanel.css";

const API_BASE_URL = "http://localhost:8000";

const getApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}?_t=${Date.now()}`;

const BusinessInputPanel = ({ businessData, setBusinessData }) => {
  const [formData, setFormData] = useState({
    category: "electronics",
    material: "plastic",
    transport: "truck_long",
    packaging: "plastic_wrap",
    units_per_year: 1000
  });

  const [analysis, setAnalysis] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [simulation, setSimulation] = useState(null);
  const [optimalConfig, setOptimalConfig] = useState(null);
  const [investorReport, setInvestorReport] = useState(null);
  const [loading, setLoading] = useState(false);

  // Material options
  const materialOptions = [
    { value: "plastic", label: "Plastic" },
    { value: "recycled_plastic", label: "Recycled Plastic" },
    { value: "bioplastic", label: "Bioplastic" },
    { value: "glass", label: "Glass" },
    { value: "recycled_glass", label: "Recycled Glass" },
    { value: "aluminum", label: "Aluminum" },
    { value: "recycled_aluminum", label: "Recycled Aluminum" },
    { value: "steel", label: "Steel" },
    { value: "recycled_steel", label: "Recycled Steel" },
    { value: "paper", label: "Paper" },
    { value: "recycled_paper", label: "Recycled Paper" },
    { value: "cardboard", label: "Cardboard" },
    { value: "bamboo", label: "Bamboo" },
    { value: "wood", label: "Wood" },
    { value: "cotton", label: "Cotton" },
    { value: "organic_cotton", label: "Organic Cotton" }
  ];

  // Transport options
  const transportOptions = [
    { value: "air", label: "Air Freight" },
    { value: "truck_long", label: "Long-Haul Truck" },
    { value: "truck_local", label: "Local Truck" },
    { value: "rail", label: "Rail" },
    { value: "sea", label: "Sea Freight" },
    { value: "local", label: "Local Sourcing" }
  ];

  // Packaging options
  const packagingOptions = [
    { value: "plastic_wrap", label: "Plastic Wrap" },
    { value: "plastic_bottle", label: "Plastic Bottle" },
    { value: "plastic_bag", label: "Plastic Bag" },
    { value: "paper_wrap", label: "Paper Wrap" },
    { value: "cardboard", label: "Cardboard" },
    { value: "glass_bottle", label: "Glass Bottle" },
    { value: "metal_can", label: "Metal Can" },
    { value: "biodegradable", label: "Biodegradable" },
    { value: "minimal", label: "Minimal Packaging" },
    { value: "bulk", label: "Bulk Packaging" }
  ];

  // Category options
  const categoryOptions = [
    { value: "electronics", label: "Electronics" },
    { value: "clothing", label: "Clothing" },
    { value: "food", label: "Food & Beverage" },
    { value: "furniture", label: "Furniture" },
    { value: "general", label: "General Products" }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const analyzeCurrent = async () => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl("/api/business/analyze"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.analysis);
        setSuggestions(data.suggestions);
        setBusinessData(data);
      } else {
        console.error("Analysis failed:", response.status);
      }
    } catch (error) {
      console.error("Analysis error:", error);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async (proposedChanges) => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl("/api/business/simulate"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current: formData,
          proposed: { ...formData, ...proposedChanges }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSimulation(data);
      } else {
        console.error("Simulation failed:", response.status);
      }
    } catch (error) {
      console.error("Simulation error:", error);
    } finally {
      setLoading(false);
    }
  };

  const findOptimal = async () => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl("/api/business/optimize"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setOptimalConfig(data);
      } else {
        console.error("Optimization failed:", response.status);
      }
    } catch (error) {
      console.error("Optimization error:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl("/api/business/investor-report"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setInvestorReport(data);
      } else {
        console.error("Report generation failed:", response.status);
      }
    } catch (error) {
      console.error("Report error:", error);
    } finally {
      setLoading(false);
    }
  };

  const applySuggestion = (suggestion) => {
    const changes = {};
    if (suggestion.type === "material") {
      changes.material = suggestion.suggestion;
    } else if (suggestion.type === "transport") {
      changes.transport = suggestion.suggestion;
    } else if (suggestion.type === "packaging") {
      changes.packaging = suggestion.suggestion;
    }
    
    setFormData(prev => ({ ...prev, ...changes }));
    runSimulation(changes);
  };

  return (
    <div className="business-input-panel">
      <div className="input-section">
        <h2 className="section-title">PRODUCT_INPUT</h2>
        
        <div className="form-grid">
          <div className="form-group">
            <label>CATEGORY</label>
            <select 
              value={formData.category} 
              onChange={(e) => handleInputChange("category", e.target.value)}
              className="form-select"
            >
              {categoryOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>MATERIAL</label>
            <select 
              value={formData.material} 
              onChange={(e) => handleInputChange("material", e.target.value)}
              className="form-select"
            >
              {materialOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>TRANSPORT</label>
            <select 
              value={formData.transport} 
              onChange={(e) => handleInputChange("transport", e.target.value)}
              className="form-select"
            >
              {transportOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>PACKAGING</label>
            <select 
              value={formData.packaging} 
              onChange={(e) => handleInputChange("packaging", e.target.value)}
              className="form-select"
            >
              {packagingOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>UNITS_PER_YEAR</label>
            <input 
              type="number" 
              value={formData.units_per_year} 
              onChange={(e) => handleInputChange("units_per_year", parseInt(e.target.value) || 1000)}
              className="form-input"
              min="1"
            />
          </div>
        </div>

        <div className="action-buttons">
          <button onClick={analyzeCurrent} disabled={loading} className="btn btn-primary">
            {loading ? "ANALYZING..." : "ANALYZE"}
          </button>
          <button onClick={findOptimal} disabled={loading} className="btn btn-secondary">
            {loading ? "OPTIMIZING..." : "FIND_OPTIMAL"}
          </button>
          <button onClick={generateReport} disabled={loading} className="btn btn-tertiary">
            {loading ? "GENERATING..." : "INVESTOR_REPORT"}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="analysis-section">
          <h3 className="section-title">SUSTAINABILITY_ANALYSIS</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">ECO_SCORE</span>
              <span className="metric-value">{analysis.score}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">CARBON_FOOTPRINT</span>
              <span className="metric-value">{analysis.carbon} kg CO2</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">VERDICT</span>
              <span className="metric-value verdict">{analysis.verdict}</span>
            </div>
          </div>

          {/* Contribution Breakdown */}
          <div className="breakdown-section">
            <h4>CONTRIBUTION_BREAKDOWN</h4>
            <div className="breakdown-grid">
              <div className="breakdown-item">
                <span className="breakdown-label">Material</span>
                <span className="breakdown-value">{analysis.breakdown.material.contribution}%</span>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-label">Transport</span>
                <span className="breakdown-value">{analysis.breakdown.transport.contribution}%</span>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-label">Packaging</span>
                <span className="breakdown-value">{analysis.breakdown.packaging.contribution}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Optimization Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions-section">
          <h3 className="section-title">OPTIMIZATION_SUGGESTIONS</h3>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-card">
                <div className="suggestion-content">
                  <span className="suggestion-type">{suggestion.type.toUpperCase()}</span>
                  <span className="suggestion-text">{suggestion.suggestion}</span>
                  <span className="suggestion-impact">Impact: {suggestion.impact}</span>
                </div>
                <div className="suggestion-metrics">
                  <span className="score-improvement">+{suggestion.score_improvement} pts</span>
                  <span className="carbon-reduction">-{suggestion.carbon_reduction}% CO2</span>
                </div>
                <button 
                  onClick={() => applySuggestion(suggestion)}
                  className="btn btn-small"
                >
                  APPLY
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Simulation Results */}
      {simulation && (
        <div className="simulation-section">
          <h3 className="section-title">WHAT_IF_SIMULATION</h3>
          <div className="comparison-grid">
            <div className="comparison-card current">
              <h4>CURRENT</h4>
              <div className="metrics">
                <span>Score: {simulation.current.score}</span>
                <span>Carbon: {simulation.current.carbon} kg CO2</span>
              </div>
            </div>
            <div className="comparison-card proposed">
              <h4>PROPOSED</h4>
              <div className="metrics">
                <span>Score: {simulation.proposed.score}</span>
                <span>Carbon: {simulation.proposed.carbon} kg CO2</span>
              </div>
            </div>
          </div>
          <div className="improvements">
            <span className="improvement">Score Improvement: +{simulation.improvements.score_improvement_percentage}%</span>
            <span className="improvement">Carbon Reduction: -{simulation.improvements.carbon_reduction_percentage}%</span>
            <span className="improvement">Annual Savings: {simulation.scale_impact.total_carbon_savings} kg CO2</span>
          </div>
        </div>
      )}

      {/* Optimal Configuration */}
      {optimalConfig && (
        <div className="optimal-section">
          <h3 className="section-title">BEST_CONFIGURATION</h3>
          <div className="optimal-config">
            <div className="config-details">
              <span>Material: {optimalConfig.optimal_configuration.material}</span>
              <span>Transport: {optimalConfig.optimal_configuration.transport}</span>
              <span>Packaging: {optimalConfig.optimal_configuration.packaging}</span>
            </div>
            <div className="optimal-metrics">
              <span>Best Score: {optimalConfig.optimal_analysis.score}</span>
              <span>Improvement: +{optimalConfig.potential_improvement.improvement_percentage}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Investor Report */}
      {investorReport && (
        <div className="investor-section">
          <h3 className="section-title">INVESTOR_REPORT</h3>
          <div className="investor-summary">
            <div className="report-metric">
              <span>Current Performance</span>
              <span>{investorReport.current_performance.score} pts</span>
            </div>
            <div className="report-metric">
              <span>Potential Improvement</span>
              <span>+{investorReport.potential_performance.improvement_percentage}%</span>
            </div>
            <div className="report-metric">
              <span>Market Position</span>
              <span>{investorReport.market_position}</span>
            </div>
            <div className="report-metric">
              <span>Investment Priority</span>
              <span>{investorReport.investment_priority}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BusinessInputPanel;
