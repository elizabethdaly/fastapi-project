FROM python:3.9.7

# tell docker where the working directory is
WORKDIR /usr/src/app

# copy req file into the workdir
COPY requirements.txt ./

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy everything from local dir into workdir (current dir)
COPY . .

# cmd to run the app, any space => use ""
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
