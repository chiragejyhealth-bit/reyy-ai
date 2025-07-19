# Perplexity API Client with Podcast Generation

A production-ready Python client for the Perplexity API with AWS integration for storing responses in S3 and DynamoDB, plus podcast generation capabilities using Podcastfy and intelligent configuration generation with Gemini.

## Features

- Fetch data from Perplexity API with Cloudflare bypass
- Save responses to local JSON files
- Upload audio files to Amazon S3
- Store structured data in Amazon DynamoDB
- Generate AI podcasts from Perplexity data using Podcastfy
- Create intelligent podcast configurations using Gemini API
- Customize podcast generation with various parameters
- Create and use Jinja templates for podcast configuration
- Environment-based configuration
- Clean architecture with separation of concerns:
  - Client layer for API communication
  - Service layer for business logic
  - Dependency injection for better testability
- Asynchronous operations with aioboto3
- FastAPI endpoints for all services

## Podcast Generation

The application can generate AI podcasts from Perplexity data stored in DynamoDB. The podcast generation service:

- Retrieves Perplexity data from DynamoDB
- Extracts URLs from the data
- Automatically generates conversation configurations based on content themes
- Allows custom configuration of podcast parameters
- Supports multiple TTS models (Gemini, Gemini Multi-Speaker, OpenAI, ElevenLabs, Edge TTS)
- Returns audio files that can be served via API

### Intelligent Podcast Configuration

The application uses Google's Gemini API to generate intelligent podcast configurations:

- Analyzes topics and content to create tailored podcast settings
- Uses Jinja templates for prompt engineering
- Allows custom templates to be created and saved
- Falls back to rule-based configuration if Gemini is unavailable
- Validates and fixes configurations to ensure they work with Podcastfy

### Podcast Configuration Options

You can customize your podcasts with these parameters:

| Parameter             | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| conversation_style    | Styles to apply to the conversation (e.g., "engaging", "fast-paced") |
| roles_person1         | Role of the first speaker                                            |
| roles_person2         | Role of the second speaker                                           |
| dialogue_structure    | Structure of the dialogue (e.g., "Introduction", "Main Content")     |
| podcast_name          | Name of the podcast                                                  |
| podcast_tagline       | Tagline for the podcast                                              |
| output_language       | Language of the output                                               |
| engagement_techniques | Techniques to engage the audience                                    |
| creativity            | Level of creativity (0-1)                                            |
| user_instructions     | Custom instructions to guide the conversation                        |
| word_count            | Target word count for the podcast                                    |

## API Endpoints

- `GET /`: Check if API is running
- `POST /process`: Process Perplexity data and store in AWS
- `POST /generate-podcast`: Generate a podcast from Perplexity data
- `POST /generate-podcast-config`: Generate a podcast configuration using Gemini
- `POST /save-template`: Save a Jinja template for podcast configuration
- `GET /templates/{template_name}`: Get a saved template
- `GET /podcast/{filename}`: Get a generated podcast file

## Environment Variables

```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=perplexity-audio
S3_AUDIO_PREFIX=perplexity_audio/

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=perplexity_data
DYNAMODB_READ_CAPACITY_UNITS=5
DYNAMODB_WRITE_CAPACITY_UNITS=5

# Perplexity API Configuration
PERPLEXITY_DEFAULT_LIMIT=20
PERPLEXITY_API_VERSION=2.18
PERPLEXITY_DEFAULT_TOPIC=top
PERPLEXITY_DEFAULT_SOURCE=default
PERPLEXITY_JSON_OUTPUT_PATH=response/perplexity_response.json

# Podcast Configuration
PODCAST_DEFAULT_TTS_MODEL=gemini
PODCAST_DEFAULT_WORD_COUNT=1000
PODCAST_DEFAULT_CREATIVITY=0.8
PODCAST_DEFAULT_NAME=Perplexity Insights
PODCAST_DEFAULT_LANGUAGE=English

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_DEFAULT_MODEL=gemini-1.5-pro
GEMINI_DEFAULT_TEMPERATURE=0.7
GEMINI_DEFAULT_MAX_TOKENS=1024
```

## Usage

### Running the API

```bash
python api.py
```

### Testing Podcast Generation

```bash
python test_podcast.py
```

### Testing Podcast Configuration Generation

```bash
python test_podcast_config.py
```

## Creating Custom Templates

You can create custom Jinja templates for podcast configuration. Templates use the Jinja2 syntax and have access to these variables:

- `topics`: List of topics for the podcast
- `urls`: Boolean indicating if URLs are provided
- `url_list`: List of URLs for the podcast
- `audience`: Target audience for the podcast
- `tone`: Desired tone for the podcast
- `additional_instructions`: Additional instructions for the configuration

Example template:

````jinja
You are an expert podcast producer tasked with creating a configuration for an AI-generated podcast.

# CONTEXT
The podcast will be about the following topics:
{% if topics %}
{% for topic in topics %}
- {{ topic }}
{% endfor %}
{% else %}
- General news and information
{% endif %}

# TASK
Create a detailed podcast configuration in JSON format.

# REQUIRED OUTPUT FORMAT
```json
{
  "conversation_style": ["style1", "style2", "style3"],
  "roles_person1": "specific role description",
  "roles_person2": "specific role description",
  "dialogue_structure": ["section1", "section2", "section3", "section4"],
  "podcast_name": "Catchy Name",
  "podcast_tagline": "Memorable tagline",
  "output_language": "English",
  "user_instructions": "Specific instructions for the conversation",
  "engagement_techniques": ["technique1", "technique2", "technique3", "technique4"],
  "creativity": 0.7,
  "word_count": 1000
}
````

```

```
