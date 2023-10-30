import os
import sys
from io import BytesIO

import numpy as np
import torch
import torchaudio
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch_text.service.search import SearchService
from embedding_generator.usecase.engine import GeneratorEngine
from fastapi import (Depends, FastAPI, File, HTTPException, Security,
                     UploadFile, status)
from fastapi.security.api_key import APIKeyHeader
from speech_to_text.usecase.engine import SpeechToTextEngine

sys.path.append("/app")
load_dotenv()
API_KEY = os.environ["FASTAPI_AUTENTICATION"]
ELASTICSEARCH_INDEXNAME = os.environ["ELASTICSEARCH_INDEXNAME"]
ELASTICSEARCH_CLIENT = os.environ["ELASTICSEARCH_CLIENT"]
api_key_header = APIKeyHeader(name="header-key", auto_error=False)


def api_key_auth(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )
    else:
        return api_key


app = FastAPI()

client = Elasticsearch("http://es-container:9200")
es_client = SearchService(client=client)
es_client.create_index(index_name=ELASTICSEARCH_INDEXNAME)

embedding_generator_engine = GeneratorEngine(
    model_path="./embedding_generator_model/model",
    tokenizer_path="./embedding_generator_model/tokenizer",
)
speech_to_text_engine = SpeechToTextEngine(
    model_path="./speech_to_text_model/model",
    preprocess_path="./speech_to_text_model/preprocess",
)


@app.get("/")
async def healthcheck():
    return {"message": "Hello from speech-to-text api"}


@app.post("/generate")
async def image_response(
    audio_file: UploadFile = File(...), keys=Depends(api_key_auth)
):
    audio_file_types = ("flac", "mp3", "wav")
    if not audio_file.content_type.endswith(audio_file_types):
        raise HTTPException(
            status_code=400,
            detail="your input must have be audio file. (.flac, .mp3, .wav)",
        )
    try:
        contents = await audio_file.read()
        wave_tensor, sample_rate = torchaudio.load(BytesIO(contents))
        speechs = speech_to_text_engine.get_text_from_speech(wave_tensor, 16000)
        for speech in speechs:
            try:
                vector_query = embedding_generator_engine.get_embedding_from_sentence(
                    speech
                ).tolist()[0]
            except:
                return HTTPException(
                    status_code=500,
                    detail="cannot convert sentence to embedding",
                )

            try:
                es_client.bulk(
                    index_name=ELASTICSEARCH_INDEXNAME,
                    sentence_query=speech,
                    vector_query=vector_query,
                )
            except:
                return HTTPException(
                    status_code=500,
                    detail="cannot add new sentence to elasticsearch",
                )
            try:  # retrun semantic response
                return es_client.get_response_from_vector_field(
                    index_name=ELASTICSEARCH_INDEXNAME,
                    vector_query=vector_query,
                )
            except:
                return HTTPException(
                    status_code=500,
                    detail="cannot return semantic response",
                )
    except Exception as e:
        return HTTPException(status_code=500, detail=f"{e}")
