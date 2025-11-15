"""
Script para configurar containers no Azure Blob Storage.
Execute este script antes de usar o Blob Trigger pela primeira vez.
"""

from azure.storage.blob import BlobServiceClient
import os
import sys
import json

# Tentar obter connection string do local.settings.json primeiro
CONNECTION_STRING = None

try:
    with open('local.settings.json', 'r') as f:
        settings = json.load(f)
        CONNECTION_STRING = settings.get('Values', {}).get('AzureWebJobsStorage')
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível ler local.settings.json: {e}")

# Fallback para variável de ambiente
if not CONNECTION_STRING:
    CONNECTION_STRING = os.environ.get("AzureWebJobsStorage")

if not CONNECTION_STRING:
    print("❌ ERRO: AzureWebJobsStorage não encontrado!")
    print("💡 Configure a variável de ambiente ou edite local.settings.json")
    sys.exit(1)

def setup_containers():
    """Cria os containers necessários no Blob Storage."""
    
    print("🔧 Configurando containers no Azure Blob Storage...")
    print(f"📦 Storage Account: stiaeadprdbrs001")
    
    try:
        # Conectar ao Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        
        # Containers necessários
        containers = [
            {
                "name": "documentos",
                "description": "Container principal para documentos"
            }
        ]
        
        for container_info in containers:
            container_name = container_info["name"]
            
            try:
                # Verificar se container existe
                container_client = blob_service_client.get_container_client(container_name)
                
                if container_client.exists():
                    print(f"✅ Container '{container_name}' já existe")
                else:
                    # Criar container
                    blob_service_client.create_container(container_name)
                    print(f"✅ Container '{container_name}' criado com sucesso")
                
            except Exception as e:
                print(f"⚠️ Erro ao verificar/criar container '{container_name}': {e}")
        
        # Verificar estrutura de pastas virtuais
        print("\n📂 Estrutura esperada:")
        print("  documentos/")
        print("  ├── input/    (faça upload aqui)")
        print("  └── output/   (documentos corrigidos aparecem aqui)")
        
        print("\n✅ Configuração concluída!")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Faça upload de um documento .docx para: documentos/input/")
        print("2. Execute: func start")
        print("3. A função processará automaticamente e salvará em: documentos/output/")
        
        # Listar containers existentes
        print("\n📋 Containers existentes:")
        containers = blob_service_client.list_containers()
        for container in containers:
            print(f"  - {container.name}")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao Blob Storage: {e}")
        print("\n💡 Verifique:")
        print("  - Connection string está correta no local.settings.json")
        print("  - Storage Account está acessível")
        print("  - Você tem permissões adequadas")
        sys.exit(1)


def test_blob_trigger():
    """Testa se o blob trigger está configurado corretamente."""
    
    print("\n🧪 Testando configuração do Blob Trigger...")
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        
        # Verificar se pode listar blobs no container
        container_client = blob_service_client.get_container_client("documentos")
        
        print("✅ Conexão com Blob Storage OK")
        
        # Listar arquivos em input/
        print("\n📁 Arquivos em documentos/input/:")
        blobs = container_client.list_blobs(name_starts_with="input/")
        blob_count = 0
        for blob in blobs:
            print(f"  - {blob.name} ({blob.size} bytes)")
            blob_count += 1
        
        if blob_count == 0:
            print("  (vazio - faça upload de um .docx para testar)")
        
        # Listar arquivos em output/
        print("\n📁 Arquivos em documentos/output/:")
        blobs = container_client.list_blobs(name_starts_with="output/")
        blob_count = 0
        for blob in blobs:
            print(f"  - {blob.name} ({blob.size} bytes)")
            blob_count += 1
        
        if blob_count == 0:
            print("  (vazio - documentos processados aparecem aqui)")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurar Blob Storage para a Azure Function')
    parser.add_argument('--test', action='store_true', help='Testar configuração existente')
    
    args = parser.parse_args()
    
    if args.test:
        test_blob_trigger()
    else:
        setup_containers()
        test_blob_trigger()
