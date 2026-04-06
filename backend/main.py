from fastapi import FastAPI, HTTPException
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="EcoScore API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_SEARCH_API_KEY = os.getenv("OPENROUTER_SEARCH_API_KEY")
OPENROUTER_BUSINESS_API_KEY = os.getenv("OPENROUTER_BUSINESS_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# Data models
class Product(BaseModel):
    name: str
    score: Optional[int] = None
    carbon: Optional[float] = None
    verdict: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class AlternativesRequest(BaseModel):
    product_name: str
    product_category: str = "general"


class EcoScoreRequest(BaseModel):
    products: List[Product]


# Business models
class BusinessInput(BaseModel):
    category: str
    material: str
    transport: str
    packaging: str
    units_per_year: Optional[int] = 1000


class SimulationRequest(BaseModel):
    current: BusinessInput
    proposed: BusinessInput


class EcoScoreResponse(BaseModel):
    products: List[Product]
    total_score: int
    total_carbon: float
    overall_verdict: str


# Helper functions
def calculate_eco_score(product_name: str, category: str = "general") -> dict:
    """Advanced eco score calculation based on multiple factors"""

    # Base scores by category
    category_baselines = {
        "electronics": {"min": 30, "max": 80, "avg_carbon": 25.0},
        "clothing": {"min": 40, "max": 85, "avg_carbon": 15.0},
        "food": {"min": 50, "max": 95, "avg_carbon": 8.0},
        "furniture": {"min": 25, "max": 75, "avg_carbon": 30.0},
        "general": {"min": 35, "max": 80, "avg_carbon": 20.0},
    }

    baseline = category_baselines.get(category.lower(), category_baselines["general"])

    # Scoring factors
    eco_positive_keywords = {
        "organic": 15,
        "recycled": 12,
        "sustainable": 10,
        "eco": 8,
        "green": 7,
        "bamboo": 10,
        "solar": 15,
        "wind": 12,
        "biodegradable": 8,
        "compostable": 8,
        "fair trade": 6,
        "local": 5,
        "natural": 4,
        "renewable": 10,
        "zero waste": 12,
    }

    eco_negative_keywords = {
        "plastic": -10,
        "disposable": -12,
        "single-use": -15,
        "fast fashion": -8,
        "synthetic": -6,
        "artificial": -4,
        "chemical": -5,
        "toxic": -10,
        "polluting": -12,
        "wasteful": -8,
        "non-recyclable": -10,
        "hazardous": -15,
    }

    # Start with baseline score
    score = (baseline["min"] + baseline["max"]) // 2
    carbon = baseline["avg_carbon"]

    # Analyze product name for keywords
    name_lower = product_name.lower()

    # Apply positive factors
    for keyword, points in eco_positive_keywords.items():
        if keyword in name_lower:
            score += points
            carbon *= 0.85  # 15% carbon reduction

    # Apply negative factors
    for keyword, points in eco_negative_keywords.items():
        if keyword in name_lower:
            score += points
            carbon *= 1.20  # 20% carbon increase

    # Brand-specific adjustments
    sustainable_brands = {
        "patagonia": 10,
        "allbirds": 8,
        "tentree": 12,
        "veja": 7,
        "fairphone": 15,
        "dell": 5,
        "hp": 4,
        "apple": 2,
        "samsung": 1,
        "nike": 0,
        "adidas": 1,
        "h&m": -5,
        "zara": -6,
        "shein": -10,
    }

    for brand, points in sustainable_brands.items():
        if brand in name_lower:
            score += points
            if points > 0:
                carbon *= 0.9  # 10% reduction for sustainable brands
            else:
                carbon *= 1.1  # 10% increase for unsustainable brands

    # Material-based adjustments
    material_impacts = {
        "cotton": {"score": 2, "carbon": 1.1},
        "organic cotton": {"score": 8, "carbon": 0.7},
        "polyester": {"score": -5, "carbon": 1.3},
        "recycled polyester": {"score": 3, "carbon": 0.8},
        "aluminum": {"score": -3, "carbon": 1.2},
        "recycled aluminum": {"score": 6, "carbon": 0.6},
        "glass": {"score": 1, "carbon": 1.0},
        "recycled glass": {"score": 5, "carbon": 0.7},
        "steel": {"score": -4, "carbon": 1.4},
        "recycled steel": {"score": 4, "carbon": 0.8},
    }

    for material, impact in material_impacts.items():
        if material in name_lower:
            score += impact["score"]
            carbon *= impact["carbon"]

    # Ensure score stays within bounds
    score = max(0, min(100, score))

    # Ensure minimum carbon values
    carbon = max(1.0, carbon)

    # Determine verdict based on score
    if score >= 80:
        verdict = "SUSTAINABLE"
    elif score >= 60:
        verdict = "MODERATE"
    elif score >= 40:
        verdict = "CONCERNING"
    else:
        verdict = "UNSUSTAINABLE"

    return {
        "score": round(score),
        "carbon": round(carbon, 2),
        "verdict": verdict,
        "factors": {
            "category": category,
            "keywords_found": [
                k for k in eco_positive_keywords.keys() if k in name_lower
            ]
            + [k for k in eco_negative_keywords.keys() if k in name_lower],
            "brand_adjustment": any(
                brand in name_lower for brand in sustainable_brands.keys()
            ),
        },
    }


# Business-specific functions
def calculate_business_eco_score(business_input: BusinessInput) -> dict:
    """Calculate eco score for business inputs"""

    # Material impact scoring
    material_scores = {
        "plastic": {"score": 20, "carbon": 15.0},
        "recycled_plastic": {"score": 45, "carbon": 8.0},
        "bioplastic": {"score": 55, "carbon": 6.0},
        "glass": {"score": 60, "carbon": 10.0},
        "recycled_glass": {"score": 75, "carbon": 5.0},
        "aluminum": {"score": 40, "carbon": 12.0},
        "recycled_aluminum": {"score": 70, "carbon": 4.0},
        "steel": {"score": 35, "carbon": 18.0},
        "recycled_steel": {"score": 65, "carbon": 7.0},
        "paper": {"score": 70, "carbon": 3.0},
        "recycled_paper": {"score": 85, "carbon": 1.5},
        "cardboard": {"score": 75, "carbon": 2.5},
        "bamboo": {"score": 90, "carbon": 1.0},
        "wood": {"score": 65, "carbon": 4.0},
        "cotton": {"score": 60, "carbon": 8.0},
        "organic_cotton": {"score": 80, "carbon": 4.0},
    }

    # Transport impact scoring
    transport_scores = {
        "air": {"score": 15, "carbon": 25.0},
        "truck_long": {"score": 35, "carbon": 15.0},
        "truck_local": {"score": 55, "carbon": 8.0},
        "rail": {"score": 70, "carbon": 5.0},
        "sea": {"score": 60, "carbon": 6.0},
        "local": {"score": 85, "carbon": 2.0},
    }

    # Packaging impact scoring
    packaging_scores = {
        "plastic_wrap": {"score": 25, "carbon": 5.0},
        "plastic_bottle": {"score": 30, "carbon": 8.0},
        "plastic_bag": {"score": 20, "carbon": 3.0},
        "paper_wrap": {"score": 70, "carbon": 1.5},
        "cardboard": {"score": 75, "carbon": 2.0},
        "glass_bottle": {"score": 65, "carbon": 4.0},
        "metal_can": {"score": 60, "carbon": 5.0},
        "biodegradable": {"score": 85, "carbon": 1.0},
        "minimal": {"score": 90, "carbon": 0.5},
        "bulk": {"score": 95, "carbon": 0.2},
    }

    # Get scores for each component
    material_data = material_scores.get(
        business_input.material.lower(), {"score": 50, "carbon": 10.0}
    )
    transport_data = transport_scores.get(
        business_input.transport.lower(), {"score": 50, "carbon": 10.0}
    )
    packaging_data = packaging_scores.get(
        business_input.packaging.lower(), {"score": 50, "carbon": 5.0}
    )

    # Calculate weighted average
    weights = {"material": 0.5, "transport": 0.3, "packaging": 0.2}
    total_score = (
        material_data["score"] * weights["material"]
        + transport_data["score"] * weights["transport"]
        + packaging_data["score"] * weights["packaging"]
    )

    total_carbon = (
        material_data["carbon"] * weights["material"]
        + transport_data["carbon"] * weights["transport"]
        + packaging_data["carbon"] * weights["packaging"]
    )

    # Determine verdict
    if total_score >= 80:
        verdict = "SUSTAINABLE"
    elif total_score >= 60:
        verdict = "MODERATE"
    elif total_score >= 40:
        verdict = "CONCERNING"
    else:
        verdict = "UNSUSTAINABLE"

    return {
        "score": round(total_score),
        "carbon": round(total_carbon, 2),
        "verdict": verdict,
        "breakdown": {
            "material": {
                "score": material_data["score"],
                "carbon": material_data["carbon"],
                "contribution": round(material_data["score"] * weights["material"]),
            },
            "transport": {
                "score": transport_data["score"],
                "carbon": transport_data["carbon"],
                "contribution": round(transport_data["score"] * weights["transport"]),
            },
            "packaging": {
                "score": packaging_data["score"],
                "carbon": packaging_data["carbon"],
                "contribution": round(packaging_data["score"] * weights["packaging"]),
            },
        },
    }


def generate_optimization_suggestions(business_input: BusinessInput) -> list:
    """Generate optimization suggestions for business"""
    suggestions = []

    # Material suggestions
    if business_input.material.lower() in ["plastic", "steel", "aluminum"]:
        suggestions.append(
            {
                "type": "material",
                "suggestion": f"Switch to recycled_{business_input.material}",
                "impact": "High",
                "score_improvement": 25,
                "carbon_reduction": 40,
            }
        )

    if business_input.material.lower() == "plastic":
        suggestions.append(
            {
                "type": "material",
                "suggestion": "Switch to bioplastic or bamboo",
                "impact": "Very High",
                "score_improvement": 35,
                "carbon_reduction": 60,
            }
        )

    # Transport suggestions
    if business_input.transport.lower() in ["air", "truck_long"]:
        suggestions.append(
            {
                "type": "transport",
                "suggestion": "Switch to rail or sea transport",
                "impact": "Medium",
                "score_improvement": 20,
                "carbon_reduction": 50,
            }
        )

    if business_input.transport.lower() != "local":
        suggestions.append(
            {
                "type": "transport",
                "suggestion": "Optimize for local sourcing",
                "impact": "High",
                "score_improvement": 30,
                "carbon_reduction": 70,
            }
        )

    # Packaging suggestions
    if business_input.packaging.lower().startswith("plastic"):
        suggestions.append(
            {
                "type": "packaging",
                "suggestion": "Switch to paper or cardboard packaging",
                "impact": "Medium",
                "score_improvement": 25,
                "carbon_reduction": 60,
            }
        )

    if business_input.packaging.lower() not in ["minimal", "bulk", "biodegradable"]:
        suggestions.append(
            {
                "type": "packaging",
                "suggestion": "Use biodegradable or minimal packaging",
                "impact": "Medium",
                "score_improvement": 20,
                "carbon_reduction": 40,
            }
        )

    return suggestions


async def call_openrouter(
    prompt: str, use_search_key: bool = False, use_business_key: bool = False
) -> str:
    """Call OpenRouter API for AI assistance"""
    # Choose appropriate API key
    if use_business_key:
        api_key = OPENROUTER_BUSINESS_API_KEY
        key_type = "business"
    elif use_search_key:
        api_key = OPENROUTER_SEARCH_API_KEY
        key_type = "search"
    else:
        api_key = OPENROUTER_API_KEY
        key_type = "alternatives"

    if not api_key:
        raise HTTPException(
            status_code=500, detail=f"OpenRouter {key_type} API key not configured"
        )

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "system",
                "content": "You are an environmental sustainability expert. Provide concise, accurate responses about products and their eco-friendly alternatives.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter API error: {str(e)}")


# API Endpoints
@app.get("/")
async def root():
    return {"message": "EcoScore API is running"}


@app.post("/test")
async def test_endpoint():
    return {"status": "ok", "message": "Backend is working"}


@app.post("/api/search-products")
async def search_products(request: SearchRequest):
    """Search for products using AI"""
    print(f"Received search request: {request}")  # Debug line
    if not request.query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    prompt = f"""You are a product search specialist with expertise in finding everyday consumer products and their environmental impact. Search for products related to: "{request.query}"

Use your knowledge to find real, specific products that consumers commonly purchase. For each product, provide accurate environmental scoring based on:
- Material composition and sustainability
- Manufacturing processes and carbon footprint
- Brand reputation for environmental responsibility
- Packaging and transportation impact
- Certifications (organic, fair trade, recycled content, etc.)

Return a JSON array of product objects with this exact structure:
[
    {{
        "name": "Specific Product Name with Brand",
        "category": "electronics|clothing|food|furniture|general",
        "environmental_notes": "Brief note on why this product's score"
    }},
    {{
        "name": "Another Specific Product",
        "category": "electronics|clothing|food|furniture|general", 
        "environmental_notes": "Environmental impact assessment"
    }}
]

Find exactly {request.limit} relevant products. Include both popular options and more sustainable alternatives when available. Be specific with brand names and product types.
Only return the JSON array, no other text or explanations.
"""

    try:
        response = await call_openrouter(
            prompt, use_search_key=True
        )  # Use search API key

        # Try to parse JSON response
        products = json.loads(response)

        # Calculate eco scores for each product
        scored_products = []
        for product in products:
            eco_data = calculate_eco_score(product["name"], product["category"])
            scored_products.append(
                {
                    "name": product["name"],
                    "category": product["category"],
                    "environmental_notes": product.get("environmental_notes", ""),
                    **eco_data,
                }
            )

        return {"products": scored_products}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from AI service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/get-alternatives")
async def get_alternatives(request: AlternativesRequest):
    """Get eco-friendly alternatives for a product"""
    if not request.product_name:
        raise HTTPException(status_code=400, detail="Product name is required")

    prompt = f"""You are a food health and environmental sustainability evaluator specializing in carbon footprint analysis. For the product "{request.product_name}" (category: {request.product_category}), suggest 3-4 more carbon-friendly and sustainable alternatives.

Return a JSON array with this exact structure:
[
    {{
        "name": "Alternative Product 1", 
        "reason": "Why it's more sustainable and carbon-friendly",
        "carbon_reduction": 5.2
    }},
    {{
        "name": "Alternative Product 2", 
        "reason": "Why it's more sustainable and carbon-friendly", 
        "carbon_reduction": 3.8
    }}
]

Focus on real, available products that are genuinely better for the environment. carbon_reduction should be in kg CO2 saved compared to the original product. Be specific about environmental benefits.
Only return the JSON array, no other text.
"""

    try:
        response = await call_openrouter(prompt)
        alternatives = json.loads(response)

        # Calculate eco scores for alternatives
        scored_alternatives = []
        original_eco = calculate_eco_score(
            request.product_name, request.product_category
        )

        for alt in alternatives:
            eco_data = calculate_eco_score(alt["name"], request.product_category)
            # Adjust carbon based on reduction
            eco_data["carbon"] = max(1.0, eco_data["carbon"] - alt["carbon_reduction"])
            scored_alternatives.append(
                {
                    "name": alt["name"],
                    "reason": alt["reason"],
                    "carbon_change": -alt["carbon_reduction"],  # Negative for reduction
                    **eco_data,
                }
            )

        return {"alternatives": scored_alternatives}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid response from AI service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate-product-score")
async def calculate_product_score(request: dict):
    """Calculate eco score for a manually added product"""
    product_name = request.get("product_name", "")
    category = request.get("category", "general")

    if not product_name:
        raise HTTPException(status_code=400, detail="Product name is required")

    # Use the advanced scoring algorithm
    eco_data = calculate_eco_score(product_name, category)

    return {
        "name": product_name,
        "category": category,
        "environmental_notes": "Manually added product - score calculated by algorithm",
        **eco_data,
    }


@app.post("/api/calculate-total-score", response_model=EcoScoreResponse)
async def calculate_total_score(request: EcoScoreRequest):
    """Calculate total eco score for multiple products"""
    if not request.products:
        raise HTTPException(status_code=400, detail="Products list is required")

    total_score = 0
    total_carbon = 0.0
    scored_products = []

    for product in request.products:
        if product.score is None or product.carbon is None:
            # Calculate if not provided
            eco_data = calculate_eco_score(product.name)
            product.score = eco_data["score"]
            product.carbon = eco_data["carbon"]
            product.verdict = eco_data["verdict"]

        total_score += product.score
        total_carbon += product.carbon
        scored_products.append(product)

    # Calculate averages and overall verdict
    avg_score = total_score // len(request.products)
    avg_carbon = total_carbon / len(request.products)

    if avg_score >= 80:
        overall_verdict = "SUSTAINABLE"
    elif avg_score >= 60:
        overall_verdict = "MODERATE"
    else:
        overall_verdict = "UNSUSTAINABLE"

    return EcoScoreResponse(
        products=scored_products,
        total_score=avg_score,
        total_carbon=round(avg_carbon, 2),
        overall_verdict=overall_verdict,
    )


# Business API Endpoints
@app.post("/api/business/analyze")
async def analyze_business_input(request: BusinessInput):
    """Analyze business input and calculate eco score"""
    try:
        result = calculate_business_eco_score(request)
        suggestions = generate_optimization_suggestions(request)

        return {"analysis": result, "suggestions": suggestions, "input": request.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/business/simulate")
async def simulate_what_if(request: SimulationRequest):
    """Simulate what-if scenarios"""
    try:
        current_analysis = calculate_business_eco_score(request.current)
        proposed_analysis = calculate_business_eco_score(request.proposed)

        # Calculate improvements
        score_improvement = proposed_analysis["score"] - current_analysis["score"]
        carbon_reduction = current_analysis["carbon"] - proposed_analysis["carbon"]
        score_improvement_percentage = (
            (score_improvement / current_analysis["score"]) * 100
            if current_analysis["score"] > 0
            else 0
        )
        carbon_reduction_percentage = (
            (carbon_reduction / current_analysis["carbon"]) * 100
            if current_analysis["carbon"] > 0
            else 0
        )

        # Calculate scale impact
        units_per_year = request.current.units_per_year or 1000
        total_carbon_savings = carbon_reduction * units_per_year

        return {
            "current": current_analysis,
            "proposed": proposed_analysis,
            "improvements": {
                "score_improvement": score_improvement,
                "carbon_reduction": carbon_reduction,
                "score_improvement_percentage": round(score_improvement_percentage, 2),
                "carbon_reduction_percentage": round(carbon_reduction_percentage, 2),
                "total_carbon_savings_per_year": round(total_carbon_savings, 2),
            },
            "scale_impact": {
                "units_per_year": units_per_year,
                "total_carbon_savings": round(total_carbon_savings, 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/business/optimize")
async def find_optimal_configuration(request: BusinessInput):
    """Find the optimal configuration"""
    try:
        # Define optimal options for each category
        materials = [
            "recycled_paper",
            "bamboo",
            "recycled_steel",
            "recycled_aluminum",
            "recycled_glass",
        ]
        transports = ["local", "rail", "sea"]
        packagings = ["bulk", "minimal", "biodegradable"]

        best_score = 0
        best_config = None
        best_analysis = None

        # Test combinations (simplified for performance)
        for material in materials[:3]:  # Limit combinations for speed
            for transport in transports[:2]:
                for packaging in packagings[:2]:
                    test_config = BusinessInput(
                        category=request.category,
                        material=material,
                        transport=transport,
                        packaging=packaging,
                        units_per_year=request.units_per_year,
                    )

                    analysis = calculate_business_eco_score(test_config)
                    if analysis["score"] > best_score:
                        best_score = analysis["score"]
                        best_config = test_config
                        best_analysis = analysis

        # Calculate improvement from current
        current_analysis = calculate_business_eco_score(request)
        improvement = best_analysis["score"] - current_analysis["score"]
        improvement_percentage = (
            (improvement / current_analysis["score"]) * 100
            if current_analysis["score"] > 0
            else 0
        )

        return {
            "optimal_configuration": best_config.dict() if best_config else None,
            "optimal_analysis": best_analysis,
            "current_analysis": current_analysis,
            "potential_improvement": {
                "score_improvement": improvement,
                "improvement_percentage": round(improvement_percentage, 2),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BestProductRequest(BaseModel):
    product_name: str
    product_category: str = "general"


@app.post("/api/best-product-auto")
async def best_product_auto(request: BestProductRequest):
    """
    Given a product name, fetch alternatives and return the best product
    along with an explanation from the LLM why it's the better choice.
    """
    if not request.product_name:
        raise HTTPException(status_code=400, detail="Product name is required")

    # 1. Calculate main product eco score
    main_eco = calculate_eco_score(request.product_name, request.product_category)
    main_product = Product(
        name=request.product_name,
        score=main_eco["score"],
        carbon=main_eco["carbon"],
        verdict=main_eco["verdict"],
    )

    # 2. Fetch AI alternatives
    try:
        prompt_request = AlternativesRequest(
            product_name=request.product_name,
            product_category=request.product_category,
        )
        response = await get_alternatives(prompt_request)
        alternatives_data = response.get("alternatives", [])

        alternatives = [
            Product(
                name=alt["name"],
                score=alt.get("score"),
                carbon=alt.get("carbon"),
                verdict=alt.get("verdict"),
            )
            for alt in alternatives_data
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch alternatives: {str(e)}"
        )

    # 3. Combine main + alternatives and pick best
    all_products = [main_product] + alternatives
    scored_products = []
    for p in all_products:
        if p.score is None or p.carbon is None:
            eco_data = calculate_eco_score(p.name, request.product_category)
            p.score = eco_data["score"]
            p.carbon = eco_data["carbon"]
            p.verdict = eco_data["verdict"]
        scored_products.append(p)

    # Sort by score descending, then carbon ascending
    best_product = sorted(scored_products, key=lambda x: (-x.score, x.carbon))[0]

    # 4. Ask LLM for explanation why this is the best choice
    explanation_prompt = f"""
    You are an environmental sustainability expert. 
    Among the following products: {[p.name for p in scored_products]}, 
    the one selected as best is '{best_product.name}'. 
    Provide a concise, clear explanation why it is the better eco-friendly choice compared to the others,
    focusing on carbon footprint, sustainability of materials, packaging, and transport.
    """

    try:
        explanation = await call_openrouter(explanation_prompt)
    except Exception:
        explanation = "Explanation could not be generated."

    return {
        "best_product": {
            "name": best_product.name,
            "score": best_product.score,
            "carbon": best_product.carbon,
            "verdict": best_product.verdict,
            "explanation": explanation.strip(),
        },
        "alternatives_considered": [
            p.name for p in scored_products if p.name != best_product.name
        ],
    }


@app.post("/api/business/investor-report")
async def generate_investor_report(request: BusinessInput):
    """Generate investor report"""
    try:
        analysis = calculate_business_eco_score(request)
        suggestions = generate_optimization_suggestions(request)

        # Find best suggestion
        best_suggestion = (
            max(suggestions, key=lambda x: x["score_improvement"])
            if suggestions
            else None
        )

        # Calculate potential improvements
        potential_score = analysis["score"] + (
            best_suggestion["score_improvement"] if best_suggestion else 0
        )
        improvement_percentage = (
            ((potential_score - analysis["score"]) / analysis["score"]) * 100
            if analysis["score"] > 0
            else 0
        )

        return {
            "current_performance": analysis,
            "potential_performance": {
                "score": potential_score,
                "improvement_percentage": round(improvement_percentage, 2),
            },
            "top_recommendation": best_suggestion,
            "market_position": (
                "Above Average" if analysis["score"] >= 60 else "Needs Improvement"
            ),
            "investment_priority": (
                "High"
                if analysis["score"] < 50
                else "Medium" if analysis["score"] < 70 else "Low"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

