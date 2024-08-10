FROM jupyter/datascience-notebook:latest

# Installer des packages supplémentaires si nécessaire
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Exposer le port 8888 pour Jupyter
EXPOSE 8888
