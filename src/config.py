# Models and settings used in the experiment (one place to change them)
ANSWER_MODEL = "openai/gpt-oss-20b"
ANSWER_EFFORT = "low"          # fixed in every run, so reasoning tokens stay comparable
JUDGE_MODEL = "qwen/qwen3.8-27b"   # different model family than the answering model
JUDGE_EFFORT = "none"

# Baseline agent settings
BASELINE_CHUNK_WORDS = 300     # about 400 tokens
BASELINE_TOP_K = 8
BASELINE_THRESHOLD = 0.0

# Output control (variant B)
CONCISE_MAX_TOKENS = 300       # diz includes the hidden reasoning tokens
