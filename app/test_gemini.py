from app.chatbot.model_client import GeminiModelClient


def main():
    client = GeminiModelClient()

    print("Running Gemini health check...")
    result = client.health_check()
    print(result)

    print("\nTesting text generation...")
    response = client.generate_text(
        "Explain a failed bank transfer in one short sentence."
    )
    print(response)


if __name__ == "__main__":
    main()