import requests
import json
import time
from pathlib import Path

API_KEY = "SUA_CHAVE_DE_API_AQUI"
URL_GERACAO = "https://cloud.leonardo.ai/api/rest/v1/generations"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

payload = {
    "prompt": "um filhote de cachorro da raça golden retriever, feliz, sentado na grama, arte digital, colorido",
    "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3", 
    "width": 1024,
    "height": 1024,
    "num_images": 1,           
    "guidance_scale": 7,       
    "alchemy": False,        
    "photoReal": False,        
    "promptMagic": False,      
    "nsfw": False,             
    "presetStyle": "LEONARDO"  
}

print("Enviando requisição para a API do Leonardo.Ai com configuração econômica...")

def run():
    try:
        response = requests.post(URL_GERACAO, headers=headers, json=payload)
        response.raise_for_status() 

        response_data = response.json()
        generation_id = response_data['sdGenerationJob']['generationId']
        
        print(f"Requisição enviada com sucesso! ID da Geração: {generation_id}")
        print("Aguardando a imagem ser gerada...")

        url_resultado = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        
        imagem_gerada_url = None
        custo_em_tokens = None
        
        for i in range(20):
            time.sleep(3)
            response_final = requests.get(url_resultado, headers=headers)
            response_final_data = response_final.json()
            
            status = response_final_data['generations_by_pk']['status']
            print(f"Tentativa {i+1}: Status atual -> {status}")

            if status == 'COMPLETE':
                imagem_gerada_url = response_final_data['generations_by_pk']['generated_images'][0]['url']
                custo_em_tokens = response_final_data['generations_by_pk']['apiCreditCost']
                break
            elif status == 'FAILED':
                print("A geração falhou.")
                break

        if imagem_gerada_url:
            print("\n--- SUCESSO! ---")
            print(f"Custo da Geração: {custo_em_tokens} tokens")
            print(f"URL da Imagem Gerada: {imagem_gerada_url}")

            print("\nIniciando o download da imagem...")
            imagem_response = requests.get(imagem_gerada_url)
            imagem_response.raise_for_status()
            pasta_destino = Path("storage/images")
            caminho_arquivo = pasta_destino / "imagem1.png"

            pasta_destino.mkdir(parents=True, exist_ok=True)
            
            with open(caminho_arquivo, 'wb') as f:
                f.write(imagem_response.content)
                
            print(f"Imagem salva com sucesso em: '{caminho_arquivo}'")

        else:
            print("\n--- FALHA ---")
            print("Não foi possível obter a imagem gerada após várias tentativas.")


    except requests.exceptions.HTTPError as err:
        print(f"\nErro de HTTP: {err}")
        print(f"Corpo da Resposta: {err.response.text}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
