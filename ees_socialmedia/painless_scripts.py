class PainlessScripts:
    def update(self, id):
        return {
            "script": {
                "source": "ctx._source.count++",
                "lang": "painless"
            },
            "query": {
                "term": {
                    "id": id
                }
            }
        }
