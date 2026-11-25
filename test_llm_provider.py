"""Test LLM provider manager."""

from modules.llm_provider import get_llm_manager

# Test initialization
print("Testing LLM Provider Manager...")
manager = get_llm_manager()
print("✅ LLM Manager initialized successfully")

# Check provider status
statuses = manager.get_provider_status()
print(f"\n📊 Provider Status:")
print(f"  Groq: {'✅ Configured' if statuses['groq'].connected else '❌ Not configured'}")
print(f"  Gemini: {'✅ Configured' if statuses['gemini'].connected else '❌ Not configured'}")

# Check active provider
active = manager.get_configured_provider()
print(f"\n🎯 Active Provider: {active.upper()}")

# Test simple generation (if any provider available)
if manager.is_groq_configured() or manager.is_gemini_configured():
    print("\n🧪 Testing generation...")
    response = manager.generate(
        prompt="Say 'Hello from ActiPulse AI' in one sentence.",
        temperature=0.5,
        max_tokens=50,
    )
    
    if response.success:
        print(f"✅ Generation successful!")
        print(f"  Provider: {response.provider_used}")
        print(f"  Model: {response.model_used}")
        print(f"  Response: {response.text[:100]}...")
    else:
        print(f"❌ Generation failed: {response.error_message}")
else:
    print("\n⚠️ No providers configured. Set API keys in .env file.")

print("\n✨ Test complete!")
