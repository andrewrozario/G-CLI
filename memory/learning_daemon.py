import threading
import time
import logging
import urllib.parse
from bs4 import BeautifulSoup
from models.base_client import BaseModelClient
from memory.vector_db import VectorMemory

class AutonomousLearningDaemon:
    """
    A background process that actively researches unknown topics and ingests them.
    It scrapes the internet for documentation, extracts reasoning, and stores it in the memory substrate.
    """
    def __init__(self, llm: BaseModelClient, memory: VectorMemory, interval_seconds: int = 300):
        self.llm = llm
        self.memory = memory
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.thread = None
        self.learning_queue = [
            "Advanced microservices architecture patterns",
            "Local LLM tool calling reasoning",
            "Vector database RAG optimizations",
            "High performance Rust web servers"
        ] # Initial seed topics

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._learning_loop, daemon=True)
            self.thread.start()
            logging.info("Autonomous Learning Daemon started.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
            logging.info("Autonomous Learning Daemon stopped.")

    def queue_topic(self, topic: str):
        if topic not in self.learning_queue:
            self.learning_queue.append(topic)

    def _learning_loop(self):
        while self.is_running:
            if self.learning_queue:
                topic = self.learning_queue.pop(0)
                try:
                    self._research_and_ingest(topic)
                except Exception as e:
                    logging.error(f"ALE Error researching {topic}: {e}")
            time.sleep(self.interval_seconds)

    def _research_and_ingest(self, topic: str):
        logging.info(f"ALE researching: {topic}")
        
        # 1. Search the web
        try:
            import requests
            url = "https://html.duckduckgo.com/html/"
            payload = {'q': f"{topic} architecture tutorial documentation"}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.post(url, data=payload, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            results = []
            for a in soup.find_all('a', class_='result__snippet', href=True):
                link = a['href']
                if link.startswith('//duckduckgo.com/l/?'):
                    parsed = urllib.parse.urlparse(link)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    link = query_params.get('uddg', [''])[0]
                results.append(link)
                if len(results) >= 1: # Just scrape the top result for speed
                    break
                    
            if not results:
                return

            best_url = results[0]
            page_res = requests.get(best_url, headers=headers, timeout=10)
            page_soup = BeautifulSoup(page_res.text, 'html.parser')
            
            text = " ".join([p.text for p in page_soup.find_all('p')])
            text = text[:4000] # Limit size for local LLM context
            
            # 2. Extract Reasoning using LLM
            prompt = f"Topic: {topic}\nSource Content:\n{text}\n\nExtract the core architectural reasoning, design patterns, and implicit knowledge. Explain how and why these patterns work."
            reasoning = self.llm.generate(prompt, system="You are Gaia's Autonomous Learning Engine.")
            
            # 3. Store in Memory Substrate
            if reasoning and len(reasoning) > 50:
                doc_id = f"ale_{hash(topic)}"
                self.memory.add_memory(
                    text=f"Reasoning for {topic}:\n{reasoning}\nSource: {best_url}",
                    metadata={"type": "reasoning", "topic": topic, "source": "ALE"},
                    doc_id=doc_id,
                    collection_name="reasoning"
                )
                logging.info(f"ALE successfully ingested reasoning for: {topic}")
                
        except ImportError:
            logging.error("Missing required packages for ALE: requests, beautifulsoup4")
        except Exception as e:
            logging.error(f"ALE failed during research of {topic}: {e}")
