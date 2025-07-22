"""
LangGraph-based Competitive Intelligence Agent
"""

import os
from datetime import datetime
from typing import Dict, List

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage

from services.news_fetcher import NewsFetcher
from agents.signal_detector import SignalDetector
from simple_supabase import SimpleSupabase
from models.agent_state import CompetitiveIntelligenceState
from utils import azure_chat_model


class CompetitiveIntelligenceAgent:
    
    def __init__(self):
        self.llm = azure_chat_model()
        self.news_fetcher = NewsFetcher()
        self.signal_detector = SignalDetector(api_key=os.environ.get("OPENAI_API_KEY", ""))
        self.db = SimpleSupabase()
        
        # Initialize the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(CompetitiveIntelligenceState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("news_fetcher", self._news_fetcher_node)
        workflow.add_node("signal_analyzer", self._signal_analyzer_node)
        workflow.add_node("data_storage", self._data_storage_node)
        workflow.add_node("summarizer", self._summarizer_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow edges
        workflow.add_edge(START, "planner")
        workflow.add_conditional_edges(
            "planner",
            self._should_continue_planning,
            {
                "fetch_news": "news_fetcher",
                "error": "error_handler",
                "complete": END
            }
        )
        workflow.add_conditional_edges(
            "news_fetcher",
            self._should_continue_after_fetch,
            {
                "analyze": "signal_analyzer",
                "next_company": "planner",
                "error": "error_handler"
            }
        )
        workflow.add_conditional_edges(
            "signal_analyzer",
            self._should_continue_after_analysis,
            {
                "store": "data_storage",
                "next_article": "signal_analyzer",
                "next_company": "planner",
                "error": "error_handler"
            }
        )
        workflow.add_conditional_edges(
            "data_storage",
            self._should_continue_after_storage,
            {
                "next_company": "planner",
                "summarize": "summarizer",
                "error": "error_handler"
            }
        )
        workflow.add_edge("summarizer", END)
        workflow.add_edge("error_handler", END)
        
        # Compile with memory for state persistence
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _planner_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Planning node that decides what to do next"""
        
        companies = state.get("companies", [])
        current_company = state.get("current_company")
        fetched_articles = state.get("fetched_articles", {})
        
        # Initialize if first run
        if not current_company and companies:
            current_company = companies[0]
            state["current_company"] = current_company
            state["status"] = "fetching"
            state["progress"] = f"Starting analysis for {current_company} (1/{len(companies)})"
            state["fetched_articles"] = fetched_articles
            state["extracted_signals"] = state.get("extracted_signals", [])
            state["total_articles"] = state.get("total_articles", 0)
            state["total_signals"] = state.get("total_signals", 0)
            state["errors"] = state.get("errors", [])
            return state
        
        # Move to next company if current one is done
        if current_company in fetched_articles:
            current_idx = companies.index(current_company)
            if current_idx + 1 < len(companies):
                next_company = companies[current_idx + 1]
                state["current_company"] = next_company
                state["status"] = "fetching"
                state["progress"] = f"Starting analysis for {next_company} ({current_idx + 2}/{len(companies)})"
                return state
            else:
                # All companies processed, move to summary
                state["status"] = "complete"
                state["progress"] = "Analysis complete, generating summary..."
                return state
        
        return state
    
    def _news_fetcher_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Fetch news articles for the current company"""
        
        current_company = state["current_company"]
        days_back = state.get("days_back", 7)
        
        try:
            state["progress"] = f"Fetching news for {current_company}..."
            
            # Use the existing news fetcher
            articles = self.news_fetcher.fetch_multiple_sources(current_company, days_back)
            
            # Convert articles to dictionaries for state storage
            article_dicts = []
            for article in articles:
                article_dicts.append({
                    "title": article.title,
                    "link": article.link,
                    "text": article.text,
                    "published": article.published,
                    "published_on": article.published_on.isoformat() if article.published_on else None,
                    "platform_name": article.platform_name,
                    "source_type": article.source_type.value
                })
            
            state["fetched_articles"][current_company] = article_dicts
            state["total_articles"] = state.get("total_articles", 0) + len(articles)
            state["status"] = "analyzing"
            state["progress"] = f"Found {len(articles)} articles for {current_company}, extracting signals..."
            
        except Exception as e:
            error_msg = f"Error fetching news for {current_company}: {str(e)}"
            state["errors"].append(error_msg)
            state["status"] = "error"
            state["progress"] = error_msg
            
        return state
    
    def _signal_analyzer_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Extract signals from articles"""
        
        current_company = state["current_company"]
        articles = state["fetched_articles"].get(current_company, [])
        extracted_signals = state.get("extracted_signals", [])
        
        try:
            state["progress"] = f"Analyzing signals for {current_company}..."
            
            signals_found = 0
            
            # Process each article (limit to 10 for performance)
            for article in articles[:10]:
                try:
                    # Extract signal using the existing detector
                    signal = self.signal_detector.extract(current_company, article["text"])
                    
                    if signal:
                        # Convert to dictionary and add metadata
                        signal_dict = signal.dict()
                        signal_dict.update({
                            "company_name": current_company,
                            "source_url": article["link"],
                            "detected_at": datetime.now().isoformat(),
                        })
                        
                        extracted_signals.append(signal_dict)
                        signals_found += 1
                        
                except Exception as e:
                    # Log article processing error but continue
                    state["errors"].append(f"Error processing article for {current_company}: {str(e)}")
                    continue
            
            state["extracted_signals"] = extracted_signals
            state["total_signals"] = state.get("total_signals", 0) + signals_found
            state["status"] = "storing"
            state["progress"] = f"Found {signals_found} signals for {current_company}, storing data..."
            
        except Exception as e:
            error_msg = f"Error analyzing signals for {current_company}: {str(e)}"
            state["errors"].append(error_msg)
            state["status"] = "error"
            state["progress"] = error_msg
            
        return state
    
    def _data_storage_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Store extracted signals in Supabase"""
        
        try:
            state["progress"] = "Storing signals in database..."
            
            # Get signals for current company that haven't been stored yet
            current_company = state["current_company"]
            all_signals = state.get("extracted_signals", [])
            company_signals = [s for s in all_signals if s["company_name"] == current_company]
            
            stored_count = 0
            for signal_dict in company_signals:
                # Check if this signal has already been stored (to avoid duplicates)
                if not signal_dict.get("stored", False):
                    result = self.db.save_signal(signal_dict)
                    if result:
                        signal_dict["stored"] = True
                        stored_count += 1
            
            state["progress"] = f"Stored {stored_count} signals for {current_company}"
            state["status"] = "fetching"  # Ready for next company
            
        except Exception as e:
            error_msg = f"Error storing signals: {str(e)}"
            state["errors"].append(error_msg)
            state["status"] = "error"
            state["progress"] = error_msg
            
        return state
    
    def _summarizer_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Generate final summary and insights"""
        
        try:
            state["progress"] = "Generating summary and insights..."
            
            total_companies = len(state.get("companies", []))
            total_articles = state.get("total_articles", 0)
            total_signals = state.get("total_signals", 0)
            extracted_signals = state.get("extracted_signals", [])
            
            # Group signals by signal_type for summary
            signals_by_type = {}
            signals_by_company = {}
            
            for signal in extracted_signals:
                signal_type = signal.get("signal_type", "unknown")
                company = signal.get("company_name", "unknown")
                
                if signal_type not in signals_by_type:
                    signals_by_type[signal_type] = []
                signals_by_type[signal_type].append(signal)
                
                if company not in signals_by_company:
                    signals_by_company[company] = []
                signals_by_company[company].append(signal)
            
            # Generate AI insights using LLM
            insights_prompt = f"""
            Analyze these competitive intelligence results and provide strategic insights:
            
            Total Companies Analyzed: {total_companies}
            Total Articles Processed: {total_articles}
            Total Signals Detected: {total_signals}
            
            Signals by Type:
            {chr(10).join(f"- {sig_type}: {len(signals)} signals" for sig_type, signals in signals_by_type.items())}
            
            High-Impact Signals:
            {chr(10).join(f"- {sig['company_name']}: {sig['title']} ({sig['signal_type']})" for sig in extracted_signals if sig.get('impact') == 'high')[:5]}
            
            Provide:
            1. Key strategic insights from these signals
            2. Prioritized recommendations for customer success teams
            3. Notable trends or patterns
            4. Top 3 companies that need immediate attention
            """
            
            try:
                ai_insights = self.llm.invoke([HumanMessage(content=insights_prompt)])
                insights_text = ai_insights.content
            except Exception as e:
                insights_text = f"Unable to generate AI insights: {str(e)}"
            
            # Create comprehensive results
            results = {
                "summary": {
                    "total_companies": total_companies,
                    "total_articles": total_articles,
                    "total_signals": total_signals,
                    "companies_with_signals": len([c for c, s in signals_by_company.items() if len(s) > 0]),
                    "processing_errors": len(state.get("errors", []))
                },
                "signals_by_type": {
                    sig_type: {
                        "count": len(signals),
                        "companies": list(set(s["company_name"] for s in signals))
                    }
                    for sig_type, signals in signals_by_type.items()
                },
                "signals_by_company": {
                    company: {
                        "count": len(signals),
                        "types": list(set(s["signal_type"] for s in signals)),
                        "high_impact_count": len([s for s in signals if s.get("impact") == "high"])
                    }
                    for company, signals in signals_by_company.items()
                },
                "ai_insights": insights_text,
                "high_impact_signals": [
                    {
                        "company": s["company_name"],
                        "signal_type": s["signal_type"],
                        "title": s["title"],
                        "action": s["action"],
                        "impact": s["impact"]
                    }
                    for s in extracted_signals if s.get("impact") == "high"
                ][:10],
                "errors": state.get("errors", [])
            }
            
            state["results"] = results
            state["status"] = "complete"
            state["progress"] = f"✅ Analysis complete! Found {total_signals} signals across {total_companies} companies"
            
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            state["errors"].append(error_msg)
            state["status"] = "error"
            state["progress"] = error_msg
            
        return state
    
    def _error_handler_node(self, state: CompetitiveIntelligenceState) -> CompetitiveIntelligenceState:
        """Handle errors and provide recovery options"""
        
        errors = state.get("errors", [])
        state["status"] = "error"
        state["progress"] = f"❌ Errors occurred: {len(errors)} issues found"
        
        # Create error summary
        error_summary = {
            "error_count": len(errors),
            "errors": errors,
            "partial_results": {
                "total_articles": state.get("total_articles", 0),
                "total_signals": state.get("total_signals", 0),
                "companies_processed": len(state.get("fetched_articles", {}))
            }
        }
        
        state["results"] = error_summary
        return state
    
    # Conditional edge functions
    def _should_continue_planning(self, state: CompetitiveIntelligenceState) -> str:
        """Decide what to do after planning"""
        status = state.get("status", "pending")
        if status == "error":
            return "error"
        elif status == "complete":
            return "complete"
        else:
            return "fetch_news"
    
    def _should_continue_after_fetch(self, state: CompetitiveIntelligenceState) -> str:
        """Decide what to do after fetching news"""
        status = state.get("status", "pending")
        if status == "error":
            return "error"
        elif status == "analyzing":
            return "analyze"
        else:
            return "next_company"
    
    def _should_continue_after_analysis(self, state: CompetitiveIntelligenceState) -> str:
        """Decide what to do after signal analysis"""
        status = state.get("status", "pending")
        if status == "error":
            return "error"
        elif status == "storing":
            return "store"
        else:
            return "next_company"
    
    def _should_continue_after_storage(self, state: CompetitiveIntelligenceState) -> str:
        """Decide what to do after storing data"""
        status = state.get("status", "pending")
        current_company = state.get("current_company")
        companies = state.get("companies", [])
        
        if status == "error":
            return "error"
        
        # Check if this is the last company
        if current_company and companies:
            current_idx = companies.index(current_company)
            if current_idx + 1 >= len(companies):
                return "summarize"
        
        return "next_company"
    
    async def run_analysis(
        self, 
        companies: List[str], 
        days_back: int = 7,
        thread_id: str = "default"
    ) -> Dict:
        """Run the competitive intelligence analysis"""
        
        # Initial state
        initial_state = CompetitiveIntelligenceState(
            companies=companies,
            days_back=days_back,
            current_company=None,
            fetched_articles={},
            extracted_signals=[],
            total_articles=0,
            total_signals=0,
            errors=[],
            status="pending",
            progress="Initializing analysis...",
            results={}
        )
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the workflow
        final_state = await self.graph.ainvoke(initial_state, config)
        
        return final_state
    
    def run_analysis_sync(
        self, 
        companies: List[str], 
        days_back: int = 7,
        thread_id: str = "default"
    ) -> Dict:
        """Synchronous version of run_analysis"""
        
        # Initial state
        initial_state = CompetitiveIntelligenceState(
            companies=companies,
            days_back=days_back,
            current_company=None,
            fetched_articles={},
            extracted_signals=[],
            total_articles=0,
            total_signals=0,
            errors=[],
            status="pending",
            progress="Initializing analysis...",
            results={}
        )
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state, config)
        
        return final_state


def create_competitive_intelligence_agent() -> CompetitiveIntelligenceAgent:
    """Factory function to create a competitive intelligence agent"""
    return CompetitiveIntelligenceAgent()


# CLI interface for testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        print("🤖 LANGGRAPH COMPETITIVE INTELLIGENCE AGENT")
        print("=" * 60)
        
        agent = create_competitive_intelligence_agent()
        
        # Test companies
        test_companies = ["Salesforce", "Databricks", "OpenAI"]
        
        print(f"🔍 Analyzing {len(test_companies)} companies...")
        
        # Run analysis
        result = await agent.run_analysis(test_companies, days_back=7)
        
        print(f"\n📊 {result['progress']}")
        
        if result.get("results"):
            results = result["results"]
            if "summary" in results:
                summary = results["summary"]
                print(f"   📰 Articles: {summary.get('total_articles', 0)}")
                print(f"   🚨 Signals: {summary.get('total_signals', 0)}")
                print(f"   🏢 Companies with signals: {summary.get('companies_with_signals', 0)}")
            
            if "high_impact_signals" in results:
                high_impact = results["high_impact_signals"][:3]
                if high_impact:
                    print(f"\n🚨 Top High-Impact Signals:")
                    for signal in high_impact:
                        print(f"   • {signal['company']}: {signal['title']}")
    
    # Run the async main function
    asyncio.run(main())
