class PainlessScripts:
    def update_by_query(self, id, doc):
        return {
            "script": {
                "source": r'''
                for (entry in params.doc.entrySet()) { 
                    ctx._source[entry.getKey()] = entry.getValue() 
                }  
''',
                "lang": "painless",
                "params": {
                    "doc": doc
                }
            },
            "query": {
                "term": {
                    "id": id
                }
            }
        }
