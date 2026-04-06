export const fetchProductData = async (barcode) => {
  try {
    const response = await fetch(`https://world.openfoodfacts.org/api/v2/product/${barcode}`);
    const data = await response.json();

    if (data.status === 1 && data.product) {
      const p = data.product;
      
      // Accessing the environmental impact data provided in your JSON sample
      const agri = p.agribalyse || {};

      return {
        id: barcode,
        name: p.product_name || "UNKNOWN_PRODUCT",
        // Extracting specific CO2 metrics for the calcEngine
        // Using logical OR fallbacks to ensure the demo never breaks
        materialVal: parseFloat(agri.co2_agriculture) || 0.5, 
        transportVal: parseFloat(agri.co2_transportation) || 0.1,
        packagingVal: parseFloat(agri.co2_packaging) || 0.05,
        categoryVal: parseFloat(agri.co2_processing) || 0.1,
        
        // Metadata for the Score and Alternatives panels
        apiEcoScore: p.ecoscore_score || 0,
        apiGrade: p.ecoscore_grade || 'u',
        image: p.image_front_url || "",
        co2Total: agri.co2_total || 0
      };
    }
    return null;
  } catch (err) {
    console.error("API_LINK_FAILURE // CHECK_NETWORK_STATUS : ",err);
    return null;
  }
};
