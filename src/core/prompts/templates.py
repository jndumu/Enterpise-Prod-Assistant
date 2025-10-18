"""Ultra-concise prompts for semantic search."""

# Web search prompt
WEB_PROMPT = "Answer '{query}' using:\n{context}\nBe factual, under 100 words:"

# Semantic search prompt  
SEMANTIC_PROMPT = "Using this data: {context}\nAnswer: {query}"

# Groq system message
GROQ_SYSTEM = "Provide accurate, concise answers only from given information."