# Speech-to-text recognition API

API for speech to text task by using `fastapi` as upload and convert speech audio file send to `elasticsearch` for finding sentences that similar to your uploaded speech audio and send similar sentence back to `fastapi`

## requirements
1) dependencies installation
```bash
pip install -r requirements.txt
```
2) init models to model path
- `speech_to_text_model`
- `embedding_generator_model`

## Run locally
1) rename `.env.template` to `.env` and copy credentials to `.env`
```
FASTAPI_AUTENTICATION=1234
ELASTICSEARCH_INDEXNAME=text_vector
ELASTICSEARCH_CLIENT=http://es-container:9200
```
2) run docker-compose
```
docker compose up --force-recreate --build
```
2) after services up you can found services via this

   **fastapi**
   - health check: http://localhost:8000/
   - api docs: http://localhost:8000/docs

   **elasticsearch**
   - health check: http://localhost:9200/


## API Usage

1) finding similar sentence from uploaded speech audio file
- endpoint\
http://localhost:8000/generate

- variable\
  `audio_file [flac, mp3, wav]`: upload speech audio file to find similar sentence

- return value: List[Dict[text:str, score:float]]
  
- how to call 
    
    via curl
    ```bash
    curl -X 'POST' \
  'http://localhost:8000/generate' \
  -H 'accept: application/json' \
  -H 'header-key: {FASTAPI_AUTENTICATION}' \
  -H 'Content-Type: multipart/form-data' \
  -F 'audio_file=@{PATH_TO_YOUR_AUDIO_FILE};type=audio/{YOUR_AUDIO_TYPE}'
    ```
    example:\
    if you want to call `harvard.wav`, its `audio_type` = wav and your `FASTAPI_AUTENTICATION` = 1234
    ```bash
    curl -X 'POST' \
  'http://localhost:8000/generate' \
  -H 'accept: application/json' \
  -H 'header-key: 1234' \
  -H 'Content-Type: multipart/form-data' \
  -F 'audio_file=@harvard.wav;type=audio/wav'
    ```

    via python
    ```python
    import requests
    url = 'http://localhost:8000/generate'
    headers = {
        'accept': 'application/json',
        'header-key': {FASTAPI_AUTENTICATION}
    }
    files = {
        'audio_file': ({AUDIO_NAME}, open(AUDIO_PATH, 'rb'), f'audio/{AUDIO_TYPE}')
    }

    response = requests.post(url, headers=headers, files=files)
    ```
    example:\
    if you want to call `harvard.wav`, its `audio_type` = wav, its `audio_name` is hardvard and your `FASTAPI_AUTENTICATION` = 1234

    ```python
    import requests

    url = 'http://localhost:8000/generate'
    headers = {
        'accept': 'application/json',
        'header-key': '1234'
    }
    files = {
        'audio_file': ('harvard.wav', open('harvard.wav', 'rb'), 'audio/wav')
    }

    response = requests.post(url, headers=headers, files=files)
    ```
  
