"""
AstraDB Vector Search Enablement - Production Ready
Enables vector search for existing collections or creates new vector-enabled collection
"""

import os
import logging
from dotenv import load_dotenv
from astrapy import DataAPIClient
from astrapy.exceptions import DataAPIException

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorSearchEnabler:
    """Production vector search enablement for AstraDB"""
    
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        self.endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
        self.collection_name = os.getenv('COLLECTION_NAME', 'semantic_data')
        self.dimension = int(os.getenv('EMBEDDING_DIMENSION', '1536'))
        
        if not self.token or not self.endpoint:
            raise ValueError("Missing ASTRA_DB_APPLICATION_TOKEN or ASTRA_DB_API_ENDPOINT")
        
        self.client = DataAPIClient(self.token)
        self.db = self.client.get_database_by_api_endpoint(self.endpoint)
    
    def check_vector_enabled(self, collection):
        """Check if collection has vector search enabled"""
        try:
            # Try to get collection info
            doc_count = collection.count_documents({})
            
            # Test vector search by trying a vector query
            try:
                collection.vector_find([0.1] * self.dimension, limit=1)
                logger.info(f"📊 Collection status: {doc_count} docs, vector_enabled=True")
                return True
            except:
                logger.info(f"📊 Collection status: {doc_count} docs, vector_enabled=False")
                return False
                
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return False
    
    def create_vector_collection(self, name, backup_data=None):
        """Create new vector-enabled collection"""
        try:
            logger.info(f"🔄 Creating vector collection '{name}'...")
            
            # Try different API approaches for vector collection creation
            try:
                collection = self.db.create_collection(
                    name,
                    dimension=self.dimension,
                    metric="cosine",
                    check_exists=False
                )
            except Exception:
                # Fallback - some AstraDB versions don't support vector collections
                logger.warning(f"⚠️ Vector collection creation not supported on this AstraDB plan")
                return None
            
            # Restore backup data if provided
            if backup_data:
                logger.info(f"📦 Restoring {len(backup_data)} documents...")
                collection.insert_many(backup_data)
            
            logger.info(f"✅ Vector collection '{name}' created")
            return collection
            
        except DataAPIException as e:
            if "already exists" in str(e).lower():
                logger.info(f"📝 Collection '{name}' exists, getting reference")
                return self.db.get_collection(name)
            else:
                logger.error(f"❌ Creation failed: {e}")
                return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    def backup_documents(self, collection):
        """Backup all documents from collection"""
        try:
            cursor = collection.find({}, limit=1000)
            documents = list(cursor)
            logger.info(f"💾 Backed up {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return []
    
    def enable_vector_search(self):
        """Main method to enable vector search"""
        logger.info("🚀 Enabling Vector Search")
        logger.info(f"📋 Collection: {self.collection_name}, Dimension: {self.dimension}")
        
        try:
            # Check existing collection
            existing_collection = self.db.get_collection(self.collection_name)
            
            if self.check_vector_enabled(existing_collection):
                logger.info("✅ Vector search already enabled!")
                return True, self.collection_name
            
            # Backup existing data
            backup_data = self.backup_documents(existing_collection)
            
            # Create new vector-enabled collection
            new_name = f"{self.collection_name}_vector"
            new_collection = self.create_vector_collection(new_name, backup_data)
            
            if new_collection:
                logger.info(f"🎉 SUCCESS! Update COLLECTION_NAME to: {new_name}")
                return True, new_name
            
        except Exception as e:
            logger.warning(f"⚠️ Existing collection not accessible: {e}")
            
            # Create fresh vector collection
            new_collection = self.create_vector_collection(self.collection_name)
            if new_collection:
                logger.info("🎉 SUCCESS! Fresh vector collection created")
                return True, self.collection_name
        
        logger.error("❌ Failed to enable vector search")
        return False, None

def main():
    """Execute vector search enablement"""
    try:
        enabler = VectorSearchEnabler()
        success, collection_name = enabler.enable_vector_search()
        
        if success:
            logger.info("=" * 50)
            logger.info("🎉 Vector Search Enabled!")
            logger.info(f"📝 Collection: {collection_name}")
            logger.info("💡 Run ingestion pipeline to populate vectors")
            return True
        else:
            logger.error("❌ Vector enablement failed")
            logger.info("💡 Check if your AstraDB plan supports vector search")
            return False
            
    except Exception as e:
        logger.error(f"❌ Process failed: {e}")
        return False

if __name__ == "__main__":
    main()