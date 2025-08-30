"""
Gemini LLM Client with cost optimization
Uses Gemini 1.5 Flash for efficiency
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
import logging

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    print("Warning: google-generativeai not installed")

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client"""
    api_key: str
    model_name: str = "gemini-1.5-flash"  # Correct model name for Gemini Flash
    temperature: float = 0.3  # Lower temperature for consistent outputs
    max_tokens: int = 1000  # Limit response length
    cache_enabled: bool = True
    cache_dir: str = "/tmp/llm_cache"
    rate_limit_delay: float = 1.0  # Seconds between API calls


class GeminiClient:
    """
    Gemini LLM client with cost optimization features:
    - Response caching to avoid duplicate API calls
    - Rate limiting to prevent quota issues
    - Minimal token usage with Flash model
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            # Use environment variable or provided key
            api_key = os.environ.get('GEMINI_API_KEY', '')
            if not api_key:
                logger.warning("No API key provided. LLM features disabled.")
                self.enabled = False
                return
            
            config = LLMConfig(api_key=api_key)
        
        self.config = config
        self.enabled = genai is not None
        self._cache = {}
        self._last_call_time = 0
        self._call_count = 0
        
        if self.enabled:
            try:
                genai.configure(api_key=config.api_key)
                self.model = genai.GenerativeModel(config.model_name)
                logger.info(f"Initialized Gemini model: {config.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.enabled = False
        
        # Setup cache directory
        if config.cache_enabled:
            Path(config.cache_dir).mkdir(exist_ok=True)
    
    def analyze_data(self, data_description: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze data using LLM (cached to minimize API calls)
        
        Args:
            data_description: Brief description of the data
            analysis_type: Type of analysis needed
            
        Returns:
            Analysis results with insights
        """
        if not self.enabled:
            return {
                "error": "LLM not enabled",
                "suggestion": "Please set GEMINI_API_KEY environment variable"
            }
        
        # Create concise prompt to minimize tokens
        prompt = f"""Analyze this data (be concise, max 200 words):
Type: {analysis_type}
Data: {data_description[:500]}  # Limit description length

Provide:
1. Key insights (2-3 points)
2. Recommended actions (2-3 points)
Format as JSON."""
        
        # Check cache first
        cache_key = self._get_cache_key(prompt)
        if self.config.cache_enabled:
            cached = self._get_cached_response(cache_key)
            if cached:
                logger.info("Using cached LLM response")
                return cached
        
        # Rate limiting
        self._apply_rate_limit()
        
        try:
            # Make API call
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                }
            )
            
            self._call_count += 1
            
            # Parse response
            result = self._parse_response(response.text)
            
            # Cache the response
            if self.config.cache_enabled:
                self._cache_response(cache_key, result)
            
            logger.info(f"LLM call #{self._call_count} completed")
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "error": str(e),
                "fallback": "Using rule-based analysis instead"
            }
    
    def generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Generate insights from metrics (cached, minimal tokens)
        """
        if not self.enabled:
            return ["LLM insights not available - using rule-based analysis"]
        
        # Create very concise prompt
        metrics_str = json.dumps(metrics, indent=2)[:300]  # Limit size
        prompt = f"Given metrics: {metrics_str}\nList 3 key insights (one line each):"
        
        # Check cache
        cache_key = self._get_cache_key(prompt)
        if self.config.cache_enabled:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached.get("insights", [])
        
        # Rate limiting
        self._apply_rate_limit()
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,  # Lower for consistency
                    "max_output_tokens": 150,  # Very limited
                }
            )
            
            self._call_count += 1
            
            # Parse insights
            insights = response.text.strip().split('\n')
            insights = [i.strip('- •123.') for i in insights if i.strip()][:3]
            
            # Cache
            if self.config.cache_enabled:
                self._cache_response(cache_key, {"insights": insights})
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return [f"Analysis based on data patterns"]
    
    def suggest_visualizations(self, data_columns: List[str], data_types: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Suggest appropriate visualizations (cached)
        """
        if not self.enabled or len(data_columns) > 20:  # Skip for large datasets
            return self._fallback_viz_suggestions(data_columns, data_types)
        
        prompt = f"""Suggest 3 visualizations for data with columns: {', '.join(data_columns[:10])}
Output JSON list with 'type' and 'reason' for each. Be concise."""
        
        # Check cache
        cache_key = self._get_cache_key(prompt)
        if self.config.cache_enabled:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached.get("visualizations", [])
        
        # Rate limiting
        self._apply_rate_limit()
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 200,
                }
            )
            
            self._call_count += 1
            
            # Parse suggestions
            suggestions = self._parse_json_response(response.text)
            
            # Cache
            if self.config.cache_enabled:
                self._cache_response(cache_key, {"visualizations": suggestions})
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Visualization suggestion failed: {e}")
            return self._fallback_viz_suggestions(data_columns, data_types)
    
    def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self._last_call_time
        
        if time_since_last < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_call_time = time.time()
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available"""
        # In-memory cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # File cache
        cache_file = Path(self.config.cache_dir) / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    self._cache[cache_key] = data
                    return data
            except:
                pass
        
        return None
    
    def _cache_response(self, cache_key: str, response: Dict):
        """Cache response to memory and disk"""
        # Memory cache
        self._cache[cache_key] = response
        
        # File cache
        cache_file = Path(self.config.cache_dir) / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(response, f)
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response, handling various formats"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback to text parsing
            return {"analysis": text.strip()}
        except:
            return {"analysis": text.strip()}
    
    def _parse_json_response(self, text: str) -> List[Dict]:
        """Parse JSON list from response"""
        try:
            import re
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except:
            return []
    
    def _fallback_viz_suggestions(self, columns: List[str], data_types: Dict[str, str]) -> List[Dict[str, str]]:
        """Fallback visualization suggestions without LLM"""
        suggestions = []
        
        numeric_cols = [c for c, t in data_types.items() if 'float' in t or 'int' in t]
        
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter",
                "reason": "Compare relationships between numeric variables"
            })
        
        if numeric_cols:
            suggestions.append({
                "type": "histogram",
                "reason": "Show distribution of numeric data"
            })
        
        if len(columns) > 3:
            suggestions.append({
                "type": "heatmap",
                "reason": "Visualize correlations between variables"
            })
        
        return suggestions[:3]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "enabled": self.enabled,
            "model": self.config.model_name if self.enabled else None,
            "api_calls": self._call_count,
            "cache_size": len(self._cache),
            "estimated_cost": f"${self._call_count * 0.00015:.4f}"  # Rough estimate for Flash
        }