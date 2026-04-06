import { useState, useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { fetchProductData } from '../utils/api';
import "../styles/InputPanel.css";

const ConsumerInputPanel = ({ setInputs, setFoundProducts }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);

  const handleScanSuccess = async (decodedText, scanner) => {
    try {
      const productData = await fetchProductData(decodedText);
      
      if (productData) {
        // 1. Update main App state to refresh Score HUD
        setInputs(productData);

        // 2. Add to history for the Alternatives comparison
        setFoundProducts(prev => {
          // Avoid duplicates in the history list
          if (prev.find(p => p.id === decodedText)) return prev;
          return [{ id: decodedText, ...productData }, ...prev];
        });

        // Stop scanner after success to show results
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
      // Initialize scanner with a square box optimized for QR codes
      scanner = new Html5QrcodeScanner("reader", {
        fps: 15,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      });

      scanner.render(
        async (decodedText) => {
          setError(null);
          await handleScanSuccess(decodedText, scanner);
        },
        (err) => {
          // Silent failure during continuous scanning
          console.log(err);
        }
      );
    }

    return () => {
      if (scanner) {
        scanner.clear().catch(error => console.error("Scanner clear failed", error));
      }
    };
  }, [isScanning]);
  return (
    <div className="input-panel consumer-theme">
      <div className="scanner-header">
        <h2 className="highlight">CONSUMER_SCAN_MODE</h2>
        <p className="small-text">// TARGET: QR_CODE / BARCODE</p>
      </div>

      {isScanning ? (
        <div className="scanner-viewport">
          <div id="reader"></div>
          <button 
            className="hud-button abort-btn" 
            onClick={() => setIsScanning(false)}
          >
            TERMINATE_SCAN
          </button>
        </div>
      ) : (
        <div className="init-view">
          <div className="scan-placeholder">
            <div className="scan-line"></div>
          </div>
          <button 
            className="hud-button init-scan" 
            onClick={() => setIsScanning(true)}
          >
            INITIALIZE_OPTIC_LINK
          </button>
        </div>
      )}

      {error && (
        <div className="error-msg highlight">
          [!] ERROR: {error}
        </div>
      )}

      <div className="system-note">
        <p className="small-text">// ENABLING_REAL_TIME_ANALYSIS</p>
      </div>
    </div>
  );
};

export default ConsumerInputPanel;
