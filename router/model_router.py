from .task_classifier import TaskClassifier
from models import ModelFactory, BaseModelClient
from core.intelligence.learningEngine import LearningEngine
from core.intelligence.routingMemory import RoutingMemory

class ModelRouter:
    """The Dynamic Model Selection Engine (DMSE) for Gaia v2. Now Self-Learning."""
    
    def __init__(self, classifier: TaskClassifier = None):
        self.classifier = classifier or TaskClassifier()
        self.learning_engine = LearningEngine(RoutingMemory())
        
        self.clients = {
            "claude": ModelFactory.get_client("claude"),
            "gemini": ModelFactory.get_client("gemini"),
            "codex": ModelFactory.get_client("codex")
        }

    def route(self, objective: str) -> dict:
        classification = self.classifier.classify(objective)
        category = classification.get("category", "coding")
        complexity = classification.get("complexity", 5)
        is_multimodal = classification.get("is_multimodal", False)
        
        # Determine logical fallback based on heuristics
        fallback_model = "gemini"
        if is_multimodal:
            fallback_model = "gemini"
        elif category == "reasoning" or complexity >= 8:
            fallback_model = "claude"
        elif category in ["coding", "debugging", "system_operations"]:
            fallback_model = "codex"
        elif category == "summarization":
            fallback_model = "gemini"

        # Ask the Learning Engine for the best model based on experience
        selected_model = self.learning_engine.get_best_model(category, fallback_model)
        
        # Ensure we don't accidentally select 'local' from learning history if it was used before
        if selected_model == "local":
            selected_model = fallback_model

        if selected_model == fallback_model:
            reasoning = f"Using cloud fallback ({fallback_model}). Learning Engine has low data for category '{category}'."
        else:
            confidence = self.learning_engine.calculate_confidence(selected_model, category)
            reasoning = f"Learning Engine selected {selected_model} for '{category}' with confidence {confidence:.2f}% based on past experience."

        return {
            "client": self.clients.get(selected_model, self.clients["gemini"]),
            "model_type": selected_model,
            "reasoning": reasoning,
            "classification": classification
        }

    def get_client(self, model_type: str) -> BaseModelClient:
        return self.clients.get(model_type, self.clients["gemini"])
