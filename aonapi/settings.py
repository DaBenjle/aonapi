from environs import env

env.read_env()

database_url = env("DATABASE_URL", "sqlite:///db.sqlite3")
debug = env.bool("DEBUG", False)

# URLs - Don't define them in env unless you want to override the defaults
aon_protocol = env("AON_PROTOCOL", "https")
aon_base_url = env("AON_URL", "aonprd.com")
elastic_search_prefix = env("ELASTIC_SEARCH_PREFIX", "elasticsearch")
search_url = f"{aon_protocol}://{elastic_search_prefix}.{aon_base_url}"
index_path = f'{search_url}/{env("AON_INDEX_PATH", "/json-data/aon52-index.json")}'
