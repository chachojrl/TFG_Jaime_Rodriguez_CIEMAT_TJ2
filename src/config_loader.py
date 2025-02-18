def load_keywords(filename="./config/keywords.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]

def load_signal_options(filename="./config/signal_options.txt"):
    """Loads valid signal names from a file."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
