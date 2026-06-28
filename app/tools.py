import httpx
from langchain.tools import tool
from cachetools import TTLCache
from app.config import settings
from app.rag import retrieval_chain

# In-memory TTL caches
stock_cache = TTLCache(maxsize=100, ttl=300)        # 5 minutes TTL for prices
overview_cache = TTLCache(maxsize=100, ttl=86400)   # 24 hours TTL for company info
symbol_cache = TTLCache(maxsize=200, ttl=86400)     # 24 hours TTL for search

def clean_company_query(query: str) -> str:
    q = query.lower().replace("?", "").replace(",", " ")

    remove_words = {
        "what", "is", "the", "latest", "stock", "price", "of",
        "give", "me", "company", "overview", "for", "tell",
        "about", "share", "data", "show"
    }

    words = q.split()
    filtered = [word for word in words if word not in remove_words]
    return " ".join(filtered).strip()

def looks_like_ticker(text: str) -> bool:
    text = text.strip().upper()
    return text.isalpha() and 1 <= len(text) <= 5

async def fetch_api(params: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.ALPHA_VANTAGE_BASE_URL, params=params, timeout=20.0)
        response.raise_for_status()
        return response.json()

async def search_symbol_from_query(query: str) -> dict | None:
    cleaned_query = clean_company_query(query)

    if not cleaned_query:
        return None

    if looks_like_ticker(cleaned_query):
        return {
            "symbol": cleaned_query.upper(),
            "name": cleaned_query.upper(),
            "match_score": "1.0000"
        }

    # Check cache
    if cleaned_query in symbol_cache:
        return symbol_cache[cleaned_query]

    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": cleaned_query,
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }

    try:
        data = await fetch_api(params)
    except Exception:
        return None

    matches = data.get("bestMatches", [])
    if not matches:
        return None

    best_match = matches[0]
    result = {
        "symbol": best_match.get("1. symbol"),
        "name": best_match.get("2. name"),
        "region": best_match.get("4. region"),
        "currency": best_match.get("8. currency"),
        "match_score": best_match.get("9. matchScore")
    }
    symbol_cache[cleaned_query] = result
    return result

@tool
async def get_stock_price(query: str) -> str:
    """Get the latest daily stock data for any market-listed company or ticker symbol."""
    symbol_data = await search_symbol_from_query(query)

    if not symbol_data or not symbol_data.get("symbol"):
        return "Could not find a matching stock symbol for your query."

    symbol = symbol_data["symbol"]

    # Check cache
    if symbol in stock_cache:
        return stock_cache[symbol]

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }

    try:
        data = await fetch_api(params)
    except Exception as e:
        return f"Error retrieving stock data: {str(e)}"

    if "Error Message" in data:
        return f"Invalid stock symbol: {symbol}"
    if "Note" in data:
        return "API rate limit reached. Please try again later."

    series = data.get("Time Series (Daily)")
    if not series:
        return f"No daily stock data found for {symbol}."

    latest_date = sorted(series.keys(), reverse=True)[0]
    latest = series[latest_date]

    result = (
        f"Best match: {symbol_data.get('name', symbol)} "
        f"({symbol}, score={symbol_data.get('match_score', 'N/A')}). "
        f"Latest available daily data on {latest_date}: "
        f"open={latest['1. open']}, high={latest['2. high']}, "
        f"low={latest['3. low']}, close={latest['4. close']}, "
        f"volume={latest['5. volume']}."
    )
    stock_cache[symbol] = result
    return result

@tool
async def get_company_overview(query: str) -> str:
    """Get company overview for any market-listed company or ticker symbol."""
    symbol_data = await search_symbol_from_query(query)

    if not symbol_data or not symbol_data.get("symbol"):
        return "Could not find a matching company symbol."

    symbol = symbol_data["symbol"]

    # Check cache
    if symbol in overview_cache:
        return overview_cache[symbol]

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }

    try:
        data = await fetch_api(params)
    except Exception as e:
        return f"Error retrieving company overview: {str(e)}"

    if not data or "Symbol" not in data:
        return f"Company overview not found for {symbol}."

    result = (
        f"Best match: {symbol_data.get('name', symbol)} "
        f"({symbol}, score={symbol_data.get('match_score', 'N/A')}). "
        f"Overview: name={data.get('Name')}, sector={data.get('Sector')}, "
        f"industry={data.get('Industry')}, market_cap={data.get('MarketCapitalization')}, "
        f"pe_ratio={data.get('PERatio')}, currency={symbol_data.get('currency', 'N/A')}."
    )
    overview_cache[symbol] = result
    return result

@tool
async def search_finance_docs(query: str) -> str:
    """Search finance documents using RAG."""
    result = await retrieval_chain.ainvoke({"input": query})
    return result["answer"]

@tool
def calculate_sip(amount: float, return_rate: float, duration_years: int) -> str:
    """Calculates the future value of a Systematic Investment Plan (SIP)."""
    monthly_rate = return_rate / 12 / 100
    months = duration_years * 12
    if monthly_rate == 0:
        future_value = amount * months
    else:
        future_value = amount * ((((1 + monthly_rate) ** months) - 1) / monthly_rate) * (1 + monthly_rate)
    total_investment = amount * months
    wealth_gained = future_value - total_investment
    return f"SIP Result: Total Investment: ₹{total_investment:,.2f}, Wealth Gained: ₹{wealth_gained:,.2f}, Expected Amount: ₹{future_value:,.2f}"

@tool
def calculate_emi(principal: float, rate: float, tenure_years: int) -> str:
    """Calculates the Equated Monthly Installment (EMI) for a loan."""
    monthly_rate = rate / 12 / 100
    months = tenure_years * 12
    if monthly_rate == 0:
        emi = principal / months
    else:
        emi = (principal * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)
    total_payable = emi * months
    total_interest = total_payable - principal
    return f"EMI Result: Monthly EMI: ₹{emi:,.2f}, Total Interest: ₹{total_interest:,.2f}, Total Payable: ₹{total_payable:,.2f}"

@tool
def assess_risk_profile(age: int, income: float, savings: float, horizon_years: int, appetite: str) -> str:
    """Assesses the user's investment risk profile based on their demographics and preferences."""
    score = 0
    if age < 30: score += 3
    elif age < 50: score += 2
    else: score += 1

    if horizon_years > 10: score += 3
    elif horizon_years > 5: score += 2
    else: score += 1

    appetite_lower = appetite.lower()
    if 'high' in appetite_lower or 'aggressive' in appetite_lower: score += 3
    elif 'medium' in appetite_lower or 'moderate' in appetite_lower: score += 2
    else: score += 1

    if score >= 8: profile = "Aggressive"
    elif score >= 5: profile = "Moderate"
    else: profile = "Conservative"
    
    return f"Risk Assessment: Based on the provided details, the calculated risk profile is '{profile}'."

@tool
def generate_budget(monthly_income: float) -> str:
    """Generates a simple 50/30/20 budget plan based on monthly income."""
    needs = monthly_income * 0.50
    wants = monthly_income * 0.30
    savings = monthly_income * 0.20
    return f"Budget Plan (50/30/20 Rule): Needs: ₹{needs:,.2f}, Wants: ₹{wants:,.2f}, Savings/Investing: ₹{savings:,.2f}"