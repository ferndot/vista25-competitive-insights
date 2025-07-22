"""
LLM-based result deduplication service
"""

import os
from typing import List, Set, Tuple
from loguru import logger

from models.model import Result, DeduplicationResult
from utils import azure_chat_model


class ResultDeduplicator:
    """Uses LLM to detect duplicate results that report on the same event"""

    def __init__(self):
        self.llm = azure_chat_model().with_structured_output(DeduplicationResult)
    
    def _normalize_datetime(self, dt):
        """Convert timezone-aware datetime to timezone-naive for comparison"""
        return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

    def deduplicate_results(self, results: List[Result]) -> List[Result]:
        """
        Remove duplicate results using LLM-based semantic comparison.
        Returns list of unique results.

        Always uses clustering approach for consistency:
        - First does fast similarity grouping by keywords/dates
        - Then uses LLM only to compare within similar groups
        """
        if len(results) <= 1:
            return results

        logger.info(f"Deduplicating {len(results)} results using clustering approach")

        # Always use clustering approach for consistency
        return self._deduplicate_with_clustering(results)

    def _deduplicate_direct_comparison(self, results: List[Result]) -> List[Result]:
        """Direct pairwise comparison for small result sets"""
        
        # Keep track of which results are duplicates
        duplicate_indices: Set[int] = set()
        
        # Compare each pair of results
        for i in range(len(results)):
            if i in duplicate_indices:
                continue
                
            for j in range(i + 1, len(results)):
                if j in duplicate_indices:
                    continue
                    
                # Compare results i and j
                is_duplicate = self._compare_results(results[i], results[j])
                
                if is_duplicate:
                    # Mark the newer one as duplicate (keep the older one)
                    dt_i = self._normalize_datetime(results[i].published_on)
                    dt_j = self._normalize_datetime(results[j].published_on)
                    
                    if dt_i >= dt_j:
                        duplicate_indices.add(i)
                        logger.debug(f"Marking result {i} as duplicate of {j}")
                        break  # Stop comparing this result
                    else:
                        duplicate_indices.add(j)
                        logger.debug(f"Marking result {j} as duplicate of {i}")

        # Return only non-duplicate results
        unique_results = [
            result for i, result in enumerate(results) 
            if i not in duplicate_indices
        ]
        
        logger.info(f"Direct comparison complete: {len(results)} → {len(unique_results)} results")
        return unique_results
    
    def _deduplicate_with_clustering(self, results: List[Result]) -> List[Result]:
        """
        Clustering-based deduplication for larger result sets.
        Groups similar results first, then uses LLM within groups.
        """
        
        logger.info("Using clustering approach for large result set")
        
        # Group results by similarity (date proximity + keyword overlap)
        clusters = self._create_similarity_clusters(results)
        
        logger.info(f"Created {len(clusters)} similarity clusters")
        
        # Deduplicate within each cluster using LLM
        all_unique_results = []
        
        for cluster_id, cluster_results in clusters.items():
            if len(cluster_results) == 1:
                # Single result clusters are automatically unique
                all_unique_results.extend(cluster_results)
            else:
                # Use LLM to deduplicate within cluster
                logger.debug(f"Deduplicating cluster {cluster_id} with {len(cluster_results)} results")
                unique_in_cluster = self._deduplicate_direct_comparison(cluster_results)
                all_unique_results.extend(unique_in_cluster)
        
        logger.info(f"Clustering deduplication complete: {len(results)} → {len(all_unique_results)} results")
        return all_unique_results
    
    def _create_similarity_clusters(self, results: List[Result]) -> dict:
        """
        Group results into clusters based on fast similarity metrics:
        - Published within similar timeframe (±2 days)
        - Share significant keyword overlap
        """
        clusters = {}
        cluster_id = 0
        
        for result in results:
            # Find existing cluster this result should join
            assigned_cluster = None
            
            for cid, cluster_results in clusters.items():
                # Check if result is similar to any result in this cluster
                for cluster_result in cluster_results[:3]:  # Check first few results only
                    if self._are_potentially_similar(result, cluster_result):
                        assigned_cluster = cid
                        break
                
                if assigned_cluster:
                    break
            
            # Add to existing cluster or create new one
            if assigned_cluster is not None:
                clusters[assigned_cluster].append(result)
            else:
                clusters[cluster_id] = [result]
                cluster_id += 1
        
        return clusters
    
    def _are_potentially_similar(self, result1: Result, result2: Result) -> bool:
        """
        Fast similarity check for clustering.
        Uses date proximity and keyword overlap.
        """
        
        # Check date proximity (within 3 days)
        dt1 = self._normalize_datetime(result1.published_on)
        dt2 = self._normalize_datetime(result2.published_on)
        
        time_diff = abs((dt1 - dt2).total_seconds())
        if time_diff > 3 * 24 * 3600:  # 3 days in seconds
            return False
        
        # Check keyword overlap
        title1_words = set(result1.title.lower().split())
        title2_words = set(result2.title.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'will', 'would', 'could', 'should'}
        title1_words -= common_words
        title2_words -= common_words
        
        if not title1_words or not title2_words:
            return False
        
        # Calculate overlap
        intersection = title1_words.intersection(title2_words)
        union = title1_words.union(title2_words)
        
        overlap_ratio = len(intersection) / len(union) if union else 0
        
        # Consider similar if >30% overlap
        return overlap_ratio > 0.2

    def _compare_results(self, result1: Result, result2: Result) -> bool:
        """
        Compare two results to determine if they're about the same event.
        Returns True if they are duplicates.
        """
        try:
            # Create comparison prompt
            prompt = self._create_comparison_prompt(result1, result2)
            
            # Get LLM response
            result: DeduplicationResult = self.llm.invoke(prompt)
            
            logger.debug(f"Comparison result: {result.is_duplicate} "
                        f"(confidence: {result.confidence:.2f}) - {result.reason}")
            
            # Consider it a duplicate if confidence is high enough
            return result.is_duplicate and result.confidence >= 0.6
            
        except Exception as e:
            logger.error(f"Error comparing results: {e}")
            # Fall back to simple title comparison
            return self._simple_title_comparison(result1, result2)

    def _create_comparison_prompt(self, result1: Result, result2: Result) -> str:
        """Create a prompt for comparing two results"""
        
        return f"""
You are an expert at identifying whether two results are reporting on the same underlying business event.

Compare these two results and determine if they are about the same event:

**result 1:**
Title: {result1.title}
Source: {result1.platform_name} ({result1.source_type.value})
Published: {result1.published}
Content Preview: {result1.text[:500]}...

**result 2:**
Title: {result2.title}  
Source: {result2.platform_name} ({result2.source_type.value})
Published: {result2.published}
Content Preview: {result2.text[:500]}...

**Instructions:**
- results are about the "same event" if they report on the same specific business occurrence (e.g., same acquisition, same executive departure, same funding round, same earnings report)
- results are NOT duplicates if they discuss the same company but different events
- results are NOT duplicates if they discuss the same topic generally but different specific incidents
- Consider timing: results published close together are more likely to be about the same event
- Consider source types: regulatory filings vs news results about the same event are still duplicates

Examples of SAME event:
- Two results about "Company X acquires Company Y for $100M"  
- SEC filing announcing CEO departure + news result about the same CEO departure
- Multiple outlets reporting the same earnings results

Examples of DIFFERENT events:
- Two different funding rounds by the same company
- Two different executive departures at the same company
- General company analysis vs specific event reporting

Provide your assessment with confidence level and reasoning.
"""

    def _simple_title_comparison(self, result1: Result, result2: Result) -> bool:
        """Fallback simple comparison based on title similarity"""
        title1 = result1.title.lower()[:50]
        title2 = result2.title.lower()[:50]
        
        # Calculate simple similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        
        logger.debug(f"Fallback title similarity: {similarity:.2f}")
        return similarity > 0.7
