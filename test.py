from podcastfy.client import generate_podcast
        
# Test URLs (using examples from the README)
test_urls = [
    "https://www.perplexity.ai/discover/top/us-threatens-to-block-mexican-z3cvmqPrSkKwQX_Gszki4A",  # Personal website example from README
]

print(f"📡 Generating podcast from URLs: {test_urls}")
custom_config = {
    "word_count": 125,
    "conversation_style": ["casual", "humorous"],
    "podcast_name": "Tech Chuckles",
    "creativity": 0.7
}
# Generate podcast
audio_file = generate_podcast(urls=test_urls,tts_model="gemini",conversation_config=custom_config)

print(f"✅ Podcast generated successfully: {audio_file}")

# Save the audio file to a local directory

print("✅ Podcast saved to podcast.mp3")