from dynaconf import Dynaconf

settings = Dynaconf(envvar_prefix="MS",
    settings_files=['settings.toml', '../settings.toml']
)
