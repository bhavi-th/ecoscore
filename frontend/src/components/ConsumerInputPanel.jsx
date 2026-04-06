import { useState, useEffect, useRef } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { fetchProductData } from '../utils/api';
import "../styles/ConsumerInputPanel.css";

const API_BASE_URL = "http://localhost:8000";
const getApiUrl = (endpoint) => `${API_BASE_URL}${endpoint}?_t=${Date.now()}`;

const ConsumerInputPanel = ({ setInputs, foundProducts, setFoundProducts }) => {
  // --- SCANNER STATE ---
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);

  // --- SEARCH STATE ---
  const [productName, setProductName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownKey, setDropdownKey] = useState(0);

  const dropdownRef = useRef(null);

  // Helper to update both HUD and History
  const processProductSelection = (productData) => {
    // 1. Update main App state to refresh Score HUD
    setInputs(productData);

    // 2. Add to history for comparison
    setFoundProducts(prev => {
      if (prev.find(p => p.name === productData.name)) return prev;
      return [{ id: Date.now() + Math.random(), ...productData }, ...prev];
    });
  };

  // --- SCANNER LOGIC ---
  const handleScanSuccess = async (decodedText, scanner) => {
    try {
      const productData = await fetchProductData(decodedText);
      if (productData) {
        processProductSelection(productData);
        scanner.clear();
        setIsScanning(false);
      } else {
        setError("PRODUCT_NOT_FOUND_IN_DATABASE");
      }
    } catch (err) {
      setError("NETWORK_PROTOCOL_ERROR");
      console.error(err);
    }
  };

  useEffect(() => {
    let scanner = null;
    if (isScanning) {
      scanner = new Html5QrcodeScanner("reader", {
        fps: 15,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      });
      scanner.render(
        async (text) => {
          setError(null);
          await handleScanSuccess(text, scanner);
        },
        (err) => console.log(err)
      );
    }
    return () => {
      if (scanner) {
        scanner.clear().catch(e => console.error("Scanner clear failed", e));
      }
    };
  }, [isScanning]);

  // --- SEARCH LOGIC ---
  const searchProducts = async (query) => {
    if (!query.trim()) return;
    setIsSearching(true);
    try {
      const response = await fetch(getApiUrl("/api/search-products"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 5 }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.products || []);
        setShowDropdown(true);
      }
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchClick = () => {
    if (productName.trim()) {
      setDropdownKey(prev => prev + 1);
      searchProducts(productName);
    }
  };

  const handleManualAdd = async () => {
    if (!productName.trim()) return;
    try {
      const response = await fetch(getApiUrl("/api/calculate-product-score"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_name: productName, category: "general" }),
      });
      
      if (response.ok) {
        const data = await response.json();
        processProductSelection(data);
        setProductName("");
      }
    } catch (err) {
      console.error("Manual add error:", err);
    }
  };

  return (
    <div className="consumer-input-panel">
      {/* SCANNER SECTION */}
      <div className="scanner-container">
        <h2 className="highlight">OPTIC_LINK</h2>
        {isScanning ? (
          <div className="scanner-viewport">
            <div id="reader"></div>
            <button className="hud-button abort-btn" onClick={() => setIsScanning(false)}>TERMINATE</button>
          </div>
        ) : (
          <button className="hud-button init-scan" onClick={() => setIsScanning(true)}>INITIALIZE_SCANNER</button>
        )}
      </div>

      <hr className="divider" />

      {/* SEARCH SECTION */}
      <div className="input-group">
        <label className="label highlight">SEARCH_DATABASE</label>
        <div className="search-row">
          <input
            type="text"
            className="product-input"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            onFocus={() => setShowDropdown(false)}
            placeholder="Search product name..."
          />
          <button className="search-button" onClick={handleSearchClick} disabled={isSearching}>
            {isSearching ? "..." : "SEARCH"}
          </button>
        </div>

        {showDropdown && searchResults.length > 0 && (
          <div className="search-dropdown" ref={dropdownRef} key={dropdownKey}>
            {searchResults.map((product, index) => (
              <div key={index} className="search-result-item" onClick={() => processProductSelection(product)}>
                <div className="search-result-info">
                  <div className="search-result-name">{product.name}</div>
                  <div className="search-result-meta">Score: {product.score} | {product.carbon} kg CO2</div>
                </div>
                <button className="add-btn">+</button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* HISTORY LIST */}
      {foundProducts?.length > 0 && (
        <div className="added-products">
          <h4 className="added-products-title">ACTIVE_SESSION_DATA</h4>
          <div className="products-list">
            {foundProducts.map((p) => (
              <div key={p.id} className="added-product-item">
                <div className="product-info">
                  <div className="product-name">{p.name}</div>
                  <div className="product-score">Score: {p.score} | {p.carbon} kg CO2</div>
                </div>
                <button className="remove-button" onClick={() => setFoundProducts(prev => prev.filter(item => item.id !== p.id))}>×</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="manual-add-section">
        <button className="manual-button" onClick={handleManualAdd} disabled={!productName.trim()}>ADD_MANUAL_ENTRY</button>
      </div>

      {error && <div className="error-msg highlight">[!] ERROR: {error}</div>}
    </div>
  );
};

export default ConsumerInputPanel;
